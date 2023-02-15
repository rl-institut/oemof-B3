import sys
from pathlib import Path

from urllib import request
from zipfile import ZipFile


def download_from_zenodo(url, target_directory):
    request.urlretrieve(url, target_directory)


def unzip(zip_filepath, destination):
    with ZipFile(zip_filepath, 'r') as zObject:
        zObject.extractall(path=destination)


if __name__ == "__main__":
    url = sys.argv[1]
    raw = Path(sys.argv[2])
    zip_filepath = raw / "oemof-B3-raw-data.zip"

    download_from_zenodo(url, zip_filepath)

    unzip(zip_filepath, raw)
