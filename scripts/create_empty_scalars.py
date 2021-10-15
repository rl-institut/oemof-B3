# coding: utf-8
r"""
Inputs
-------
scenario_specs : str
    path of input file (.yml) containing scenario specifications
destination : str
    path of output directory

Outputs
---------
pandas.DataFrame
    Empty scalars

Description
-------------
The script creates an empty scalars that serve as a template for input data.
"""
import sys

import pandas as pd
from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.tools.helpers import load_yaml

from oemof_b3.model import bus_attrs_update, component_attrs_update
from oemof_b3.tools.data_processing import HEADER_B3_SCAL, format_header

NON_REGIONAL = [
    "capacity_cost",
    "carrier_cost",
    "efficiency",
    "expandable",
    "marginal_cost",
    "electric_efficiency",
    "thermal_efficiency",
    "condensing_efficiency",
    "loss_rate",
    "storage_capacity_cost",
]


def format_input_scalars(df):
    _df = df.copy()

    _df = format_header(_df, HEADER_B3_SCAL, "id_scal")

    # Keep only those rows whose values are not set
    _df = _df.loc[_df.loc[:, "var_value"].isna()]

    # Combine those parameters that are valid for all regions
    _df.loc[_df["var_name"].isin(NON_REGIONAL), ["name", "region"]] = [None, "ALL"]

    _df.drop_duplicates(inplace=True)

    _df = _df.reset_index(drop=True)

    _df.index.name = "id_scal"

    # set scenario name
    _df.loc[:, "scenario"] = "toy-scenario"

    _df = _df.sort_values(by=["carrier", "tech", "var_name", "scenario"])

    return _df


def expand_annuisation(df):
    _df = df.copy()

    _df_cc = _df.loc[df["var_name"] == "capacity_cost"].copy()

    _df_wo_cc = _df.loc[df["var_name"] != "capacity_cost"].copy()

    for var in ["overnight_cost", "lifetime", "fixom_cost"]:

        d = _df_cc.copy()

        d["var_name"] = var

        _df_wo_cc = _df_wo_cc.append(d)

    _df_wo_cc.reset_index(inplace=True, drop=True)

    _df_wo_cc.index.name = "id_scal"

    _df_wo_cc = _df_wo_cc.sort_values(by=["carrier", "tech", "var_name", "scenario"])

    return _df_wo_cc


if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    destination = sys.argv[2]

    scenario_specs = load_yaml(scenario_specs)

    # setup empty EnergyDataPackage
    datetimeindex = pd.date_range(start="2019-01-01", freq="H", periods=8760)

    # setup default structure
    edp = EnergyDataPackage.setup_default(
        basepath=destination,
        datetimeindex=datetimeindex,
        bus_attrs_update=bus_attrs_update,
        component_attrs_update=component_attrs_update,
        name=scenario_specs["name"],
        regions=scenario_specs["regions"],
        links=scenario_specs["links"],
        busses=scenario_specs["busses"],
        components=scenario_specs["components"],
    )

    edp.stack_components()

    components = edp.data["component"].reset_index()

    empty_scalars = format_input_scalars(components)

    empty_scalars = expand_annuisation(empty_scalars)

    empty_scalars.to_csv(destination)
