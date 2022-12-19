# coding: utf-8
r"""
Inputs
-------
paths_scenarios : list[str]
    A list of scenario paths.
destination : path
    ``results/joined_scenarios/{scenario_list}/joined/scalars.csv``: Path of output file to store
    joined scalar results.

Outputs
---------
.csv-file
    File containing the joined scalar results of the scenarios.

Description
-------------
This script joins scalar results of a group of scenarios.
"""
import os
import sys

import pandas as pd

from oemof_b3.config import config


def load_scalars(path):
    scalars = pd.read_csv(
        path, index_col=[0, 1, 2], sep=config.settings.general.separator
    )
    return scalars


if __name__ == "__main__":
    paths_scenarios = sys.argv[1:-1]

    destination = sys.argv[-1]

    joined_scalars = list()
    for path_sc in paths_scenarios:
        scalars = load_scalars(os.path.join(path_sc, "scalars.csv"))

        joined_scalars.append(scalars)

    joined_scalars = pd.concat(joined_scalars)

    if not os.path.exists(destination):
        os.makedirs(destination)

    joined_scalars.to_csv(
        os.path.join(destination, "scalars.csv"), sep=config.settings.general.separator
    )
