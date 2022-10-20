# coding: utf-8
r"""
Inputs
-------
scenario_specs : str
    ``scenarios/{scenario}.yml``: path of input file (.yml) containing scenario specifications
destination : str
    ``results/{scenario}/preprocessed``: path of output directory
logfile : str
    ``logs/{scenario}.log``: path to logfile

Outputs
---------
oemoflex.EnergyDatapackage
    EnergyDatapackage that can be read by oemof.tabular, with data (scalars and timeseries)
    as csv and metadata (describing resources and foreign key relations) as json.

Description
-------------
The script creates an empty EnergyDatapackage from the specifications given in the scenario_specs,
fills it with scalar and timeseries data, infers the metadata and saves it to the given destination.
Further, additional parameters like emission limit are saved in a separate file.

Explanations about the structure of the result datapackage can be found in section
:ref:`Preprocessed datapackages` of the `docu <https://oemof-b3.readthedocs.io/en/latest/index.html>`_.

"""
import logging
import sys
import os
from collections import OrderedDict

import pandas as pd
from oemoflex.model.datapackage import EnergyDataPackage
from oemof_b3.config.config import load_yaml

from oemof_b3.model import (
    model_structures,
    bus_attrs_update,
    component_attrs_update,
    foreign_keys_update,
)
from oemof_b3.tools.data_processing import (
    filter_df,
    update_filtered_df,
    multi_load_b3_scalars,
    multi_load_b3_timeseries,
    unstack_timeseries,
    expand_regions,
    save_df,
)
from oemof_b3.config import config

logger = logging.getLogger()


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
        logger.warning("Index of new data is not in the index of old data.")

    try:
        # Check if it overwrites by setting errors = 'raise'
        old.update(new, errors="raise")
    except ValueError:
        old.update(new, errors="ignore")
        logger.warning("Update overwrites existing data.")


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

    # apply filters subsequently
    filtered = update_filtered_df(scalars, filters)

    # set index to component name and var_name
    filtered = filtered.set_index(["name", "var_name"]).loc[:, "var_value"]

    # check if there are duplicates after setting index
    duplicated = filtered.loc[filtered.index.duplicated()]

    if duplicated.any():
        raise ValueError(f"There are duplicates in the scalar data: {duplicated}")

    update_with_checks(edp.data["component"], filtered)

    edp.unstack_components()

    logger.info(f"Updated DataPackage with timeseries from '{paths_scalars}'.")

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

        edp.data[name] = data_unstacked

        edp.data[name].index.name = "timeindex"

    logger.info(f"Updated DataPackage with timeseries from '{paths_timeseries}'.")

    return edp


def load_additional_scalars(scalars, filters):
    """Loads additional scalars like the emission limit and filters by 'scenario_key'"""
    # get electricity/gas relations and parameters for the calculation of emission_limit
    el_gas_rel = scalars.loc[
        scalars.var_name == config.settings.build_datapackage.el_gas_relation
    ]
    emissions = scalars.loc[
        scalars.carrier == config.settings.build_datapackage.emission
    ]

    # get `output_parameters` of backpressure components as they are not taken into
    # consideration in oemof.tabular so far. They are added to the components' output flow towards
    # the heat bus in script `optimize.py`.
    bpchp_out = scalars.loc[
        (scalars.tech == "bpchp") & (scalars.var_name == "output_parameters")
    ]

    # concatenate data for filtering
    df = pd.concat([el_gas_rel, emissions, bpchp_out])

    # subsequently apply filters
    filtered_df = update_filtered_df(df, filters)

    # calculate emission limit and prepare data frame in case all necessary data is available
    _filtered_df = filtered_df.copy().set_index("var_name")
    try:
        emission_limit = calculate_emission_limit(
            _filtered_df.at["emissions_1990", "var_value"],
            _filtered_df.at["emissions_not_modeled", "var_value"],
            _filtered_df.at["emission_reduction_factor", "var_value"],
        )
    except KeyError:
        emission_limit = None

    emission_limit_df = pd.DataFrame(
        {
            "var_name": "emission_limit",
            "var_value": emission_limit,
            "carrier": "emission",
            "var_unit": "kg_CO2_eq",
            "scenario_key": "ALL",
        },
        index=[0],
    )

    # add emission limit to filtered additional scalars and adapt format of data frame
    add_scalars = pd.concat([filtered_df, emission_limit_df], sort=False)
    add_scalars.reset_index(inplace=True, drop=True)
    add_scalars.index.name = "id_scal"

    return add_scalars


def save_additional_scalars(additional_scalars, destination):
    """Saves `additional_scalars` to additional_scalar_file in `destination`"""
    filename = os.path.join(
        destination, config.settings.build_datapackage.additional_scalars_file
    )
    save_df(additional_scalars, filename)

    logger.info(f"Saved additional scalars to '{filename}'.")


def calculate_emission_limit(
    emissions_1990, emissions_not_modeled, emission_reduction_factor
):
    """Calculates the emission limit.
    Emission limit is calculated by
    emissions_1990 * (1 - emission_reduction_factor) - emissions_not_modeled"""

    return emissions_1990 * (1 - emission_reduction_factor) - emissions_not_modeled


if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    destination = sys.argv[2]

    logfile = sys.argv[3]
    logger = config.add_snake_logger(logfile, "build_datapackage")

    scenario_specs = load_yaml(scenario_specs)

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

    # parametrize scalars
    paths_scalars = scenario_specs["paths_scalars"]

    scalars = multi_load_b3_scalars(paths_scalars)

    # Replace 'ALL' in the column regions by the actual regions
    scalars = expand_regions(scalars, model_structure["regions"])

    # get filters for scalars
    filters = OrderedDict(sorted(scenario_specs["filter_scalars"].items()))

    # load additional scalars like "emission_limit" and filter by `filters` in 'scenario_key'
    additional_scalars = load_additional_scalars(scalars=scalars, filters=filters)

    # Drop those scalars that do not belong to a specific component
    scalars = scalars.loc[~scalars["name"].isna()]

    # filter and parametrize scalars
    edp = parametrize_scalars(edp, scalars, filters)

    # parametrize timeseries
    paths_timeseries = scenario_specs["paths_timeseries"]

    ts = multi_load_b3_timeseries(paths_timeseries)

    filters = scenario_specs["filter_timeseries"]

    edp = parametrize_sequences(edp, ts, filters)

    # save to csv
    edp.to_csv_dir(destination)

    logger.info(f"Saved datapackage to '{destination}'.")

    save_additional_scalars(
        additional_scalars=additional_scalars, destination=destination
    )

    logger.info(f"Saved additional_scalars to '{destination}'.")

    # add metadata
    edp.infer_metadata(foreign_keys_update=foreign_keys_update)
