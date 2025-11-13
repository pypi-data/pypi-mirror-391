from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.7'
DESCRIPTION = 'Simulation of methematical models of signaling pathways of GPCRs'
LONG_DESCRIPTION = 'The SSB computational toolkit was developed to easily predict classical pharmacodynamic models of drug-GPCR (class A) interactions given just as input structural information of the receptor and the ligand.'

# Setting up
setup(
    name="ssbtoolkit",
    version=VERSION,
    author="Rui Ribeiro",
    author_email="<rui.ribeiro@univr.it>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    include_package_data = True,
    install_requires=['numpy', 'scipy', 'sympy', 'pandas', 'matplotlib','plotly==5','scikit-learn','db-sqlite3'
                      ,'seaborn','pubchempy','biopython','pysb','bionetgen','bioservices','qgrid==1.3.0','kaleido'],
    keywords=['python', 'bioinformatics', 'Systems Biology', 'GPCR'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X"
    ]
)
