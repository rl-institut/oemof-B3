#!/usr/bin/env python

from setuptools import setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='oemofB3',
    version='0.0.0',
    description='',
    long_description=read('README.md'),
    packages=['oemofB3'],
    install_requires=[
        'pandas',
        'oemof',
        'oemof.tabular',
    ],
)
