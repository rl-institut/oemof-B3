# coding: utf-8
r"""
Inputs
-------
list_scenarios : path
    ``scenario_groups/{scenario_list}.yml``: Path to yaml-file containing a list of scenarios.
destination : path
    ``results/joined_scenarios/{scenario_list}/joined/scalars.csv``: Path of output file to store
    joined scalar results.

Outputs
---------
.csv-file
    File containing the joined scalar results of the scenarios.

Description
-------------
This script joins scalar results of a set of scenarios.
"""
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
        scalars["scenario"] = scenario
        joined_scalars.append(scalars)

    joined_scalars = pd.concat(joined_scalars)

    joined_scalars.to_csv(destination)
