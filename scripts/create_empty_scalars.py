# coding: utf-8
r"""
Inputs
-------
scenario_specs : str
    ``scenarios/{scenario}.yml``: path of input file (.yml) containing scenario specifications
destination : str
    path of output directory

Outputs
---------
pandas.DataFrame
    Empty scalar in oemof-B3 resource format.

Description
-------------
The script creates an empty DataFrame for scalar data that serve as a template for input data.
"""
import sys
import os
import pandas as pd

from oemoflex.model.datapackage import EnergyDataPackage

from oemof_b3.config.config import load_yaml, settings
from oemof_b3.model import bus_attrs_update, component_attrs_update, model_structures
from oemof_b3.tools.data_processing import (
    HEADER_B3_SCAL,
    load_b3_scalars,
    format_header,
    sort_values,
    save_df,
)

NON_REGIONAL = settings.create_empty_scalars.non_regional


def get_edp_from_scenario(scenario_specs):
    model_structure = model_structures[scenario_specs["model_structure"]]

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
        regions=model_structure["regions"],
        links=model_structure["links"],
        busses=model_structure["busses"],
        components=model_structure["components"],
    )

    edp.stack_components()

    return edp


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

        _df_wo_cc = pd.concat([_df_wo_cc, d])

    _df_wo_cc = sort_values(_df_wo_cc)

    return _df_wo_cc


def add_wacc(sc):
    sc = sc.append(
        {
            "scenario_key": scenario_specs["name"],
            "var_name": "wacc",
            "carrier": "ALL",
            "region": "ALL",
            "tech": "ALL",
            "type": "ALL",
            "var_unit": "None",
        },
        ignore_index=True,
    )

    return sc


def save_empty_scalars(sc, path):

    if os.path.exists(path):
        all_sc = load_b3_scalars(path)

        if all_sc.empty:
            all_sc = sc
        else:
            all_sc = all_sc.append(sc, ignore_index=True)
            all_sc.index.name = sc.index.name

    else:
        all_sc = sc

    all_sc.drop_duplicates(inplace=True)

    save_df(all_sc, path)


if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    destination = sys.argv[2]

    scenario_specs = load_yaml(scenario_specs)

    edp = get_edp_from_scenario(scenario_specs)

    components = edp.data["component"].reset_index()

    empty_scalars = format_input_scalars(components)

    # set scenario name
    empty_scalars.loc[:, "scenario_key"] = scenario_specs["name"]

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

    empty_scalars = add_wacc(empty_scalars)

    empty_scalars = sort_values(empty_scalars)

    save_empty_scalars(empty_scalars, destination)
