import os

import json
import pandas as pd


def load_json_to_dict(filepath):
    with open(filepath, "rb") as f:
        return json.load(f)


here = os.path.dirname(__file__)

SCHEMA_SCAL = pd.read_csv(
    os.path.join(here, "scalars.csv"), index_col=0, delimiter=";"
)

SCHEMA_TS = pd.read_csv(
    os.path.join(here, "timeseries.csv"), index_col=0, delimiter=";"
)

oemetadata_template = load_json_to_dict(os.path.join(here, "oemetadata.json"))
