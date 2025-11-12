from setuptools import setup, find_packages
from os import path
import pathlib

working_directory = pathlib.Path(__file__).parent

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sgwr',
    version='0.4',
    url='https://github.com/Lessani252/FastSGWR',
    author='M. Naser Lessani (GIBD)',
    author_email='naserlessani252@gmail.com',
    license='MIT',
    description='Python implementation of SGWR and Fast SGWR (MPI-enhanced)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(include=['sgwr', 'sgwr.*']),
    include_package_data=True,
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn',
        'click',
        'mpi4py',
        'scipy',
        'spglm',
        'matplotlib'
    ],
    python_requires='>=3.7',

    entry_points={
        'console_scripts': [
            'fastsgwr=sgwr.fastsgwr.__main__:main',
        ]
    },
)
