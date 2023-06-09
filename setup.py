#!/usr/bin/env python

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import codecs
import os.path

import sys

# to access version
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


repo_name = "QUOP"
analysis = "prioritization"

long_description = "This package contains a quantitative universal option prioritizer (QUOP) tool."

setup(
    name=repo_name,
    version=get_version(os.path.join(analysis,"__init__.py")),
    description="Decision-making " + analysis.lower() + " tool",
    long_description=long_description,
    # The project's main homepage.
    url="https://github.com/LBNL-ETA/QUOP",
    # Author details
    author="Milica Grahovac",
    # Choose your license
    license="BSD-3-Clause-LBNL",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python :: 3.8",
    ],
    keywords="prioritization decision-making AHP choice",
    packages=find_packages(exclude=["docs"]),
    install_requires=[
        "pandas>=1.0.3",
        "numpy>=1.18.4",
        "scipy>=1.4.1",
        "seaborn>=0.10.1",
        "adapterio>=1.0.0",
        "openpyxl>=3.0.9",
    ]
    + [
        "pywin32>=225" if sys.platform.lower().startswith("win") else ""
    ],  # If OSX, tkinter is python native
)
