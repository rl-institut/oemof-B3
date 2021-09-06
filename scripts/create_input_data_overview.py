# coding: utf-8
r"""
Inputs
------
in_path1

Outputs
-------
out_path

Description
-----------
This script creates overview tables of input data such
that it can be included in a TeX-document.
"""
import sys

import pandas as pd

scenario = "all"

var_names = [
    "overnight_cost",
    "lifetime",
    "FOM",
    "efficiency",
]


if __name__ == "__main__":
    in_path1 = sys.argv[1]  # input data
    out_path = sys.argv[2]

    df = pd.read_csv(in_path1)

    # filter for data within the scenario defined above
    df = df.loc[df["scenario"] == scenario]

    # filter for the variables defined above
    df = df.loc[df["var_name"].isin(var_names)]

    # keep only columns of interest
    df = df[["name", "var_name", "var_value", "var_unit", "reference"]]

    # unstack
    df = df.set_index(["name", "var_name"]).unstack("var_name")

    # bring table into correct end format
    df = df.loc[:, "var_value"]

    for var_name in var_names:
        if var_name not in df.columns:
            df[var_name] = ""

    df = df[var_names]

    # TODO: map names

    # save
    df.to_csv(out_path)
