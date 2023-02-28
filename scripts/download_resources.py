# coding: utf-8
r"""
Inputs
-------
target_paths : list
    List of PosixPaths of table names from OEP to be downloaded

Description
-------------
The script downloads a list of tables from the OEP and saves them as csv.
"""

import pathlib
import sys

from oemof_b3.config import config
from oemof_b3.tools import oep

OEP_SCHEMA = "model_draft"
NAME_PREFIX = "resources"


if __name__ == "__main__":
    target_paths = [pathlib.Path(path) for path in sys.argv[1:]]

    logger = config.add_snake_logger("download_resources")

    for filepath in target_paths:

        tablename = "_".join([NAME_PREFIX, filepath.stem])

        logger.info(f"Attempting to download {tablename}")

        try:
            oep.download_table_from_OEP(filepath, tablename, OEP_SCHEMA)
        except Exception as e:
            logger.warning(
                f"Could not download resource {tablename} because of Exception: {e}"
            )
