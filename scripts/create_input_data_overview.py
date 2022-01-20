# coding: utf-8
r"""
Inputs
------
in_path : str
    ``raw/{scalars}.csv``: path to raw scalars
out_path : str
    ``results/_tables/{scalars}_technical_and_cost_assumptions.csv``: target path for the table

Outputs
-------
.csv
    Table showing investment cost and efficiency data.

Description
-----------
This script creates overview tables of input data such
that it can be included in a TeX-document.
"""
import sys

import pandas as pd

from oemof_b3 import labels_dict
from oemof_b3.tools.data_processing import load_b3_scalars

SCENARIO = "Base 2050"
REGION = "ALL"
INDEX = ["carrier", "tech", "var_name"]
VAR_NAMES = {
    "capacity_cost_overnight": "Overnight cost",
    "storage_capacity_cost_overnight": "Overnight cost",
    "fixom_cost": "Fix OM cost",
    "storage_fixom_cost": "Fix OM cost",
    "lifetime": "Lifetime",
    "efficiency": "Efficiency",
}
DTYPES = {
    "capacity_cost_overnight": "Int64",  # use pandas' int to allow for NaNs
    "storage_capacity_cost_overnight": "Int64",
    "fixom_cost": "Int64",
    "storage_fixom_cost": "Int64",
    "lifetime": "Int64",
    "efficiency": float,
}
ROUND = {
    "capacity_cost_overnight": 0,
    "storage_capacity_cost_overnight": 0,
    "fixom_cost": 0,
    "storage_fixom_cost": 0,
    "lifetime": 0,
    "efficiency": 2,
}
DISPLAY_UNITS = {
    "Capacity cost": ["capacity_cost_overnight", "storage_capacity_cost_overnight"],
    "Fix OM cost": ["fixom_cost", "storage_fixom_cost"],
}

if __name__ == "__main__":
    in_path = sys.argv[1]  # input data
    out_path = sys.argv[2]

    df = load_b3_scalars(in_path)

    # filter for data within the scenario defined above
    df = df.loc[df["scenario"] == SCENARIO]

    # filter for the variables defined above
    df = df.loc[df["var_name"].isin(VAR_NAMES)]

    # Raise error if DataFrame is empty
    if df.empty:
        raise ValueError(
            f"No data in {in_path} for scenario {SCENARIO} and variables {VAR_NAMES}."
        )

    # unstack
    df = df.set_index(INDEX).unstack("var_name")

    # bring table into correct end format
    df = df.loc[:, ["var_value", "var_unit", "reference"]]

    # save units
    idx = pd.IndexSlice
    combined = []
    for name, group in DISPLAY_UNITS.items():
        values = df.loc[:, idx["var_value", group]]
        values = values.stack()

        units = df.loc[:, idx["var_unit", group]]
        units = units.stack()

        result = pd.concat([values, units], 1)
        result.columns = [name, name + "_unit"]

        combined.append(result)

    # collect those var_names that are not grouped
    rest = df.loc[:, idx["var_value", ["lifetime", "efficiency"]]]

    # Add a third level because these data are not stacked
    rest["newlevel"] = "capacity_cost_overnight"
    rest = rest.set_index("newlevel", append=True)
    rest.columns = rest.columns.droplevel(0)

    # concat the rest with the first
    combined[0] = pd.concat([combined[0], rest], 1)

    # concat all
    combined[0].index = combined[0].index.droplevel(2)
    combined[1].index = combined[1].index.droplevel(2)
    combined = pd.concat(combined, 1)

    # save
    combined.to_csv(out_path)
