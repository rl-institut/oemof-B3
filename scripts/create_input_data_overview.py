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

from oemof_b3.tools.data_processing import load_b3_scalars

SCENARIO = "Base 2050"
REGION = "ALL"
INDEX = ["carrier", "tech", "var_name"]
VAR_NAMES = [
    "overnight_cost",
    "lifetime",
    "FOM",
    "efficiency",
]


if __name__ == "__main__":
    in_path1 = sys.argv[1]  # input data
    out_path = sys.argv[2]

    df = load_b3_scalars(in_path1)

    # filter for data within the scenario defined above
    df = df.loc[df["scenario"] == SCENARIO]

    # filter for the variables defined above
    df = df.loc[df["var_name"].isin(VAR_NAMES)]

    # Raise error if DataFrame is empty
    if df.empty:
        raise ValueError(
            f"No data in {in_path1} for scenario {SCENARIO} and variables {VAR_NAMES}."
        )

    # unstack
    df = df.set_index(INDEX).unstack("var_name")

    # bring table into correct end format
    df = df.loc[:, "var_value"]

    for var_name in VAR_NAMES:
        if var_name not in df.columns:
            df[var_name] = ""

    df = df[VAR_NAMES]

    # TODO: map names

    # save
    df.to_csv(out_path)
