from setuptools import setup, find_packages

setup(
    name='powder_ens_commons',
    version='0.3.8',
    description='A simple data/model commons package for POWDER experiments',
    author='Mumtahin Habib',
    author_email='mumtahin.mazumder@utah.edu',
    url='https://gitlab.flux.utah.edu/mumtahin_habib/powder_ens_commons',
    packages=find_packages(),
    install_requires=[
        'rasterio==1.3.6',
        'scipy>=1.10',
        'torch>=2.0.0',
        'opencv-python==4.7.0.68',
        'shapely==2.0.1',
        'scikit-image==0.22.0',
        'pandas==2.0.2',
        'numpy>=1.24.3',
        'matplotlib==3.8.3',
        'scikit-learn==1.2.2',
        'utm==0.7.0',
        'POT==0.9.3',
        'setuptools==65.5.0',
        'sympy==1.11.1',
        'tqdm==4.66.2',
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10, <3.13',
)
