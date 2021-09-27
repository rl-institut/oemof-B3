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

from oemof_b3.tools.data_processing import load_b3_scalars


def prepare_annuity(df):
    return df


if __name__ == "__main__":
    in_path = sys.argv[1]  # path to raw scalar data
    out_path = sys.argv[2]  # path to destination

    prepare_funcs = [
        prepare_annuity,
    ]

    df = load_b3_scalars(in_path)

    for func in prepare_funcs:
        df = func(df)

    df.to_csv(out_path, index=False)
