import os

import json


def load_json_to_dict(filepath):
    with open(filepath, "rb") as f:
        return json.load(f)


here = os.path.dirname(__file__)

oemetadata_template = load_json_to_dict(os.path.join(here, "oemetadata.json"))
