#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CDICALC: calculator for coherent X-ray diffraction imaging experiments
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

from setuptools import setup, find_packages
from os import path
from io import open

from cdicalc import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cdicalc",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    # package_data={'bcdi/preprocessing': ['bcdi/preprocessing/alias_dict.txt']},
    # the file needs to be in a package
    # data_files=[('bcdi/data', ['bcdi/data/S978_LLKf000.460.cxi'])],
    # data files will be installed outside of the package, which is not ideal
    scripts=[],
    # metadata
    author="Jerome Carnis",
    author_email="carnis_jerome@yahoo.fr",
    description="""CDICALC: GUI for setup calculations in Coherent X-ray Diffraction
     Imaging experiments""",
    license="CeCILL-B",
    keywords="CDI Coherent X-rays diffraction imaging",
    long_description_content_type="text/x-rst",
    long_description="""
        GUI for setup calculations in Coherent X-ray Diffraction Imaging experiments.
        """,
    url="https://github.com/carnisj/cdicalc",
    project_urls={},
    python_requires=">=3.8*",
    install_requires=["pint", "xrayutilities", "pyqt5", "pyyaml"],
    extras_require={
        "dev": [
            "black",
            "coverage",
            "doit",
            "mypy",
            "pydocstyle",
            "pylint",
            "pytest",
            "twine",
            "wheel",
        ],
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # Pick your license as you wish
        "License :: CeCILL-B Free Software License Agreement (CECILL-B)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # These classifiers are *not* checked by 'pip install'. See instead
        # 'python_requires' below.
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
)
