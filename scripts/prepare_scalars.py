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

from oemof_b3.tools.data_processing import ScalarProcessor, load_b3_scalars

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
