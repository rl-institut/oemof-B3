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
    # read time series (raw) and time series template of oemof-B3
    ts_raw = pd.read_csv(filename_ts, header=2, index_col=0, parse_dates=True)
    template = pd.read_csv(filename_template, sep=";")
    # extract one specific `year`
    time_series = ts_raw[ts_raw.index.year == year]
    # get time series for B and BB only
    time_series = time_series[["DE30", "DE40"]].rename(
        columns={"DE30": "B", "DE40": "BB"}
    )

    # bring time series to oemof-B3 format with `stack_timeseries()`
    ts_stacked = dp.stack_timeseries(time_series).rename(columns={"var_name": "region"})
    ts_prepared = template

    # add addtional information as required by template
    ts_prepared[ts_stacked.columns] = ts_stacked
    ts_prepared["var_unit"] = "None"
    ts_prepared["id_ts"] = [0, 1]
    ts_prepared["var_name"] = f"{type}-profile"
    ts_prepared["source"] = "https://www.renewables.ninja/"
    ts_prepared["comment"] = "navigate to country, Germany"
    ts_prepared["scenario"] = "all"
    # set 'id_ts' column as index
    ts_prepared.set_index("id_ts", inplace=True)

    return ts_prepared


if __name__ == "__main__":
    filename_wind = sys.argv[1]
    filename_pv = sys.argv[2]
    template = sys.argv[3]
    output_file = sys.argv[4]

    year = 2012  # todo read from scalars

    # prepare wind time series
    wind_ts = prepare_time_series(
        filename_ts=filename_wind, filename_template=template, year=year, type="wind"
    )

    # pepare pv time series
    pv_ts = prepare_time_series(
        filename_ts=filename_pv, filename_template=template, year=year, type="pv"
    )

    # join time series and save to `output_file`
    time_series = pd.concat([wind_ts, pv_ts], axis=0)
    time_series.index = [0, 1, 2, 3]

    # create output directory in case it does not exist, yet and save data to `output_file`
    output_dir = "/".join(output_file.split("/")[0:-1])
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dp.save_df(time_series, output_file)
