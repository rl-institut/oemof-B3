# coding: utf-8
r"""
Inputs
-------
opsd_ts_data : str
    raw opsd timeseries data including electricty load as .csv
output_file : str
    ``results/_resources/ts_load_electricity.csv``: path of output file with prepared
    data as .csv

Outputs
---------
pandas.DataFrame
    with normalized load data of 50 Hertz region in Germany from the years 2015, 2016, 2017, 2018
    and 2019. The data is normalized with the total electricity demand of the corresponding year.

Description
-------------
The corresponding snakemake rule of the preparation of the electricity demand profile
downloads the 60 min timeseries data from OPSD and keeps it locally.
The script takes this data and filters for the load data of the 50 Hertz region in Germany.
The load data is normalized with the total electricity demand of the corresponding year and put
into the timeseries template format. The years 2015 to 2019 (including) are available.
"""

import sys
import pandas as pd
import os
import oemof_b3.tools.data_processing as dp


# global variables
OPSD_YEARS = list(
    range(2015, 2020)
)  # opsd load time series are prepared for these years
REGIONS = ["BB", "B"]
TS_VAR_UNIT = "None"
TS_SOURCE = "https://data.open-power-system-data.org/time_series/2020-10-06"
TS_COMMENT = "DE_50hertz actual load data"
COL_SELECT = "DE_50hertz_load_actual_entsoe_transparency"


def prepare_load_profile_time_series(ts_raw, year, region):
    r"""
    Prepares and formats time series of load for region 'B' and 'BB'.
    The load profile is normalized with the total energy demand of a year.

    Parameters
    ----------
    ts_raw : pd.DataFrame
        Contains actual load data from 50hertz region from opsd load data
    year : int
        Year for which time series is extracted from raw data in `ts_raw`
    region : str
        Region of time series; used for column 'region' in output

    Returns
    -------
    ts_prepared : pd.DataFrame
        Contains time series in the format of timeseries template.

    """
    # copy data frame
    time_series = ts_raw.copy()

    # extract one specific `year`
    time_series = time_series[time_series.index.year == year]

    # normalize with total electricity demand in year
    time_series.iloc[:, 0] = time_series.iloc[:, 0] / time_series.iloc[:, 0].sum()

    # bring time series to oemof-B3 format with `stack_timeseries()` and `format_header()`
    ts_stacked = dp.stack_timeseries(time_series).rename(columns={"var_name": "region"})
    ts_prepared = dp.format_header(
        df=ts_stacked, header=dp.HEADER_B3_TS, index_name="id_ts"
    )

    # add additional information as required by template
    ts_prepared.loc[:, "region"] = region
    ts_prepared.loc[:, "var_unit"] = TS_VAR_UNIT
    ts_prepared.loc[:, "var_name"] = "load-profile"
    ts_prepared.loc[:, "source"] = TS_SOURCE
    ts_prepared.loc[:, "comment"] = TS_COMMENT
    ts_prepared.loc[:, "scenario"] = f"ts_{year}"

    return ts_prepared


if __name__ == "__main__":
    opsd_ts_data = sys.argv[1]
    output_file = sys.argv[2]

    # initialize data frame
    time_series_df = pd.DataFrame()

    # download raw time series from OPSD
    ts_raw = pd.read_csv(opsd_ts_data, index_col=0)
    ts_raw.index = pd.to_datetime(ts_raw.index, utc=True)
    # filter for 50hertz actual load
    ts_raw = ts_raw[[COL_SELECT]]

    # prepare time series for each year and region
    for year in OPSD_YEARS:
        for region in REGIONS:
            # prepare opsd 50hertz actual load time series
            load_ts = prepare_load_profile_time_series(
                ts_raw=ts_raw, year=year, region=region
            )

            # add time series to `time_series_df`
            time_series_df = pd.concat([time_series_df, load_ts], axis=0)

    # set index
    time_series_df.reset_index(drop=True, inplace=True)
    time_series_df.index.name = "id_ts"

    # create output directory in case it does not exist, yet and save data to `output_file`
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dp.save_df(time_series_df, output_file)
