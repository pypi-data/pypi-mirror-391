import setuptools
from setuptools import setup

setup(
    name='chanter',

    version='0.0.7',

    description='Simple galaxy spectral modelling and fitting',

    long_description='CHANTER is a simple galaxy spectral energy distribution (SED) modelling/fitting code, based on the larger BAGPIPES code, of astronomical literary fame. CHANTER provides the barebones of Stellar Population Synthesis (SPS), as well as redshift and dust/IGM attenuation effects, and is written in a simple and digestible format, ideal for learning the theory behind larger spectral fitting software codes.\n Currently, I cannot include the SSP/IGM grids in the package due to PyPi size limitations, but this is being appealed.',

    author='Struan Stevenson',

    author_email='struan.stevenson@ed.ac.uk',

    packages= setuptools.find_packages(),

    package_data = {'': ['*.txt', '*.fits'],},  

    install_requires=["numpy", "astropy", "matplotlib", "spectres", "nautilus-sampler"],

)