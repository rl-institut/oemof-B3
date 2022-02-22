# coding: utf-8
r"""
Inputs
-------
scenario_specs : str
    ``scenarios/{scenario}.yml``: path of input file (.yml) containing scenario specifications
destination : str
    ``results/{scenario}/preprocessed``: path of output directory

Outputs
---------
oemoflex.EnergyDatapackage
    EnergyDatapackage in the correct structure, with data (scalars and timeseries) as csv and
    metadata (describing resources and foreign key relations) as json.

Description
-------------
The script creates an empty EnergyDatapackage from the specifications given in the scenario_specs,
fills it with scalar and timeseries data, infers the metadata and saves it to the given destination.
Further, additional parameters like emission limit are saved in a separate file.
"""
import sys
import os
from collections import OrderedDict

import pandas as pd
from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.tools.helpers import load_yaml

from oemof_b3.model import bus_attrs_update, component_attrs_update, foreign_keys_update
from oemof_b3.tools.data_processing import (
    filter_df,
    load_b3_scalars,
    load_b3_timeseries,
    unstack_timeseries,
    format_header,
    HEADER_B3_SCAL,
    save_df,
)

# global variables
EL_GAS_RELATION = "electricity_gas_relation"
EMISSION_LIMIT = "emission_limit"
ADDITIONAL_SCALARS_FILE = "additional_scalars.csv"


def multi_load(paths, load_func):
    if isinstance(paths, list):
        pass
    elif isinstance(paths, str):
        return load_func(paths)
    else:
        raise ValueError(f"{paths} has to be either list of paths or path.")

    dfs = []
    for path in paths:
        df = load_func(path)
        dfs.append(df)

    result = pd.concat(dfs)

    return result


def multi_load_b3_scalars(paths):
    return multi_load(paths, load_b3_scalars)


def multi_load_b3_timeseries(paths):
    return multi_load(paths, load_b3_timeseries)


def expand_regions(scalars, regions, where="ALL"):
    r"""
    Expects scalars in oemof_b3 format (defined in ''oemof_b3/schema/scalars.csv'') and regions.
    Returns scalars with new rows included for each region in those places where region equals
    `where`.

    Parameters
    ----------
    scalars : pd.DataFrame
        Data in oemof_b3 format to expand
    regions : list
        List of regions
    where : str
        Key that should be expanded
    Returns
    -------
    sc_with_region : pd.DataFrame
        Data with expanded regions in oemof_b3 format
    """
    _scalars = format_header(scalars, HEADER_B3_SCAL, "id_scal")

    sc_with_region = _scalars.loc[scalars["region"] != where, :].copy()

    sc_wo_region = _scalars.loc[scalars["region"] == where, :].copy()

    if sc_wo_region.empty:
        return sc_with_region

    for region in regions:
        regionalized = sc_wo_region.copy()

        regionalized["name"] = regionalized.apply(
            lambda x: "-".join([region, x["carrier"], x["tech"]]), 1
        )

        regionalized["region"] = region

        sc_with_region = sc_with_region.append(regionalized)

    sc_with_region = sc_with_region.reset_index(drop=True)

    sc_with_region.index.name = "id_scal"

    return sc_with_region


def update_with_checks(old, new):
    r"""
    Updates a Series or DataFrame with new data. Raises a warning if there is new data that is not
    in the index of the old data.
    Parameters
    ----------
    old : pd.Series or pd.DataFrame
        Old Series or DataFrame to update
    new : pd.Series or pd.DataFrame
        New Series or DataFrame

    Returns
    -------
    None
    """
    # Check if some data would get lost
    if not new.index.isin(old.index).all():
        print("Index of new data is not in the index of old data.")

    try:
        # Check if it overwrites by setting errors = 'raise'
        old.update(new, errors="raise")
    except ValueError:
        old.update(new, errors="ignore")
        print("Update overwrites existing data.")


