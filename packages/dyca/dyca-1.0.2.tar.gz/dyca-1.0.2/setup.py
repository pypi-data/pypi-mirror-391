from setuptools import setup, find_packages

setup(
    name='dyca',
    version='1.0.2',
    description='Dynamical Component Analysis - A method to decompose multivariate signals',
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    url='https://github.com/HS-Ansbach-CCS/dyca',
    author='Annika Stiehl',
    author_email='annika.stiehl@hs-ansbach.de',
    license='GPL-3.0',
    install_requires=['numpy>=1.18.0,<2.0.0',
                      'matplotlib',
                      'scipy>=1.13.0'],
    python_requires='>=3.10',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    extras_require={
        "dev": ["twine>=4.0.2"],
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics'
    ],

)
