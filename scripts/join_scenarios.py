import os
import sys

import pandas as pd
from oemoflex.tools.helpers import load_yaml


def load_scalars(path):
    scalars = pd.read_csv(path, index_col=[0, 1, 2])
    return scalars


if __name__ == "__main__":
    list_scenarios = sys.argv[1]

    destination = sys.argv[2]

    scenarios = load_yaml(list_scenarios)

    joined_scalars = list()
    for scenario in scenarios:
        scalars = load_scalars(
            os.path.join("results", scenario, "postprocessed", "scalars.csv")
        )
        joined_scalars.append(scalars)

    joined_scalars = pd.concat(joined_scalars)

    joined_scalars.to_csv(destination)
