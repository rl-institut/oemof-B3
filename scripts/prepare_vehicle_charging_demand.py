# coding: utf-8
r"""
Inputs
-------
input_dir : str
    ``raw/time_series/vehicle_charging``: Path to directory where csv files containing electric
    vehicle charging demand profiles are placed
output_file : str
    ``results/_resources/ts_load_electricity_vehicles.csv``: Path incl. file name to prepared time
    series

Outputs
---------
pandas.DataFrame
    Normalized electric vehicle charging demand profiles for regions "B" and "BB" for all years
    provided in `input_dir`.

Description
-------------
This script prepares electric vehicle charging demand profiles for the regions Berlin and
Brandenburg. The profiles have been created before with simBEV
(https://github.com/rl-institut/simbev). The charging strategy of simBEV data is "greedy", i.e.
batteries are charged with maximum power until they are fully charged or removed. This scripts
applies a charging strategy "balanced" for the profiles "home" and "work" during specific hours (see
global variables).

"""

import sys
import pandas as pd
import os
import oemof_b3.tools.data_processing as dp

# global variables
TS_VAR_UNIT = "None"
TS_SOURCE = "created with simBEV"
TS_COMMENT = "https://github.com/rl-institut/simbev"
HOME_START = "15:00"  # start charging strategy "balanced" for home profile
HOME_END = "05:00"  # end charging strategy "balanced" for home profile
WORK_START = "06:00"  # start charging strategy "balanced" for work profile
WORK_END = "14:00"  # end charging strategy "balanced" for work profile


def prepare_vehicle_charging_demand(input_dir, balanced=True):
    r"""
    Prepares and formats electric vehicle charging demand profiles for regions 'B' and 'BB'.

    The profiles are resampled from 15-min to hourly time steps. If `balanced` is True the profiles
    "work" and "home" are smoothed between `HOME_START`, `HOME_END` and `WORK_START`, `WORK_END`
    respectively with charging strategy "balanced".
    The charging demand profile is then divided by the total demand.

    Parameters
    ----------
    input_dir : str
        Path to directory where csv files containing electric vehicle charging demand profiles
        are placed
    balanced : bool
        If True profiles "work" and "home" are smoothed with charging strategy "balanced".
        Default: True

    Returns
    -------
    ts_prepared : pd.DataFrame
        Contains electric vehicle charging demand profiles in the format of time series template of
        oemof-B3

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
            path,
            index_col=1,
            sep=";",
            decimal=",",
            parse_dates=True,
            thousands=".",
        ).drop(columns=["Unnamed: 0"], axis=1)
        ts = ts_raw[ts_raw.index.year == year]

        # resample (15 min to hourly), unit is kW
        hourly_ts = ts.resample("H").mean()

        if balanced:
            # smooth work and home profiles as they have high peaks (~strategy balanced)
            hourly_ts = balance_profiles(df=hourly_ts)

        # only keep column "sum CS power" (sum of power demand at all charging stations)
        ts_total_demand = pd.DataFrame(hourly_ts["sum CS power"]).rename(
            columns={"sum CS power": f"ts_{year}"}
        )

        # divide by total electricity demand of vehicles
        ts_total_norm = ts_total_demand / ts_total_demand.sum()

        # stack time series and add region
        ts_stacked = dp.stack_timeseries(ts_total_norm).rename(
            columns={"var_name": "scenario"}
        )
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


def balance_profiles(df):
    r"""
    Smoothes profiles "work" and "home" of `df` between specific hours (see global variables).

    Parameters
    ----------
    df: pandas.DataFrame
        Contains vehicle charging profiles.

    Returns
    -------
    df : pandas.DataFrame
        Vehicle charging profiles with smoothed "home" and "work" profiles and adapted total
        charging demand.
    """

    def balanced_between_hours(ts, start, end):
        """Apply charging strategy 'balanced' between two hours of the day."""
        # calculate average between start and end
        average = ts.between_time(start, end).mean()
        # set average for times between start and end
        ts.loc[ts.between_time(start, end).index] = average
        return ts

    df["sum UC work"] = df.groupby(df.index.date)["sum UC work"].apply(
        lambda x: balanced_between_hours(ts=x, start=WORK_START, end=WORK_END)
    )

    # for home: determine which hours of the day should belong to next day
    temp = (
        pd.DataFrame(df.index)["time"].apply(lambda x: 0 if x.hour < 12 else 1).values
    )
    df["temp"] = df.index.dayofyear + temp
    if int(HOME_START.split(":")[0]) < 12:
        raise ValueError(
            f"For smoothing home profile the days should be split at an earlier hour than 12 if "
            f"`HOME_START` is {HOME_START}."
        )

    df["sum UC home"] = df.groupby(df["temp"])["sum UC home"].apply(
        lambda x: balanced_between_hours(ts=x, start=HOME_START, end=HOME_END)
    )

    # get total charging df after balancing
    df["sum CS power"] = df.drop("sum CS power", axis=1).sum(axis=1)

    return df


if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    time_series = prepare_vehicle_charging_demand(input_dir=input_dir)

    # create output directory in case it does not exist, yet and save data to `output_file`
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dp.save_df(time_series, output_file)
