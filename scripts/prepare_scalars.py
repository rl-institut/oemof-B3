# coding: utf-8
r"""
Inputs
-------
in_path1 : str
    path of input file with raw scalar data as .csv
out_path : str
    path of output file with prepared scalar data as .csv

Outputs
---------
pandas.DataFrame
    with scalar data prepared for parametrization

Description
-------------
The script performs the following steps to prepare scalar data for parametrization:

* Calculate annualized investment cost from overnight cost, lifetime and wacc.
"""
import sys

from oemof.tools.economics import annuity

import oemof_b3.tools.data_processing as dp
from oemof_b3.tools.data_processing import load_b3_scalars


def unstack_var_name(df):
    # TODO: to dataprocessing
    _df = df.copy()

    _df = _df.set_index(
        ["scenario", "name", "region", "carrier", "tech", "type", "var_name"]
    )

    _df = _df.unstack("var_name")

    return _df


def stack_var_name(df):
    # TODO: to dataprocessing

    _df = df.copy()

    _df = _df.stack("var_name")

    return _df


def filter_unstack(df, var_name):
    # TODO: to dataprocessing

    _df = df.copy()

    _df = dp.filter_df(_df, "var_name", var_name)

    _df = unstack_var_name(_df)

    _df = _df.loc[:, "var_value"]

    return _df


def prepare_annuity(df):
    _df = df.copy()

    def calculate_annuized_capacity_cost(on_cost, on1_cost):

        annuized_capacity_cost = annuity(on_cost, 2, 0.05)

        annuized_capacity_cost.columns = ["capacity_cost"]

        annuized_capacity_cost.columns.name = "var_name"

        return annuized_capacity_cost

    # filter and unstack
    on_cost = filter_unstack(_df, "overnight_cost")

    on_cost = filter_unstack(_df, "overnight_cost")

    # func
    capacity_cost = calculate_annuized_capacity_cost(on_cost, on_cost)

    # stack and append
    capacity_cost = stack_var_name(capacity_cost)

    return _df


if __name__ == "__main__":
    in_path = sys.argv[1]  # path to raw scalar data
    out_path = sys.argv[2]  # path to destination

    prepare_funcs = [
        prepare_annuity,
    ]

    df = load_b3_scalars(in_path)

    for func in prepare_funcs:
        df.append(func(df))

    df.to_csv(out_path, index=False)