def parametrize_scalars(edp, scalars, filters):
    r"""
    Parametrizes an oemoflex.EnergyDataPackage with scalars. Accepts an OrderedDict of filters
    that is used to filter the scalars and subsequently update the EnergyDatapackage.

    Parameters
    ----------
    edp : oemoflex.EnergyDatapackage
        EnergyDatapackage to parametrize
    scalars : pd.DataFrame in oemof_B3-Resources format.
        Scalar data
    filters : OrderedDict
        Filters for the scalar data

    Returns
    -------
    edp : oemoflex.EnergyDatapackage
        Parametrized EnergyDatapackage
    """
    edp.stack_components()

    for id, filt in filters.items():
        filtered = scalars.copy()

        for key, value in filt.items():

            filtered = filter_df(filtered, key, value)

        filtered = filtered.set_index(["name", "var_name"]).loc[:, "var_value"]

        duplicated = filtered.loc[filtered.index.duplicated()]

        if duplicated.any():
            raise ValueError(f"There are duplicates in the scalar data: {duplicated}")

        update_with_checks(edp.data["component"], filtered)

        print(f"Updated DataPackage with scalars filtered by {filt}.")

    edp.unstack_components()

    return edp


def parametrize_sequences(edp, ts, filters):
    r"""
    Parametrizes an oemoflex.EnergyDataPackage with timeseries.

    Parameters
    ----------
    edp : oemoflex.EnergyDatapackage
        EnergyDatapackage to parametrize
    ts : pd.DataFrame in oemof_B3-Resources format.
        Timeseries data
    filters : dict
        Filters for timeseries data

    Returns
    -------
    edp : oemoflex.EnergyDatapackage
        Parametrized EnergyDatapackage
    """
    # Filter timeseries
    _ts = ts.copy()

    for key, value in filters.items():
        _ts = filter_df(_ts, key, value)

    # Group timeseries and parametrize EnergyDatapackage
    ts_groups = _ts.groupby("var_name")

    for name, group in ts_groups:

        data = group.copy()  # avoid pandas SettingWithCopyWarning

        data.loc[:, "var_name"] = data.loc[:, "region"] + "-" + data.loc[:, "var_name"]

        data_unstacked = unstack_timeseries(data)

        edp.data[name].update(data_unstacked)

    print(f"Updated DataPackage with timeseries from '{paths_timeseries}'.")

    return edp


def save_additional_scalars(scalars, destination):
    """Saves additional scalars like the emission limit to `ADDITIONAL_SCALARS_FILE`"""
    # get electricity/gas relations and emission limit
    el_gas_rel = scalars.loc[scalars.var_name == EL_GAS_RELATION]
    emissions = scalars.loc[scalars.var_name == EMISSION_LIMIT]

    # get `output_parameters` of backpressure components as they are not take into
    # consideration in oemof.tabular so far. They are added to the components' output flow towards
    # the heat bus in script `optimize.py`.
    bpchp_out = scalars.loc[(scalars.tech == "bpchp") & (scalars.var_name == "output_parameters")]

    # save all dataframes in one file
    df = pd.concat([el_gas_rel, emissions, bpchp_out])
    filename = os.path.join(destination, ADDITIONAL_SCALARS_FILE)
    save_df(df, filename)


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

    # parametrize scalars
    paths_scalars = scenario_specs["paths_scalars"]

    scalars = multi_load_b3_scalars(paths_scalars)

    # Replace 'ALL' in the column regions by the actual regions
    scalars = expand_regions(scalars, scenario_specs["regions"])

    filters = OrderedDict(sorted(scenario_specs["filter_scalars"].items()))

    edp = parametrize_scalars(edp, scalars, filters)

    # parametrize timeseries
    paths_timeseries = scenario_specs["paths_timeseries"]

    ts = multi_load_b3_timeseries(paths_timeseries)

    filters = scenario_specs["filter_timeseries"]

    edp = parametrize_sequences(edp, ts, filters)

    # save to csv
    edp.to_csv_dir(destination)

    # save emission limit and gas-electricity-relation to "additional_scalars.csv" in `destination`
    save_additional_scalars(scalars=scalars, destination=destination)

    # add metadata
    edp.infer_metadata(foreign_keys_update=foreign_keys_update)
