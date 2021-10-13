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
import pandas as pd
import sys

from oemof.tools.economics import annuity

import oemof_b3.tools.data_processing as dp
from oemof_b3.tools.data_processing import (
    load_b3_scalars,
    format_header,
    HEADER_B3_SCAL,
)


def is_correct_header(df):
    return True


def unstack_var_name(df):
    r"""
    Given a DataFrame in oemof_b3 scalars format, this function will unstack
    the variables. The returned DataFrame will have one column for each var_name.

    Parameters
    ----------
    df : pd.DataFrame
        Stacked scalar data.
    Returns
    -------
    unstacked : pd.DataFrame
        Unstacked scalar data.
    """
    assert is_correct_header(df)

    _df = df.copy()

    _df = _df.set_index(
        ["scenario", "name", "region", "carrier", "tech", "type", "var_name"]
    )

    unstacked = _df.unstack("var_name")

    return unstacked


def stack_var_name(df):
    r"""
    Given a DataFrame, this function will stack the variables.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with one column per variable

    Returns
    -------
    stacked : pd.DataFrame
        DataFrame with a column "var_name" and "var_value"
    """
    assert isinstance(df, pd.DataFrame)

    _df = df.copy()

    _df.columns.name = "var_name"

    stacked = _df.stack("var_name")

    stacked.name = "var_value"

    stacked = pd.DataFrame(stacked).reset_index()

    return stacked


class ScalarProcessor:
    def __init__(self, scalars):
        self.scalars = scalars

    def get_unstacked_var(self, var_name):

        _df = dp.filter_df(self.scalars, "var_name", var_name)

        if _df.empty:
            raise ValueError(f"No entries for {var_name} in df.")

        _df = unstack_var_name(_df)

        _df = _df.loc[:, "var_value"]

        return _df

    def append(self, var_name, data):

        _df = data.copy()

        if isinstance(_df, pd.Series):
            _df.name = var_name

            _df = pd.DataFrame(_df)

        _df = stack_var_name(_df)

        _df = format_header(_df, HEADER_B3_SCAL, "id_scal")

        self.scalars = self.scalars.append(_df)


if __name__ == "__main__":
    in_path = sys.argv[1]  # path to raw scalar data
    out_path = sys.argv[2]  # path to destination

    df = load_b3_scalars(in_path)

    sc = ScalarProcessor(df)

    invest_data = sc.get_unstacked_var(["overnight_cost", "lifetime"])

    wacc = sc.get_unstacked_var("wacc").iloc[0, 0]

    assert isinstance(wacc, float)

    invest_data["wacc"] = wacc

    annuised_investment_cost = invest_data.apply(
        lambda x: annuity(x["overnight_cost"], x["lifetime"], x["wacc"]), 1
    )

    sc.append("annuity", annuised_investment_cost)

    sc.scalars.to_csv(out_path, index=False)
