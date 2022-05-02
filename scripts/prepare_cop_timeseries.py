# coding: utf-8
r"""
Inputs
-------
in_path1 : str
    ``raw/weatherdata``: path of input directory with weather data
in_path2 : str
    ``raw/scalars/capacities.csv``: path of scalar data as .csv

Outputs
---------
pandas.DataFrame
    with timeseries of cops of air-water heat pumps

Description
-------------
The script calculates cop timeseries of small-scale air-water heat pumps for decentralized use.
"""

import datetime
import os
import sys
import itertools
import pandas as pd
import numpy as np
import oemof_b3.tools.data_processing as dp

# from oemof.thermal.compression_heatpumps_and_chillers import calc_cops


def find_regional_files(path, region):
    """
    This function returns a list of file names in a directory that match the specified region.

    Parameters
    ----------
    path : str
        Path to data

    region : str
        Region (eg. Brandenburg)

    Returns
    -------
    files_region : list
        List of file names matching region
    """
    files_region = [file for file in os.listdir(path) if f"_{region}_" in file]
    files_region = sorted(files_region)

    if not files_region:
        raise FileNotFoundError(
            f"No data of region {region} could be found in directory: {path}."
        )

    return files_region


def get_year(file_name):
    """
    This function returns a year from file name

    Parameters
    ----------
    file_name : str
        Name of file with year in it

    Returns
    -------
    year : int
        Year
    """
    # Add array with years to be searched for in file name
    years_search_array = np.arange(1990, 2051)
    newline = "\n"

    year_in_file = [
        year_searched
        for year_searched in years_search_array
        if str(year_searched) in file_name
    ]
    if len(year_in_file) == 1:
        year = year_in_file[0]
    else:
        raise ValueError(
            f"Your file {file_name} is missing a year or has multiple years "
            f"in its name." + newline + "Please provide data for a single year "
            "with that year in the file name."
        )

    return year


def calc_cops(temp_high, temp_low, quality_grade):
    """
    This function is based on the calc_cops function in the module
    compression_heatpumps_and_chillers.py of oemof.thermal
    https://github.com/oemof/oemof-thermal.

    It calculates the Coefficient of Performance (COP) of heat pumps
    based on the Carnot efficiency (ideal process) and a scale-down factor.

     Parameters
    ----------
    temp_high : list or pandas.Series of numerical values
        Temperature of the high temperature reservoir in degrees Celsius
    temp_low : list or pandas.Series of numerical values
        Temperature of the low temperature reservoir in degrees Celsius
    quality_grade : numerical value
        Factor that scales down the efficiency of the real heat pump
        (or chiller) process from the ideal process (Carnot efficiency), where
         a factor of 1 means teh real process is equal to the ideal one.

    Returns
    -------
    cops : list of numerical values
        List of Coefficients of Performance (COPs)
    """
    # Check if input arguments have proper type and length
    if not isinstance(temp_low, (list, pd.Series)):
        raise TypeError("Argument 'temp_low' is not of type list or pd.Series!")

    if not isinstance(temp_high, (list, pd.Series)):
        raise TypeError("Argument 'temp_high' is not of " "type list or pd.Series!")

    if len(temp_high) != len(temp_low):
        if (len(temp_high) != 1) and ((len(temp_low) != 1)):
            raise IndexError(
                "Arguments 'temp_low' and 'temp_high' "
                "have to be of same length or one has "
                "to be of length 1 !"
            )

    # Make temp_low and temp_high have the same length and
    # convert unit to Kelvin.
    length = max([len(temp_high), len(temp_low)])
    if len(temp_high) == 1:
        list_temp_high_K = [temp_high[0] + 273.15] * length
    elif len(temp_high) == length:
        list_temp_high_K = [t + 273.15 for t in temp_high]
    if len(temp_low) == 1:
        list_temp_low_K = [temp_low[0] + 273.15] * length
    elif len(temp_low) == length:
        list_temp_low_K = [t + 273.15 for t in temp_low]

    cops = [
        quality_grade * t_h / (t_h - t_l)
        for t_h, t_l in zip(list_temp_high_K, list_temp_low_K)
    ]

    return cops


if __name__ == "__main__":
    in_path1 = sys.argv[1]  # path to csv with b3 capacities
    in_path2 = sys.argv[2]  # path to weather data
    out_path = sys.argv[3]  # path to timeseries of cops of small-scale heat pumps

    # Read state heat demands of ghd and hh sectors
    sc = dp.load_b3_scalars(in_path1)

    # Filter sc for heat pump capacities
    sc_filtered = dp.filter_df(sc, "tech", ["heatpump_small"])

    # get regions from data
    regions = sc_filtered.loc[:, "region"].unique()

    scenarios = sc_filtered.loc[:, "scenario_key"].unique()

    # Create empty data frame for results / output
    final_cops = pd.DataFrame(columns=dp.HEADER_B3_TS)

    for region, scenario in itertools.product(regions, scenarios):
        weather_file_names = find_regional_files(in_path2, region)

        for weather_file_name in weather_file_names:
            # Read year from weather file name
            year = get_year(weather_file_name)

            # Read temperature from weather data
            path_weather_data = os.path.join(in_path2, weather_file_name)
            temperature = pd.read_csv(
                path_weather_data,
                usecols=["temp_air", "precipitable_water"],
                header=0,
            )

            # Sink temperature: Surface + warm water heating
            temp_high = [
                50
            ]  # TODO https://www.buderus.de/de/waermepumpe/vorlauftemperatur
            # Source temperature: Ambient temperature
            temp_low = temperature["temp_air"]
            # Quality grade of an air/water heat pump
            quality_grade = 0.4

            cops = pd.DataFrame(
                index=pd.date_range(
                    datetime.datetime(year, 1, 1, 0),
                    periods=len(temperature),
                    freq="H",
                )
            )

            cops["air-water"] = calc_cops(temp_high, temp_low, quality_grade)

            final_cops = dp.postprocess_data(
                final_cops,
                cops,
                region,
                scenario,
                ["-"],
            )

    dp.save_df(final_cops, out_path)