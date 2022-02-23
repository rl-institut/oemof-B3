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
from oemof_b3.tools.data_processing import HEADER_B3_SCAL, format_header, sort_values, save_df

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

    _df = sort_values(_df)

    return _df


def expand_scalars(df, column, where, expand):
    _df = df.copy()

    _df_cc = _df.loc[df[column] == where].copy()

    _df_wo_cc = _df.loc[df[column] != where].copy()

    for var in expand:

        d = _df_cc.copy()

        d[column] = var

        _df_wo_cc = _df_wo_cc.append(d)

    _df_wo_cc = sort_values(_df_wo_cc)

    return _df_wo_cc


if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    destination = sys.argv[2]

    scenario_specs = load_yaml(scenario_specs)

    # setup empty EnergyDataPackage
    datetimeindex = pd.date_range(
        start=scenario_specs["datetimeindex"]["start"],
        freq=scenario_specs["datetimeindex"]["freq"],
        periods=scenario_specs["datetimeindex"]["periods"],
    )

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

    # set scenario name
    empty_scalars.loc[:, "scenario"] = scenario_specs["name"]

    # if empty raw scalars should be created, reverse the annuisation as well.
    # if empty resources scalars are needed, set this to False.
    raw_scalars = True
    if raw_scalars:
        empty_scalars = expand_scalars(
            empty_scalars,
            column="var_name",
            where="capacity_cost",
            expand=["capacity_cost_overnight", "lifetime", "fixom_cost"],
        )

        empty_scalars = expand_scalars(
            empty_scalars,
            column="var_name",
            where="storage_capacity_cost",
            expand=["storage_capacity_cost_overnight", "storage_fixom_cost"],
        )

    empty_scalars = sort_values(empty_scalars)

    save_df(empty_scalars, destination)
