# coding: utf-8
r"""
Inputs
-------
filename_wind : str
    Path incl. file name to wind feed-in time series of renewables ninja
filename_pv : str
    Path incl. file name to pv feed-in time series of renewables ninja
template : str
    Path incl. file name to time series template of oemof-B3

Outputs
---------
output_file : str
    Path incl. file name to output: wind and pv feed-in time series

Description
-------------
This script prepares wind and pv feed-in time series for the regions Berlin and Brandenburg. Raw
data is read from csvs from https://www.renewables.ninja/ and then formatted to fit the time series
template for oemof-B3.

"""

# todo  ROR could be included here

import sys
import pandas as pd
import os
import oemof_b3.tools.data_processing as dp

# global variables
RE_NINJA_YEARS = list(
    range(2010, 2020)
)  # re ninja wind+pv time series are prepared for these years
NUTS_DE30 = "DE30"
NUTS_DE40 = "DE40"
RENAME_NUTS = {NUTS_DE30: "B", NUTS_DE40: "BB"}
TS_VAR_UNIT = "None"
TS_SOURCE = "https://www.renewables.ninja/"
TS_COMMENT = "navigate to country Germany"


def prepare_time_series(filename_ts, filename_template, year, type):
    r"""
    Prepares and formats time series of `type` 'wind' or 'pv' for region 'B' and 'BB'.

    Parameters
    ----------
    filename_ts : str
        Path including file name to
    filename_template : str
        Path including file name to template of time series format
    year : int
        Year for which time series is extracted from raw data in `filename_ts`
    type : str
        Type of time series like 'wind' or 'pv'; used for column 'var_name' in output

    Returns
    -------
    ts_prepared : pd.DataFrame
        Contains time series in the format of template in `filename_template`

    """
    # load raw time series
    ts_raw = pd.read_csv(filename_ts, header=2, index_col=0, parse_dates=True)

    # extract one specific `year`
    time_series = ts_raw[ts_raw.index.year == year]
    # get time series for B and BB only
    time_series = time_series[[NUTS_DE30, NUTS_DE40]].rename(columns=RENAME_NUTS)

    # bring time series to oemof-B3 format with `stack_timeseries()` and `format_header()`
    ts_stacked = dp.stack_timeseries(time_series).rename(columns={"var_name": "region"})
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


if __name__ == "__main__":
    filename_wind = sys.argv[1]
    filename_pv = sys.argv[2]
    template = sys.argv[3]
    output_file = sys.argv[4]

    # initialize data frame
    time_series_df = pd.DataFrame()

    # prepare time series for each year
    for year in RE_NINJA_YEARS:
        # prepare wind time series
        wind_ts = prepare_time_series(
            filename_ts=filename_wind,
            filename_template=template,
            year=year,
            type="wind",
        )

        # prepare pv time series
        pv_ts = prepare_time_series(
            filename_ts=filename_pv, filename_template=template, year=year, type="pv"
        )

        # add time series to `time_series_df`
        time_series_df = pd.concat([time_series_df, wind_ts, pv_ts], axis=0)

    # set index
    time_series_df.index = range(0, len(time_series_df))

    # create output directory in case it does not exist, yet and save data to `output_file`
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dp.save_df(time_series_df, output_file)
