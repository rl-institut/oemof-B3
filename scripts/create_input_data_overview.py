# coding: utf-8
r"""
Inputs
------
in_path : str
    ``raw/raw/scalars/costs_efficiencies.csv.csv``: path to raw scalar data.
out_path : str
    ``results/_tables/technical_and_cost_assumptions_{scenario_key}.csv``: target path for
    the table.
logfile : str
    ``logs/{scenario}.log``: path to logfile

Outputs
-------
.csv
    Table showing investment cost and efficiency data for all technologies.

Description
-----------
This script creates an overview table of input data that can be included in a TeX-document.
"""
import sys

import pandas as pd

from oemof_b3 import labels_dict
import oemof_b3.tools.data_processing as dp
from oemof_b3.config import config


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
    scenario_key = sys.argv[2]
    out_path = sys.argv[3]
    logfile = sys.argv[4]

    logger = config.add_snake_logger(logfile, "create_input_data_overview")

    df = dp.load_b3_scalars(in_path)

    # filter for data within the scenario key defined above
    df = df.loc[df["scenario_key"] == scenario_key]

    # filter for the variables defined above
    variables = [item for sublist in VAR_NAMES.values() for item in sublist]
    df = df.loc[df["var_name"].isin(variables)]

    # Raise error if DataFrame is empty
    if df.empty:
        raise ValueError(
            f"No data in {in_path} for scenario {scenario_key} and variables {variables}."
        )

    # drop duplicates before unstacking
    duplicated = df[INDEX].duplicated()
    if duplicated.any():
        logger.warning(
            f"Data contains duplicates that are dropped {df.loc[duplicated][INDEX]}"
        )

    df = df.loc[~duplicated]

    # unstack
    df = df.set_index(INDEX).unstack("var_name")

    # bring table into correct end format
    df = df.loc[:, ["var_value", "var_unit", "source"]]

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

    df = dp.round_setting_int(df, DECIMALS)

    # save
    df.to_csv(out_path)
