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
    with timeseries of cops of air driven, water driven and ground driven heat pumps

Description
-------------
The script calculates cop timeseries of
    1. air driven heat pumps
    2. water driven heat pumps
    3. ground driven heat pumps
heat pumps.
"""

import datetime
import os
import sys
import pandas as pd
import numpy as np
import itertools
import scripts.prepare_heat_demand as phd
import oemof_b3.tools.data_processing as dp
from oemof.thermal.compression_heatpumps_and_chillers import calc_cops

if __name__ == "__main__":
    in_path1 = sys.argv[1]  # path to csv with b3 capacities
    in_path2 = sys.argv[2]  # path to weather data
    out_path1 = sys.argv[3]  # path to timeseries of cops of small heat pumps
    out_path2 = sys.argv[4]  # path to timeseries of cops of large heat pumps

    #################### To be deleted ####################
    # path_this_file = os.path.realpath(__file__)
    # raw_data = os.path.abspath(
    #     os.path.join(path_this_file, os.pardir, os.pardir, "raw")
    # )
    #
    # in_path1 = os.path.join(raw_data, "scalars", "capacities.csv")
    # in_path2 = os.path.join(raw_data, "weatherdata")
    # out_path1 = os.path.join(
    #     os.pardir, "results", "_resources", "ts_efficiency_heatpump_small.csv"
    # )
    # out_path2 = os.path.join(
    #     os.pardir, "results", "_resources", "ts_efficiency_heatpump_large.csv"
    # )
    #######################################################

    # Read state heat demands of ghd and hh sectors
    sc = dp.load_b3_scalars(in_path1)

    hp_systems = ["small", "large"]

    for hp_system in hp_systems:
        # Filter sc for heat pump capacities
        sc_filtered = dp.filter_df(sc, "tech", ["heatpump_" + hp_system])

        # get regions from data
        regions = sc_filtered.loc[:, "region"].unique()

        scenarios = sc_filtered.loc[:, "scenario_key"].unique()

        # Create empty data frame for results / output
        final_cops = pd.DataFrame(columns=dp.HEADER_B3_TS)

        for region, scenario in itertools.product(regions, scenarios):
            weather_file_names = phd.find_regional_files(in_path2, region)

            for weather_file_name in weather_file_names:
                # Read year from weather file name
                year = phd.get_year(weather_file_name)

                # Read temperature from weather data
                path_weather_data = os.path.join(in_path2, weather_file_name)
                temperature = pd.read_csv(
                    path_weather_data,
                    usecols=["temp_air", "precipitable_water"],
                    header=0,
                )

                temp_air = temperature["temp_air"]
                temp_water = temperature["precipitable_water"]
                temp_ground = [np.average(temperature[["temp_air"]].values)]

                hps = {
                    "air_driven": [temp_air, 0.4],
                    "water_driven": [temp_water, 0.5],
                    "ground_driven": [temp_ground * len(temperature), 0.55],
                }
                cops = pd.DataFrame(
                    index=pd.date_range(
                        datetime.datetime(year, 1, 1, 0),
                        periods=len(temperature),
                        freq="H",
                    )
                )

                for name, params in hps.items():
                    temp_low = params[0]
                    quality_grade = params[1]

                    cops[name] = calc_cops("heat_pump", [40], temp_low, quality_grade)

                # Calculate distribution of COP TODO: To be reworked
                cops["total"] = cops.mean(axis=1)

                final_cops = phd.postprocess_data(
                    final_cops,
                    cops.drop(columns=cops.columns[0:3]),
                    region,
                    scenario,
                    ["-"],
                )

        if hp_system == "small":
            dp.save_df(final_cops, out_path1)
        elif hp_system == "large":
            dp.save_df(final_cops, out_path2)
