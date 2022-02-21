# coding: utf-8
r"""
Inputs
------
in_path : str
    ``results/{scenario}/postprocessed/scalars.csv``: path to scalar results.
out_path : str
    ``results/{scenario}/tables/``: target path for results tables.

Outputs
-------
.csv
    Tables showing results.

Description
-----------
"""
import os
import sys

import pandas as pd

import oemof_b3.tools.data_processing as dp

if __name__ == "__main__":
    in_path = sys.argv[1]  # input data
    out_path = sys.argv[2]
    scalars = pd.read_csv(in_path)

    def create_production_table(scalars, carrier):
        VAR_NAMES = [
            "capacity",
            f"flow_out_{carrier}",
            "storage_capacity",
            "invest",
            "loss",
        ]

        df = scalars.copy()

        # df = dp.aggregate_scalars(df, "region")

        df = dp.filter_df(df, "var_name", VAR_NAMES)

        df = dp.unstack_var_name(df).loc[:, "var_value"]

        df = df.loc[~df[f"flow_out_{carrier}"].isna()]

        df.index = df.index.droplevel(["name", "scenario", "type"])

        df["FLH"] = df[f"flow_out_{carrier}"] / (df["capacity"] + df["invest"])

        return df

    def create_demand_table(scalars):
        df = scalars.copy()

        var_name = "flow_in_"

        # df = dp.aggregate_scalars(df, "region")

        df = df.loc[df["var_name"].str.contains(var_name)]

        df = dp.filter_df(df, "type", ["excess", "load"])

        df = df.set_index(["region", "carrier", "tech"])

        df = df.loc[:, ["var_name", "var_value"]]

        return df

    df = create_production_table(scalars, "electricity")
    df.to_csv(os.path.join(out_path, "production_table.csv"))

    df = create_demand_table(scalars)
    df.to_csv(os.path.join(out_path, "sink_table.csv"))
