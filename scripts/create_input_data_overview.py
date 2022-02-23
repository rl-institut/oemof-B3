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
DECIMALS = {
    "Capacity cost": 0,
    "Fix OM cost": 0,
    "Lifetime": 0,
    "Efficiency": 2,
}
VAR_NAMES = {
    "Capacity cost": ["capacity_cost_overnight", "storage_capacity_cost_overnight"],
    "Fix OM cost": ["fixom_cost", "storage_fixom_cost"],
    "Lifetime": ["lifetime"],
    "Efficiency": ["efficiency"],
}

if __name__ == "__main__":
    in_path = sys.argv[1]  # input data
    out_path = sys.argv[2]

    df = load_b3_scalars(in_path)

    # filter for data within the scenario defined above
    df = df.loc[df["scenario_key"] == SCENARIO]

    # filter for the variables defined above
    variables = [item for sublist in VAR_NAMES.values() for item in sublist]
    df = df.loc[df["var_name"].isin(variables)]

    # Raise error if DataFrame is empty
    if df.empty:
        raise ValueError(
            f"No data in {in_path} for scenario {SCENARIO} and variables {variables}."
        )

    # unstack
    df = df.set_index(INDEX).unstack("var_name")

    # bring table into correct end format
    df = df.loc[:, ["var_value", "var_unit", "reference"]]

    # save units
    idx = pd.IndexSlice
    combined = []
    for name, group in VAR_NAMES.items():
        values = df.loc[:, idx["var_value", group]]
        values = values.stack()

        units = df.loc[:, idx["var_unit", group]]
        units = units.stack()

        result = pd.concat([values, units], 1)
        result.columns = [name, name + "_unit"]

        result.index = result.index.remove_unused_levels()

        n_levels = list(range(len(result.index.levels[2])))

        result.index = result.index.set_levels(n_levels, level=2)

        combined.append(result)

    df = pd.concat(combined, 1)

    df.index = df.index.droplevel(2)

    # map names
    df["Technology"] = df.index.map(lambda x: "-".join(x))
    df.loc[:, "Technology"].replace(labels_dict, inplace=True)
    df.set_index("Technology", inplace=True, drop=True)
    df = df.sort_index()

    def round_setting_int(df, decimals):
        r"""
        Rounds the columns of a DataFrame to the specified decimals. For zero decimals,
        it changes the dtype to Int64. Tolerates NaNs.
        """
        _df = df.copy()

        for col, dec in decimals.items():
            if dec == 0:
                dtype = "Int64"
            else:
                dtype = float

            _df[col] = pd.to_numeric(_df[col], errors="coerce").round(dec).astype(dtype)

        return _df

    df = round_setting_int(df, DECIMALS)

    # save
    df.to_csv(out_path)
