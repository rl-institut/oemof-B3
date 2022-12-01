# coding: utf-8
r"""
Inputs
-------
in_path1 : str
    ``raw/scalars/costs_efficiencies.csv``: path incl. file name of input file with raw scalar data
out_path : str
    ``results/_resources/scal_costs_efficiencies.csv``: path incl. file name of output file with
    prepared scalar data

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

from oemof_b3.tools.data_processing import B3_Scalars, save_df
from oemof_b3.config import config


def annuise_investment_cost(sc):

    for var_name_cost, var_name_fixom_cost in [
        ("capacity_cost_overnight", "fixom_cost"),
        ("storage_capacity_cost_overnight", "storage_fixom_cost"),
    ]:

        invest_data = sc.get_unstacked_var_name(
            [var_name_cost, "lifetime", var_name_fixom_cost]
        )

        # TODO: Currently, (storage)_capacity_overnight_cost, (storage)_fixom_cost and lifetime have
        # to be given for each tech and each scenario, but wacc may change per scenario, but
        # is defined for all techs uniformly. Could offer a more general and flexible solution.

        # wacc is defined per scenario, ignore other index levels
        wacc = sc.get_unstacked_var_name("wacc")
        wacc.index = wacc.index.get_level_values("scenario_key")

        # set wacc per scenario_key
        invest_data = invest_data.join(wacc, on="scenario_key")
        invest_data = invest_data["var_value"]

        annuised_investment_cost = invest_data.apply(
            lambda x: annuity(x[var_name_cost], x["lifetime"], x["wacc"])
            + x[var_name_fixom_cost],
            1,
        )

        sc = sc.append_unstacked_df(
            annuised_investment_cost, var_name_cost.replace("_overnight", "")
        )

    sc = sc.drop_var_name(
        [
            "wacc",
            "lifetime",
            "capacity_cost_overnight",
            "storage_capacity_cost_overnight",
            "fixom_cost",
            "storage_fixom_cost",
        ]
    )

    return sc


if __name__ == "__main__":
    in_path = sys.argv[1]  # path to raw scalar data
    out_path = sys.argv[2]  # path to destination

    sc = B3_Scalars.from_csv(in_path)

    sc = annuise_investment_cost(sc)

    sc.df = sc.df.sort_values(by=["carrier", "tech", "var_name", "scenario_key"])

    sc.df.reset_index(inplace=True, drop=True)

    sc.df.index.name = config.settings.general.scal_index_name

    save_df(sc.df, out_path)
