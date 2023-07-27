# coding: utf-8
r"""
Inputs
-------
input_dir : str
    ``raw/time_series/vehicle_charging``: Path of directory where csv-files containing electric
    vehicle charging demand profiles are placed
scalars_file : str
    ``raw/scalars/demands.csv``: Path incl. file name of demand scalars including 'bev_car_share',
    the share of electricity demand for charging passenger cars
output_file : str
    ``results/_resources/ts_load_electricity_vehicles.csv``: Path incl. file name of prepared time
    series
logfile : str
    ``results/_resources/ts_load_electricity_vehicles.log``: path to logfile

Outputs
---------
pd.DataFrame
    Normalized electric vehicle charging demand profiles for regions "B" and "BB" for all years
    provided in `input_dir`.

Description
-------------
This script prepares electric vehicle charging demand profiles for the regions Berlin and
Brandenburg. The profiles for passenger cars have been created before with simBEV
(https://github.com/rl-institut/simbev), other vehicles are taken into consideration with constant
profiles. The charging strategy of simBEV data is "greedy", i.e. batteries are charged with maximum
power until they are fully charged or removed. This script applies a charging strategy we refer to
as "balanced" for the profiles "home" and "work" during specific hours (see global variables). To
apply this, charging strategy values between [`HOME_START`, `HOME_END`] and
[`WORK_START`, `WORK_END`] respectively are replaced by the average of all these values. We assume
that this is a more realistic picture of the future than a charging strategy "greedy".
"""

import sys
import pandas as pd
import os

import oemof_b3.tools.data_processing as dp
from oemof_b3.config import config

# dummy logger for tests
import logging

logger = logging.getLogger("dummy")

# global variables
TS_INDEX_NAME = config.settings.general.ts_index_name
HOME_START = (
    config.settings.prepare_vehicle_charging_demand.home_start
)  # start charging strategy "balanced" for home profile
HOME_END = (
    config.settings.prepare_vehicle_charging_demand.home_end
)  # end charging strategy "balanced" for home profile
WORK_START = (
    config.settings.prepare_vehicle_charging_demand.work_start
)  # start charging strategy "balanced" for work profile
WORK_END = (
    config.settings.prepare_vehicle_charging_demand.work_end
)  # end charging strategy "balanced" for work profile


