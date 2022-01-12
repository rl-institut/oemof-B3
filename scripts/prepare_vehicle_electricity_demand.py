# coding: utf-8
r"""
Inputs
-------
input_dir : str
    ``raw/time_series/vehicle_charging``: Path to directory where csv files containing electric
    vehicle charging demand time series are placed
output_file : str
    ``results/_resources/ts_load_electricity_vehicles.csv``: Path incl. file name to prepared time
    series

Outputs
---------
pandas.DataFrame
    Normalized electric vehicle charging demand for regions "B" and "BB" for all years provided in
    `input_dir`.

Description
-------------
This script prepares electric vehicle charging demand time series for the regions Berlin
and Brandenburg. The time series have been created before with simBEV
(https://github.com/rl-institut/simbev). The charging strategy is "greedy", i.e. batteries are
charged with maximum power until they are fully charged or removed.

"""

import sys
import pandas as pd
import os
import oemof_b3.tools.data_processing as dp

# global variables
TS_VAR_UNIT = "None"
TS_SOURCE = "created with simBEV"
TS_COMMENT = "https://github.com/rl-institut/simbev"


def prepare_vehicle_time_series(input_dir):
    r"""
    Prepares and formats electric vehicle charging demand time series for regions 'B' and 'BB'.

    Parameters
    ----------
    input_dir : str
        Path to directory where csv files containing electric vehicle charging demand time series
        are placed

    Returns
    -------
    ts_prepared : pd.DataFrame
        Contains electric vehicle charging demand time series in the format of time series template
        of oemof-B3

    """
    # initialize data frame
    df = pd.DataFrame()

    # loop through files in `input_dir`
    for filename in os.listdir(input_dir):
        # get year and region from file name
        split_filename = os.path.splitext(os.path.basename(filename))[0].split("_")
        region, year = split_filename[2], int(split_filename[3])
        path = os.path.join(input_dir, filename)

        # read data from file, copy and superfluous drop last time step
        ts_raw = pd.read_csv(
            path, index_col=1, sep=";", decimal=",", parse_dates=True
        ).drop(columns=["Unnamed: 0"], axis=1)
        ts = ts_raw[ts_raw.index.year == year]

        # resample (15 min to hourly)
        hourly_ts = ts.resample("H").sum()

        # normalize with total electricity demand
        hourly_ts_norm = hourly_ts / hourly_ts.sum()

        # only keep column "sum CS power" (sum of power demand at all charging stations)
        ts_df = pd.DataFrame(hourly_ts_norm["sum CS power"]).rename(
            columns={"sum CS power": f"ts_{year}"}
        )

        # stack time series and add region
        ts_stacked = dp.stack_timeseries(ts_df).rename(columns={"var_name": "scenario"})
        ts_stacked.loc[:, "region"] = region

        # add to `df`
        df = pd.concat([df, ts_stacked], axis=0)

    # prepare index
    df.reset_index(inplace=True, drop=True)
    df.index.name = "id_ts"

    # bring time series to oemof-B3 format with `stack_timeseries()` and `format_header()`
    ts_prepared = dp.format_header(df=df, header=dp.HEADER_B3_TS, index_name="id_ts")

    # add additional information as required by template
    ts_prepared.loc[:, "var_unit"] = TS_VAR_UNIT
    ts_prepared.loc[:, "var_name"] = "vehicle-charging-profile"
    ts_prepared.loc[:, "source"] = TS_SOURCE
    ts_prepared.loc[:, "comment"] = TS_COMMENT

    return ts_prepared


if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    time_series = prepare_vehicle_time_series(input_dir=input_dir)

    # create output directory in case it does not exist, yet and save data to `output_file`
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dp.save_df(time_series, output_file)
