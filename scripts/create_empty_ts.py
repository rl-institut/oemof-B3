# coding: utf-8
r"""
Inputs
-------
scenarios_dir : str
    ``scenarios``: path to scenarios directory
destination : str
    ``raw/time_series/empty_ts_efficiencies.csv``: path of output directory for
    empty ts with efficiencies of all scenarios
    ``raw/time_series/empty_ts_feedin.csv``: path of output directory for
    empty ts with feedins of all scenarios
    ``raw/time_series/empty_ts_load.csv``: path of output directory for
    empty ts with loads of all scenarios

Outputs
---------
pandas.DataFrame
    Empty ts in oemof-B3 resource format.

Description
-------------
The script creates empty DataFrames for load, feed-in and efficiency time
series data that serve as template for input data.
"""
import sys
import os
import pandas as pd
import numpy as np

from datetime import datetime

from oemof_b3.config.config import load_yaml, settings
from oemof_b3.model import model_structures
from oemof_b3 import model
from oemof_b3.tools.data_processing import HEADER_B3_TS, stack_timeseries


def get_sub_dict(subsub_key, dict):
    """
    This function extracts a subsub-dictionary from a dictionary using a subsub-key

    Inputs
    -------
    subsub_key : str
        Key of the subsub-dictionary

    dict : dict
        Dictionary with two inner dictionaries

    Outputs
    -------
    subsub_dict : dictionary
        Subsub-dictionary

    """

    subsub_dict = [
        subsubdict
        for sub_dict in dict.values()
        for subsubdict in sub_dict.values()
        if subsub_key in subsubdict
    ]

    return subsub_dict


def create_empty_ts_with_zero_or_nan_values(periods, date_rng, name):
    """
    Returns a pandas DataFrame with time series values set to either zeros or
    NaNs, based on settings.yaml

    Parameters
    ----------
    periods : int
        Number of periods in the time series
    date_rng : pd.DatetimeIndex
        Datetime index specifying start and end dates of the time series
    name : str
        Name of the time series column in the DataFrame

    Returns
    -------
    df : pd.DataFrame
        A pandas DataFrame containing the time series values, with 'name' as
        the column name.

    Raises
    ------
    KeyError
        If settings.create_empty_ts.ts_values is not set to either 'zeros' or 'empty'.
    """
    ts_values = settings.create_empty_ts.ts_values

    if ts_values == "zeros":
        df = pd.DataFrame(np.zeros((periods, 1)), index=date_rng, columns=[name])
    elif ts_values == "empty":
        df = pd.DataFrame(
            np.empty((periods, 1)) * np.nan, index=date_rng, columns=[name]
        )
    else:
        raise KeyError(
            f"{ts_values} is not a valid option. Valid options are: 'zeros' or"
            f"'empty'. Please provide a valid value for ts_values in "
            f"settings.yaml"
        )

    return df


def create_empty_ts(name):
    """
    This function provides a Dataframe with a time series of zeros
    according to the start, periods and freq of the scenario specifications

    Parameters
    ----------
    name : str
        Name of the ts

    Returns
    -------
    df : Dataframe
        Dataframe containing ts with zeros as values and name as column name

    """
    format = settings.create_empty_ts.datetime_format

    # Get start date from scenario specifications
    start = datetime.strptime(scenario_specs["datetimeindex"]["start"], format)

    # Get periods and freq from scenario specifications
    periods = scenario_specs["datetimeindex"]["periods"]
    freq = scenario_specs["datetimeindex"]["freq"]

    # Get date range from start periods and freq
    date_rng = pd.date_range(start=start, periods=periods, freq=freq)

    # Create DataFrame with ts of zeros from date range and name
    df = create_empty_ts_with_zero_or_nan_values(periods, date_rng, name)

    return df


def get_df_of_all_empty_ts(profile_names, region):
    """
    This function provides a Dataframe with all ts of a profile (load, feedin
    or efficiency)

    Inputs
    -------
    profile_names : list
        List with names of profiles (loads, feedins or efficiencies)

    region : str
        Region

    Outputs
    -------
    ts_df : Dataframe
        Dataframe with empty time series (consisting of zeros)

    """
    ts_df = pd.DataFrame(columns=HEADER_B3_TS)

    for name in profile_names:
        df = create_empty_ts(name)

        # Stack Dataframe
        stacked_df = stack_timeseries(df)

        # Reindex according to time series in schema directory
        stacked_df = stacked_df.reindex(columns=HEADER_B3_TS)

        # Add region and scenario_specs to Dataframe
        stacked_df["region"] = region
        stacked_df["scenario_key"] = settings.create_empty_ts.filter_ts

        # Append Dataframe to ts_profile_df and add index name
        ts_df = pd.concat([ts_df, stacked_df], ignore_index=True)
        ts_df.index.name = "id_ts"

    return ts_df


def save_ts(_df, path):
    """
    This function saves time series that contain values of datetime format
    Datetime format used: "%Y-%m-%d %H:%M:%S"

    Parameters
    ----------
    _df : Dataframe
        Dataframe with value(s) of datetime format

    path : str
        Path where df is saved to


    """
    _df.to_csv(
        path,
        index=True,
        date_format="%Y-%m-%d %H:%M:%S",
        sep=settings.general.separator,
    )


if __name__ == "__main__":
    scenarios_dir = sys.argv[1]

    path_empty_load_ts = sys.argv[2]
    path_empty_ts_feedin = sys.argv[3]
    path_empty_ts_efficiencies = sys.argv[4]

    scenarios = os.listdir(scenarios_dir)

    for scenario_specs in scenarios:
        scenario_specs = load_yaml(os.path.join(scenarios_dir, scenario_specs))
        model_structure = model_structures[scenario_specs["model_structure"]]

        component_attrs_update = load_yaml(
            os.path.join(model.here, "component_attrs_update.yml")
        )

        # Get all foreign_keys that contain "profile" from component_attrs_update
        foreign_keys_profile = get_sub_dict("profile", component_attrs_update)

        # Get all foreign_keys that contain "efficiency" from component_attrs_update
        foreign_keys_efficiency = get_sub_dict("efficiency", component_attrs_update)

        # Save profile names depending on whether it is a load, a feed-in or an efficiency
        load_names = [
            attr_subdict["profile"]
            for attr_subdict in foreign_keys_profile
            if "demand" in attr_subdict["profile"]  # noqa: E713
        ]
        feedin_names = [
            attr_subdict["profile"]
            for attr_subdict in foreign_keys_profile
            if not "demand" in attr_subdict["profile"]  # noqa: E713
        ]
        efficiency_names = [
            attr_subdict["efficiency"] for attr_subdict in foreign_keys_efficiency
        ]

        for region in model_structure["regions"]:
            if load_names:
                df_loads = get_df_of_all_empty_ts(load_names, region)
                save_ts(df_loads, path_empty_load_ts)

            if feedin_names:
                df_feedin = get_df_of_all_empty_ts(feedin_names, region)
                save_ts(df_feedin, path_empty_ts_feedin)

            if efficiency_names:
                df_efficiencies = get_df_of_all_empty_ts(efficiency_names, region)
                save_ts(df_efficiencies, path_empty_ts_efficiencies)
