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

from oemof_b3.tools.data_processing import ScalarProcessor, load_b3_scalars, save_df
import oemof_b3.config.config as config


def annuise_investment_cost(sc):

    for var_name_cost, var_name_fixom_cost in [
        ("capacity_cost_overnight", "fixom_cost"),
        ("storage_capacity_cost_overnight", "storage_fixom_cost"),
    ]:

        invest_data = sc.get_unstacked_var(
            [var_name_cost, "lifetime", var_name_fixom_cost]
        )

        # TODO: Currently, (storage)_capacity_overnight_cost, (storage)_fixom_cost and lifetime have
        # to be given for each tech and each scenario, but wacc may change per scenario, but
        # is defined for all techs uniformly. Could offer a more general and flexible solution.

        # wacc is defined per scenario, ignore other index levels
        wacc = sc.get_unstacked_var("wacc")
        wacc.index = wacc.index.get_level_values("scenario_key")

        # set wacc per scenario_key
        scenario_keys = invest_data.index.get_level_values("scenario_key")
        invest_data["wacc"] = wacc.loc[scenario_keys].values

        annuised_investment_cost = invest_data.apply(
            lambda x: annuity(x[var_name_cost], x["lifetime"], x["wacc"])
            + x[var_name_fixom_cost],
            1,
        )

        sc.append(var_name_cost.replace("_overnight", ""), annuised_investment_cost)

    sc.drop(
        [
            "wacc",
            "lifetime",
            "capacity_cost_overnight",
            "storage_capacity_cost_overnight",
            "fixom_cost",
            "storage_fixom_cost",
        ]
    )


if __name__ == "__main__":
    in_path = sys.argv[1]  # path to raw scalar data
    out_path = sys.argv[2]  # path to destination

    df = load_b3_scalars(in_path)

    sc = ScalarProcessor(df)

    annuise_investment_cost(sc)

    sc.scalars = sc.scalars.sort_values(
        by=["carrier", "tech", "var_name", "scenario_key"]
    )

    sc.scalars.reset_index(inplace=True, drop=True)

    sc.scalars.index.name = config.settings.general.scal_index_name

    save_df(sc.scalars, out_path)
