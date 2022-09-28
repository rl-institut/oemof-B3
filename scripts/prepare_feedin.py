# coding: utf-8
r"""
Inputs
-------
filename_wind : str
    ``raw/time_series/ninja_wind_country_DE_current_merra-2_nuts-2_corrected.csv``: Path incl. file
    name of wind feed-in time series of renewables ninja
filename_pv : str
    ``raw/time_series/ninja_pv_country_DE_merra-2_nuts-2_corrected.csv``: Path incl. file name of pv
    feed-in time series of renewables ninja
filename_ror : str
    ``raw/time_series/DIW_Hydro_availability.csv``: Path incl. file name of feed-in time series of
    run-of-river power plants
output_file : str
    ``results/_resources/ts_feedin.csv``: Path incl. file name of prepared time series

Outputs
---------
pd.DataFrame
    Prepared feed-in time series of pv, wind and hydropower

Description
-------------
This script prepares wind, pv and run-of-the-river (ror) feed-in time series for the regions Berlin
and Brandenburg. Raw data is read from csvs from https://www.renewables.ninja/ (wind+pv) and
https://zenodo.org/record/1044463 (ror) and is then formatted to fit the time series template of
oemof-B3 (`schema/timeseries.csv`).

"""

import sys
import pandas as pd
import os
import oemof_b3.tools.data_processing as dp
import oemof_b3.config.config as config

# global variables
TS_INDEX_NAME = config.settings.general.ts_index_name


def prepare_wind_and_pv_time_series(filename_ts, year, type):
    r"""
    Prepares and formats time series of `type` 'wind' or 'pv' for region 'B' and 'BB'.

    Parameters
    ----------
    filename_ts : str
        Path including file name to wind and pv time series of renewables ninja for NUTS2 regions
    year : int
        Year for which time series is extracted from raw data in `filename_ts`
    type : str
        Type of time series like 'wind' or 'pv'; used for column 'var_name' in output

    Returns
    -------
    ts_prepared : pd.DataFrame
        Contains time series in the format of time series template of oemof-B3

    """
    # load raw time series and copy data frame
    ts_raw = pd.read_csv(filename_ts, header=2, index_col=0, parse_dates=True)
    time_series = ts_raw.copy()

    # extract one specific `year`
    time_series = time_series[time_series.index.year == year]
    # get time series for B and BB only
    time_series_regions = time_series.loc[
        :,
        [
            config.settings.prepare_feedin.NUTS_DE30,
            config.settings.prepare_feedin.NUTS_DE40,
        ],
    ].rename(columns=config.settings.prepare_feedin.RENAME_NUTS)

    # bring time series to oemof-B3 format with `stack_timeseries()` and `format_header()`
    ts_stacked = dp.stack_timeseries(time_series_regions).rename(
        columns={"var_name": "region"}
    )
    ts_prepared = dp.format_header(
        df=ts_stacked, header=dp.HEADER_B3_TS, index_name=TS_INDEX_NAME
    )

    # add additional information as required by template
    ts_prepared.loc[:, "var_unit"] = config.settings.prepare_feedin.TS_VAR_UNIT
    ts_prepared.loc[:, "var_name"] = f"{type}-profile"
    ts_prepared.loc[:, "source"] = config.settings.prepare_feedin.TS_SOURCE
    ts_prepared.loc[:, "comment"] = config.settings.prepare_feedin.TS_COMMENT
    ts_prepared.loc[
        :, "scenario_key"
    ] = "ALL"  # The profile is not varied in different scenarios

    return ts_prepared


def prepare_ror_time_series(filename_ts, region):
    r"""
    Prepares and formats run-of-the-river (ror) time series for region 'B' and 'BB'.

    The raw data only includes one year. This functions prepares the time series for years `YEARS`
    using the same data for each year. For leap years Feb 29th is filled with the last value of Feb
    28.

    Parameters
    ----------
    filename_ts : str
        Path including file name to ror time series of DIW Data Documentation 92
    region : str
        Region of time series; used for column 'region' in output

    Returns
    -------
    ts_df : pd.DataFrame
        Contains time series in the format of time series template of oemof-B3

    """
    # load raw time series and copy data frame
    ts_raw = pd.read_csv(filename_ts, index_col=0, skiprows=3, delimiter=";")
    # add time index
    ts_raw.index = pd.date_range("2017-01-01 00:00:00", "2017-12-31 23:00:00", freq="H")

    # prepare for all years
    ts_df = pd.DataFrame()
    for year in config.settings.prepare_feedin.YEARS:
        time_series = ts_raw.copy()
        new_index = pd.date_range(
            f"{year}-01-01 00:00:00", f"{year}-12-31 23:00:00", freq="H"
        )
        new_index_df = pd.DataFrame(index=new_index)
        leap_year = new_index_df.index.is_leap_year[0]

        # extend time series for leap years
        if leap_year == True:  # noqa: E712
            # Change datetimeindex to current `year`
            time_series.index = (
                time_series.reset_index()["index"]
                .apply(lambda x: x.replace(year=year))
                .values
            )
            # concatenate `time_series` and the new index and fill nans with value of previous day
            time_series = pd.concat(
                [time_series, new_index_df], axis=1, join="outer"
            ).fillna(method="ffill")
        else:
            # set `new_index`
            time_series.index = new_index

        # bring time series to oemof-B3 format with `stack_timeseries()` and `format_header()`
        ts_stacked = dp.stack_timeseries(time_series).rename(
            columns={"var_name": "region"}
        )
        ts_prepared = dp.format_header(
            df=ts_stacked, header=dp.HEADER_B3_TS, index_name=TS_INDEX_NAME
        )
        ts_prepared.loc[:, "scenario_key"] = "ALL"
        ts_df = pd.concat([ts_df, ts_prepared])

    # add additional information as required by template
    ts_df.loc[:, "region"] = region
    ts_df.loc[:, "var_unit"] = config.settings.prepare_feedin.TS_VAR_UNIT
    ts_df.loc[:, "var_name"] = "hydro-ror-profile"
    ts_df.loc[:, "source"] = config.settings.prepare_feedin.TS_SOURCE_ROR
    ts_df.loc[:, "comment"] = config.settings.prepare_feedin.TS_COMMENT_ROR

    return ts_df


if __name__ == "__main__":
    filename_wind = sys.argv[1]
    filename_pv = sys.argv[2]
    filename_ror = sys.argv[3]
    output_file = sys.argv[4]

    # initialize data frame
    time_series_df = pd.DataFrame()

    # prepare time series for each year
    for year in config.settings.prepare_feedin.YEARS:
        # prepare wind time series
        wind_ts = prepare_wind_and_pv_time_series(
            filename_ts=filename_wind,
            year=year,
            type="wind-onshore",
        )

        # prepare pv time series
        pv_ts = prepare_wind_and_pv_time_series(
            filename_ts=filename_pv, year=year, type="solar-pv"
        )

        # add time series to `time_series_df`
        time_series_df = pd.concat([time_series_df, wind_ts, pv_ts], axis=0)

    # prepare ror time series
    for region in config.settings.prepare_feedin.REGIONS:
        ror_ts = prepare_ror_time_series(filename_ts=filename_ror, region=region)

        # add time series to `time_series_df`
        time_series_df = pd.concat([time_series_df, ror_ts], axis=0)

    # set index
    time_series_df.reset_index(drop=True, inplace=True)
    time_series_df.index.name = TS_INDEX_NAME

    # create output directory in case it does not exist, yet and save data to `output_file`
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dp.save_df(time_series_df, output_file)
