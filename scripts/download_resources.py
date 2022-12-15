import sys
import pathlib

from oemof_b3.tools import oep

OEP_SCHEMA = "model_draft"
NAME_PREFIX = "resources"


if __name__ == "__main__":
    target_paths = [pathlib.Path(path) for path in sys.argv[1:]]

    for filepath in target_paths:

        tablename = "_".join([NAME_PREFIX, filepath.stem])

        print(f"Attempting to download {tablename}")

        oep.download_table_from_OEP(filepath, tablename, OEP_SCHEMA)
