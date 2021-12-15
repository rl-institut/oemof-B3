#!/usr/bin/env python

from setuptools import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="oemof-B3",
    version="0.0.0",
    description="",
    long_description=read("README.md"),
    packages=["oemof_b3"],
    install_requires=[
        "pandas",
        "rtree",
        "pyyaml",
        "snakemake",
        "oemoflex @ git+https://git@github.com/rl-institut/oemoflex@dev#egg=oemoflex",
        "sphinx-rtd-theme>=0.5.1",
    ],
    extras_require={
        "dev": ["pytest", "black==20.8b1", "coverage", "flake8", "geopandas"]
    },
)
