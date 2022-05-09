# coding: utf-8
r"""
Inputs
------
in_path : str
    ``results/{scenario}/postprocessed/scalars.csv``: path to scalar results.
out_path : str
    ``results/{scenario}/tables/``: target path for results tables.
logfile : str
    ``logs/{scenario}.log``: path to logfile

Outputs
-------
.csv
    Tables showing results.

Description
-----------
"""
import os
import sys

import numpy as np
import pandas as pd

import oemof_b3.tools.data_processing as dp
from oemof_b3.config import config


def create_production_table(scalars, carrier):
    VAR_NAMES = [
        "capacity",
        f"invest_out_{carrier}",
        f"flow_out_{carrier}",
        "storage_capacity",
        "invest",
        "loss",
    ]

    df = scalars.copy()

    df = dp.aggregate_scalars(df, "region")

    df = dp.filter_df(df, "var_name", VAR_NAMES)

    df = dp.unstack_var_name(df).loc[:, "var_value"]

    df = df.loc[~df[f"flow_out_{carrier}"].isna()]

    df.index = df.index.droplevel(["name", "type"])

    df.loc[:, "FLH"] = df.loc[:, f"flow_out_{carrier}"] / df.loc[
        :, ["capacity", f"invest_out_{carrier}"]
    ].sum(axis=1)

    df.replace({np.inf: np.nan}, inplace=True)

    df = dp.round_setting_int(df, decimals={col: 0 for col in df.columns})

    return df


def create_demand_table(scalars):
    df = scalars.copy()

    var_name = "flow_in_"

    df = dp.aggregate_scalars(df, "region")

    df = df.loc[df["var_name"].str.contains(var_name)]

    df = dp.filter_df(df, "type", ["excess", "load"])

    df = df.set_index(["scenario_key", "region", "carrier", "tech", "var_name"])

    df = df.loc[:, ["var_value"]]

    df = dp.round_setting_int(df, decimals={col: 0 for col in df.columns})

    return df


def create_total_system_cost_table(scalars):
    df = scalars.copy()

    df = dp.filter_df(df, "var_name", "total_system_cost")

    df = df.set_index(["scenario_key", "var_name"])

    df = df.loc[:, ["var_value"]]

    df = dp.round_setting_int(df, decimals={col: 0 for col in df.columns})

    return df


if __name__ == "__main__":
    in_path = sys.argv[1]  # input data
    out_path = sys.argv[2]
    logfile = sys.argv[3]

    logger = config.add_snake_logger(logfile, "create_results_table")

    scalars = pd.read_csv(os.path.join(in_path, "scalars.csv"))

    # Workaround to conform to oemof-b3 format
    scalars.rename(columns={"scenario": "scenario_key"}, inplace=True)

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    for carrier in ["electricity", "heat_central", "heat_decentral", "h2"]:
        try:
            df = create_production_table(scalars, carrier)
            dp.save_df(df, os.path.join(out_path, f"production_table_{carrier}.csv"))
        except:  # noqa E722
            logger.info(f"Could not create production table for carrier {carrier}.")
            continue

    df = create_demand_table(scalars)
    dp.save_df(df, os.path.join(out_path, "sink_table.csv"))

    df = create_total_system_cost_table(scalars)
    dp.save_df(df, os.path.join(out_path, "total_system_cost.csv"))
