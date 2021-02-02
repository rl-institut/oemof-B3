#!/usr/bin/env python

from setuptools import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='oemof-B3',
    version='0.0.0',
    description='',
    long_description=read('README.md'),
    packages=['oemof_b3'],
    install_requires=[
        'pandas',
        'pyomo<5.6.9',
        'pyutilib<6.0.0',
        'oemof.tabular @ git+https://git@github.com/oemof/oemof-tabular@dev#egg=oemof.tabular',
    ],
)
