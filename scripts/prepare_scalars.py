# coding: utf-8
r"""
Inputs
-------
in_path1 : str
    path incl. file name of input file with raw scalar data as .csv
out_path : str
    path incl. file name of output file with prepared scalar data as .csv

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

import pandas as pd

from oemof.tools.economics import annuity

from oemof_b3.tools.data_processing import ScalarProcessor, load_b3_scalars


def fill_na(df):
    key = "scenario"

    value = "None"

    _df = df.copy()

    # save index and columns before resetting index
    id_names = _df.index.names

    columns = _df.columns

    _df.reset_index(inplace=True)

    # separate data where NaNs should be filled and base
    df_fill_na = _df.loc[_df[key] != value]

    base = _df.loc[_df[key] == value]

    # merge data on the columns of the data to update
    df_merged = df_fill_na.drop(columns, 1).merge(base.drop(key, 1), "left")

    # update dataframe NaNs
    df_fill_na.update(df_merged)

    # combine the filled data with the base data
    df_fill_na = pd.concat([df_fill_na, base])

    # set index as before
    df_fill_na = df_fill_na.set_index(id_names)

    return df_fill_na


if __name__ == "__main__":
    in_path = sys.argv[1]  # path to raw scalar data
    out_path = sys.argv[2]  # path to destination

    df = load_b3_scalars(in_path)

    sc = ScalarProcessor(df)

    invest_data = sc.get_unstacked_var(["overnight_cost", "lifetime"])

    # if some value is None in some scenario key, use the values from Base scenario to fill NaNs
    invest_data = fill_na(invest_data)

    wacc = sc.get_unstacked_var("wacc").iloc[0, 0]

    assert isinstance(wacc, float)

    invest_data["wacc"] = wacc

    annuised_investment_cost = invest_data.apply(
        lambda x: annuity(x["overnight_cost"], x["lifetime"], x["wacc"]), 1
    )

    sc.append("annuity", annuised_investment_cost)

    sc.scalars.to_csv(out_path, index=False)