def prepare_vehicle_charging_demand(input_dir, balanced=True, const_share=None):
    r"""
    Prepares and formats electric vehicle charging demand profiles for regions 'B' and 'BB'.

    The simBEV profiles are passenger cars charging demand profiles. If `const_share` of the
    charging demand is given this hourly profile is mixed with a constant profile:
    car_profile * (1 - const_share) + constant_profile * const_share
        (using specified profiles, i.e. divided by their yearly sum)

    The profiles are resampled from 15-min to hourly time steps. If `balanced` is True the profiles
    "work" and "home" are smoothed between [`HOME_START`, `HOME_END`] and
    [`WORK_START`, `WORK_END`]. The respective values are replaced by the average of all these
    values. We refer to this as charging strategy 'balanced'.
    The charging demand profile is then divided by the total demand.

    Parameters
    ----------
    input_dir : str
        Path to directory where csv files containing electric vehicle charging demand profiles
        are placed
    balanced : bool
        If True profiles "work" and "home" are smoothed with charging strategy "balanced" with
        :py:func:`smooth_profiles()`.
        Default: True
    const_share : float
        If given the passenger car charging profile is mixed with a constant profile.
        Default: None

    Returns
    -------
    ts_prepared : pd.DataFrame
        Contains electric vehicle charging demand profiles in the format of time series template of
        oemof-B3

    """

    def get_year_region_from_filename():
        """Gets  region and year from file name"""
        split_filename = os.path.splitext(os.path.basename(filename))[0].split("_")
        r, y = split_filename[2], int(split_filename[3])
        return r, y

    if const_share is not None:
        logger.info(
            f"Passenger car charging profile is mixed with constant share of "
            f"{int(const_share*100)} %."
        )
    if balanced:
        logger.info(
            f"Passenger car charging profiles have charging strategy 'balanced': 'home' between "
            f"{HOME_START} and {HOME_END}, 'work' between {WORK_START} and {WORK_END}."
        )

    # initialize data frame
    df = pd.DataFrame()

    # loop through files in `input_dir`
    for filename in os.listdir(input_dir):
        path = os.path.join(input_dir, filename)
        region, year = get_year_region_from_filename()
        region = config.settings.prepare_vehicle_charging_demand.region_dict[region]

        # read data from file, copy and superfluous drop last time step
        ts_raw = pd.read_csv(
            path,
            index_col=1,
            sep=";",
            decimal=".",
            parse_dates=True,
            thousands=",",
        ).drop(columns=["Unnamed: 0"], axis=1)
        ts_raw.index = pd.to_datetime(
            ts_raw.index, infer_datetime_format=True, errors="coerce", utc=True
        )
        ts = ts_raw[ts_raw.index.year == year]

        # resample (15 min to hourly), unit is kW
        hourly_ts = ts.resample("H").mean()

        if balanced:
            # smooth work and home profiles as they have high peaks (strategy balanced)
            hourly_ts = smooth_profiles(df=hourly_ts)

        # only keep column "sum CS power" (sum of power demand at all charging stations)
        ts_total_demand = pd.DataFrame(hourly_ts["sum CS power"]).rename(
            columns={"sum CS power": f"ts_{year}"}
        )

        # divide by total electricity demand of vehicles
        ts_total_norm = ts_total_demand / ts_total_demand.sum()

        if const_share is not None:
            # combine car profile and constant profile with `const_share`
            length = len(ts_total_demand)
            constant_ts_norm = pd.DataFrame(
                [1 / length] * length,
                index=ts_total_demand.index,
            )
            array_ts_total_norm = (
                ts_total_norm.values * (1 - const_share)
                + constant_ts_norm.values * const_share
            )
            ts_total_norm[f"ts_{year}"] = array_ts_total_norm

        # stack time series and add region
        ts_stacked = dp.stack_timeseries(ts_total_norm)

        # The profile is not varied in different scenarios
        ts_stacked.loc[:, "scenario_key"] = "ALL"

        ts_stacked.loc[:, "region"] = region

        # add to `df`
        df = pd.concat([df, ts_stacked], axis=0)

    # prepare index
    df.reset_index(inplace=True, drop=True)
    df.index.name = TS_INDEX_NAME

    # bring time series to oemof-B3 format with `stack_timeseries()` and `format_header()`
    ts_prepared = dp.format_header(
        df=df, header=dp.HEADER_B3_TS, index_name=TS_INDEX_NAME
    )

    # add additional information as required by template
    ts_prepared.loc[
        :, "var_unit"
    ] = config.settings.prepare_vehicle_charging_demand.ts_var_unit
    ts_prepared.loc[
        :, "var_name"
    ] = config.settings.prepare_vehicle_charging_demand.var_name
    ts_prepared.loc[
        :, "source"
    ] = config.settings.prepare_vehicle_charging_demand.ts_source
    ts_prepared.loc[
        :, "comment"
    ] = config.settings.prepare_vehicle_charging_demand.ts_comment

    return ts_prepared


def smooth_profiles(df):
    r"""
    Smoothes profiles "work" and "home" of `df` between specific hours (see global variables).

    Values between [`HOME_START`, `HOME_END`] and [`WORK_START`, `WORK_END`] respectively are
    replaced by the average of all these values. We refer to this as charging strategy 'balanced'.

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

    def balance_between_hours(ts, start, end):
        """Apply charging strategy 'balanced' between two hours of the day."""
        # calculate average between start and end
        average = ts.between_time(start, end).mean()
        # set average for times between start and end
        ts.loc[ts.between_time(start, end).index] = average
        return ts

    df["sum UC work"] = df.groupby(df.index.date)["sum UC work"].apply(
        lambda x: balance_between_hours(ts=x, start=WORK_START, end=WORK_END)
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
        lambda x: balance_between_hours(ts=x, start=HOME_START, end=HOME_END)
    )

    # get total charging df after balancing
    df["sum CS power"] = df.drop("sum CS power", axis=1).sum(axis=1)

    return df


def get_constant_share_of_vehicle_ts(filename):
    """Reads electric car share from `filename` and returns (1 - car_share), the constant share"""
    scalars = dp.load_b3_scalars(filename)
    car_share = scalars.loc[scalars["var_name"] == "bev_car_share"].var_value.iloc[0]
    const_share = 1 - car_share
    return const_share


if __name__ == "__main__":
    input_dir = sys.argv[1]
    scalars_file = sys.argv[2]
    output_file = sys.argv[3]

    logger = config.add_snake_logger("prepare_vehicle_charging_demand")

    # get constant share of electric charging demand
    const_share = get_constant_share_of_vehicle_ts(scalars_file)

    time_series = prepare_vehicle_charging_demand(
        input_dir=input_dir, const_share=const_share
    )

    # create output directory in case it does not exist, yet and save data to `output_file`
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dp.save_df(time_series, output_file)
