# coding: utf-8
r"""
Inputs
-------
url : str
    Path to raw data on zenodo
zip_filepath : str
    Path to raw directory in oemof-B3
directory : str
    Path of output directory

Description
-------------
The script downloads raw data from zenodo as a zip file and unpacks the zip file to raw directory
"""

import sys
from pathlib import Path

from urllib import request
from zipfile import ZipFile


def download_from_zenodo(url, target_directory):
    request.urlretrieve(url, target_directory)


def unzip(zip_filepath, destination):
    with ZipFile(zip_filepath, "r") as zObject:
        zObject.extractall(path=destination)


if __name__ == "__main__":
    url = sys.argv[1]
    zip_filepath = Path(sys.argv[2])
    directory = zip_filepath.parent

    download_from_zenodo(url, zip_filepath)

    unzip(zip_filepath, directory)
