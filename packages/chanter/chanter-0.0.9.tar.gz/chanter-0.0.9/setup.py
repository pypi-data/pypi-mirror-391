import setuptools
from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='chanter',

    version='0.0.9',

    description='Simple galaxy spectral modelling and fitting',

    long_description=long_description,

    long_description_content_type='text/markdown',

    author='Struan Stevenson',

    author_email='struan.stevenson@ed.ac.uk',

    packages= setuptools.find_packages(),

    package_data = {'': ['*.txt', '*.fits'],},  

    install_requires=["numpy", "astropy", "matplotlib", "spectres", "nautilus-sampler"],

)