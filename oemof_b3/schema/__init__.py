import copy
import os

import json
import pandas as pd


here = os.path.dirname(__file__)


def load_metadata_json_to_dict(filepath):
    r"""
    Mirrors the function with the same name in oeomof_b3.tools.oep to
    avoid circular import.
    """
    with open(filepath, "rb") as f:
        return json.load(f)


def write_schema_to_metadata(schema, metadata, num_resource=0):

    _metadata = copy.deepcopy(metadata)

    # save a template for the fields
    field = copy.deepcopy(metadata["resources"][num_resource]["schema"]["fields"][0])

    # allocate enough fields to fit schema in
    _metadata["resources"][num_resource]["schema"]["fields"] = [
        copy.deepcopy(field)
        for i in range(len(schema.columns.columns) + 1)  # one more for index
    ]

    # write schema to metadata
    _metadata["resources"][num_resource]["schema"]["fields"][0][
        "name"
    ] = schema.index.name
    _metadata["resources"][num_resource]["schema"]["fields"][0]["type"] = schema.index[
        "type"
    ]
    _metadata["resources"][num_resource]["schema"]["fields"][0][
        "description"
    ] = schema.index["description"]

    for i, (name, (type, description)) in enumerate(schema.columns.iteritems()):
        _metadata["resources"][num_resource]["schema"]["fields"][i + 1]["name"] = name
        _metadata["resources"][num_resource]["schema"]["fields"][i + 1]["type"] = type
        _metadata["resources"][num_resource]["schema"]["fields"][i + 1][
            "description"
        ] = description

    return _metadata


class B3Schema:
    def __init__(self, index, columns):
        self.index = index
        self.columns = columns

    @classmethod
    def load_from_csv(cls, path):
        df = pd.read_csv(path, delimiter=";")

        df.columns.name = "field"

        df.index = ["type", "description"]

        index = df.iloc[:, 0]

        columns = df.iloc[:, 1:]

        return cls(index, columns)


SCHEMA_SCAL = B3Schema.load_from_csv(os.path.join(here, "scalars.csv"))

SCHEMA_TS = B3Schema.load_from_csv(os.path.join(here, "timeseries.csv"))

oemetadata = load_metadata_json_to_dict(os.path.join(here, "oemetadata.json"))

oemetadata_scal = write_schema_to_metadata(SCHEMA_SCAL, oemetadata)

oemetadata_ts = write_schema_to_metadata(SCHEMA_TS, oemetadata)
