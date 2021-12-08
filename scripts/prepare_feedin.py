# coding: utf-8
r"""
Inputs
-------
filename_wind : str
    ``raw/time_series/ninja_wind_country_DE_current_merra-2_nuts-2_corrected.csv``: Path incl. file
    name to wind feed-in time series of renewables ninja
filename_pv : str
    ``raw/time_series/ninja_pv_country_DE_merra-2_nuts-2_corrected.csv``: Path incl. file name to pv
    feed-in time series of renewables ninja
filename_for : str
    ``raw/time_series/DIW_Hydro_availability.csv``:
output_file : str
    ``results/_resources/feedin_time_series.csv``:

Outputs
---------
output_file : str
    Path incl. file name to output: wind and pv feed-in time series

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

# global variables
# specific to wind and pv time series
RE_NINJA_YEARS = list(
    range(2010, 2020)
)  # re ninja wind+pv time series are prepared for these years
NUTS_DE30 = "DE30"
NUTS_DE40 = "DE40"
RENAME_NUTS = {NUTS_DE30: "B", NUTS_DE40: "BB"}
TS_VAR_UNIT = "None"
TS_SOURCE = "https://www.renewables.ninja/"
TS_COMMENT = "navigate to country Germany"
# specific to ror time series
REGIONS = ["BB", "B"]
TS_SOURCE_ROR = "https://zenodo.org/record/1044463"
TS_COMMENT_ROR = "Isolated ror availability time series from DIW data"
YEAR_ROR = 2017


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
    time_series_regions = time_series.loc[:, [NUTS_DE30, NUTS_DE40]].rename(
        columns=RENAME_NUTS
    )

    # bring time series to oemof-B3 format with `stack_timeseries()` and `format_header()`
    ts_stacked = dp.stack_timeseries(time_series_regions).rename(
        columns={"var_name": "region"}
    )
    ts_prepared = dp.format_header(
        df=ts_stacked, header=dp.HEADER_B3_TS, index_name="id_ts"
    )

    # add additional information as required by template
    ts_prepared.loc[:, "var_unit"] = TS_VAR_UNIT
    ts_prepared.loc[:, "var_name"] = f"{type}-profile"
    ts_prepared.loc[:, "source"] = TS_SOURCE
    ts_prepared.loc[:, "comment"] = TS_COMMENT
    ts_prepared.loc[:, "scenario"] = f"ts_{year}"

    return ts_prepared


def prepare_ror_time_series(filename_ts, region):
    r"""
    Prepares and formats run-of-the-river (ror) time series for region 'B' and 'BB'.

    Parameters
    ----------
    filename_ts : str
        Path including file name to ror time series of DIW Data Documentation 92
    region : str
        Region of time series; used for column 'region' in output

    Returns
    -------
    ts_prepared : pd.DataFrame
        Contains time series in the format of time series template of oemof-B3

    """
    # load raw time series and copy data frame
    ts_raw = pd.read_csv(filename_ts, index_col=0, skiprows=3, delimiter=";")
    time_series = ts_raw.copy()

    time_series.index = pd.date_range(
        f"{YEAR_ROR}-01-01 00:00:00", f"{YEAR_ROR}-12-31 23:00:00", 8760
    )
    # bring time series to oemof-B3 format with `stack_timeseries()` and `format_header()`
    ts_stacked = dp.stack_timeseries(time_series).rename(columns={"var_name": "region"})
    ts_prepared = dp.format_header(
        df=ts_stacked, header=dp.HEADER_B3_TS, index_name="id_ts"
    )

    # add additional information as required by template
    ts_prepared.loc[:, "region"] = region
    ts_prepared.loc[:, "var_unit"] = TS_VAR_UNIT
    ts_prepared.loc[:, "var_name"] = "ror-profile"
    ts_prepared.loc[:, "source"] = TS_SOURCE_ROR
    ts_prepared.loc[:, "comment"] = TS_COMMENT_ROR
    ts_prepared.loc[:, "scenario"] = f"ts_{YEAR_ROR}"

    return ts_prepared


if __name__ == "__main__":
    filename_wind = sys.argv[1]
    filename_pv = sys.argv[2]
    filename_ror = sys.argv[3]
    output_file = sys.argv[4]

    # initialize data frame
    time_series_df = pd.DataFrame()

    # prepare time series for each year
    for year in RE_NINJA_YEARS:
        # prepare wind time series
        wind_ts = prepare_wind_and_pv_time_series(
            filename_ts=filename_wind,
            year=year,
            type="wind",
        )

        # prepare pv time series
        pv_ts = prepare_wind_and_pv_time_series(
            filename_ts=filename_pv, year=year, type="pv"
        )

        # add time series to `time_series_df`
        time_series_df = pd.concat([time_series_df, wind_ts, pv_ts], axis=0)

    # prepare ror time series
    for region in REGIONS:
        ror_ts = prepare_ror_time_series(filename_ts=filename_ror, region=region)

        # add time series to `time_series_df`
        time_series_df = pd.concat([time_series_df, ror_ts], axis=0)

    # set index
    time_series_df.reset_index(drop=True, inplace=True)
    time_series_df.index.name = "id_ts"

    # create output directory in case it does not exist, yet and save data to `output_file`
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dp.save_df(time_series_df, output_file)
