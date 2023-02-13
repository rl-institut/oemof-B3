import sys
from pathlib import Path

from urllib import request


def download_from_zenodo(url, target_directory):
    request.urlretrieve(url, target_directory)


if __name__ == "__main__":
    url = sys.argv[1]
    raw = Path(sys.argv[2])

    download_from_zenodo(url, raw)
