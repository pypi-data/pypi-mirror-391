import setuptools
from setuptools import setup

setup(
    name='chanter',

    version='0.0.4',

    description='Galaxy spectral fitting',

    author='Struan Stevenson',

    author_email='struan.stevenson@ed.ac.uk',

    packages= setuptools.find_packages(),

    package_data = {'': ['*.txt', '*.fits'],},  

    install_requires=["numpy", "astropy", "matplotlib", "spectres", "nautilus-sampler"],

)