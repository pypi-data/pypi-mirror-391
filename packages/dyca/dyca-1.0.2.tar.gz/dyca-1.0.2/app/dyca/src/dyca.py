import numpy as np
from .dyca_internal import _input_check, _calculate_correlations, _calculate_eigenvalues_and_vectors, _calculate_svd, _calculate_amplitudes, _derivativesignal

def dyca(signal: np.ndarray, m: int = None, n: int = None, time_index: np.ndarray = None, derivative_signal: np.ndarray = None) -> dict:
    """ Calculate DyCA eigenvalues, DyCA singular values and DyCA amplitudes of the input signal. 
    DyCA (Dynamical Component Analysis) is a method to extract temporal amplitudes from a multivariate signal based on the assumption
    that the temporal evoltion of these amplitudes is driven by a certaim set of differential equations.
    See https://doi.org/10.1109/OJSP.2020.3038369 for detailed information.

    Arguments:
        signal {np.ndarray} -- Input signal (shape = time, channels) with full rank.
        m {int} -- Number of linear components to be used for reconstruction. If m = None, only the eigenvalues are returned.
        n {int} -- Number of differential equations to be used for the reconstruction. If n = None, only the eigenvalues and singular values are returned.
        (optional) time_index {np.ndarray} -- The corresponding array of the times for the signal (time,).
        (optional) derivative_signal {np.ndarray} -- The derivative of the signal with respect to the time array (time, channels).
        You can use this to use a better suited derivative signal than the default one, e. g. with appropriate filters.

    Returns:
        Dictionary with:
            amplitudes {np.ndarray | None} -- Amplitudes (n, time).
            generalized_eigenvalues {np.ndarray | None} -- Eigenvalues (channels,).
            singular_values {np.ndarray | None} -- Singular_values of the amplitudes (2*m,).

        The values of the returned dictionary are None if the corresponding parameter m or n are set to None.
    """
    if time_index is None:
        time_index = np.array(range(signal.shape[0]))

    if derivative_signal is None:
        derivative_signal = _derivativesignal(signal, time_index)

    # Check inputs
    try:
        _input_check(signal, m, n, time_index, derivative_signal)
    except Exception as e:
        raise ValueError(e)
    
    # compute correlation matrices
    signal_autocorrelation_inv, signal_derivate_correlation, derivate_autocorrelation = _calculate_correlations(signal, derivative_signal)

    # solve for eigenvalues, eigenvectors
    generalized_eigenvalues, eigenvectors = _calculate_eigenvalues_and_vectors(
        signal_autocorrelation_inv, signal_derivate_correlation, derivate_autocorrelation)

    # do singular value decomposition of the amplitudes corresponding to the DyCA eigenvector-matrix U and the associated matrix V
    U_svd, S_svd, V_svd = _calculate_svd(m, signal_autocorrelation_inv, signal_derivate_correlation, eigenvectors, signal)

    # project the signal along n important components
    amplitudes = _calculate_amplitudes(U_svd, S_svd, V_svd, n)

    output = {'amplitudes': amplitudes,
              'generalized_eigenvalues': generalized_eigenvalues,
              'singular_values': S_svd}

    return output

def reconstruction(signal: np.ndarray, amplitudes: np.ndarray) -> dict:
    """Find modes such that modes*amplitudes approximates signal

    Arguments:
        signal {np.ndarray} -- Input signal (time, channels).
        amplitudes {np.ndarray} -- Amplitudes (n, time).

    Returns:
        Dictionary with:
            modes {np.ndarray} -- Modes (channels, n).
            reconstruction {np.ndarray} -- Reconstructed signal (time, channels).
            cost {float} -- L2-norm of the reconstruction (relative to the signal norm).
    """
    modes = signal @ np.linalg.pinv(amplitudes)

    # reconstructed time-series
    reconstruction = modes @ amplitudes

    # cost of the reconstruction (relative L2-norm)
    cost = np.linalg.norm(reconstruction - signal) / np.linalg.norm(signal)

    output = {
        'modes': modes,
        'reconstruction': reconstruction,
        'cost': cost
    }

    return output
