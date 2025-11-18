from setuptools import setup, find_packages

setup(
    name='powder_ens_commons',
    version='0.3.11',
    description='A simple data/model commons package for POWDER experiments',
    author='Mumtahin Habib',
    author_email='mumtahin.mazumder@utah.edu',
    url='https://gitlab.flux.utah.edu/mumtahin_habib/powder_ens_commons',
    packages=find_packages(),
    install_requires=[
        'rasterio>=1.3.6, <1.5',
        'scipy>=1.11, <1.13',
        'torch>=2.4.0, <2.6',
        'opencv-python>=4.7.0.72, <4.10',
        'shapely>=2.0.1, <2.1',
        'scikit-image>=0.22.0, <0.23',
        'pandas>=2.0.2, <2.3',
        'numpy>=1.26, <2.0',
        'matplotlib>=3.8.3, <3.10',
        'scikit-learn>=1.2.2, <1.4',
        'utm>=0.7.0, <1.0',
        'POT>=0.9.3, <0.10',
        'sympy>=1.12, <1.13',
        'tqdm>=4.66.2, <4.67',
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10, <3.13',
)
