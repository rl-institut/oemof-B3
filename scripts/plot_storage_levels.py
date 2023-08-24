# coding: utf-8
r"""
Inputs
-------
postprocessed : str
    ``results/{scenario}/postprocessed/``: path to directory which contains the input data which
    can be plotted
plotted : str
    ``results/{scenario}/plotted/storage_levels/``: path where a new directory is created and
    the plots are saved
logfile : str
    ``results/{scenario}/{scenario}.log``: path to logfile

Outputs
---------
Static storage level plots.

Description
-------------
The script creates storage level plots.

The static plots with a file format defined by the *plot_filetype* variable in
``oemof_b3/config/settings.yaml`` and the interactive plotly plots as html-files
in a new directory called storage_levels within directory plotted.
Timeframes and the carrier for the plot can be chosen.
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots
import matplotlib.dates as mdates

from oemof_b3.config import config
from oemof_b3.config.config import LABELS, COLORS
from oemof_b3.tools import data_processing as dp


def reduce_labels(ax, simple_labels_dict):
    """
    Replaces two labels by one as defined in a dictionary.

    Parameters
    ----------
    ax: matplotlib.axes
        The axes containing the plot for which the labels shall be simplified
    simple_labels_dict:
        dictionary which contains the simplified label as a key
        and for every key a list of two labels
        which shall be replaced by the simplified label as value

    Returns
    -------

    """
    handles, labels = ax.get_legend_handles_labels()

    for key, value in simple_labels_dict.items():
        if value[0] in labels and value[1] in labels:
            labels = [
                key if item == value[0] else "_Hidden" if item == value[1] else item
                for item in labels
            ]
    return handles, labels


def get_component_from_tuple(tuple):
    # Dummy implementation because for this application, component is always first in tuple.
    return tuple[0]


def get_region_carrier_tech_from_component_name(component_name):
    DELIMITER = "-"

    region, carrier, tech = component_name.split(DELIMITER)

    return region, carrier, tech


def results_ts_to_oemof_b3(df):
    _df = df.copy()

    _df.columns = df.columns.droplevel(2).map(get_component_from_tuple)

    _df = dp.stack_timeseries(_df)

    _df["region"], carrier, tech = zip(
        *_df["var_name"].map(get_region_carrier_tech_from_component_name)
    )

    _df["var_name"] = ["-".join([c, t]) for c, t in zip(carrier, tech)]

    return _df


def normalize_to_max(ts):
    max = ts.max()
    ts_norm = ts / max
    return ts_norm


def multiplot_df(df, figsize=None, sharex=True, colors=None, **kwargs):
    n_cols = len(df.columns)

    fig, axs = plt.subplots(n_cols, 1, figsize=figsize, sharex=sharex)

    if colors:
        assert all(name_col in colors for name_col in df.columns)

    for ax, (name_col, series) in zip(axs, df.iteritems()):

        ax.plot(series, color=colors[name_col], **kwargs)

        ax.set_ylabel(name_col, rotation=0, ha="right")

    return fig, axs


if __name__ == "__main__":
    postprocessed = sys.argv[1]
    plotted = sys.argv[2]

    logger = config.add_snake_logger("plot_storage_levels")

    # create the directory plotted where all plots are saved
    if not os.path.exists(plotted):
        os.makedirs(plotted)

    STORAGE_LEVEL_FILE = os.path.join(
        postprocessed, "sequences/by_variable/storage_content.csv"
    )
    MW_to_W = 1e6

    data = pd.read_csv(
        STORAGE_LEVEL_FILE, header=[0, 1, 2], parse_dates=[0], index_col=[0], delimiter=';'
    )

    # select carrier
    carriers = ["electricity", "heat_central", "heat_decentral"]

    # convert data to SI-unit
    data = data * MW_to_W

    # prepare data

    # static storage level plot
    # plot one winter and one summer month and the whole year
    # select timeframe
    year = data.index[0].year
    timeframe = [
        (f"{year}-01-01 00:00:00", f"{year}-01-31 23:00:00"),
        (f"{year}-07-01 00:00:00", f"{year}-07-31 23:00:00"),
        (f"{year}-01-01 00:00:00", f"{year}-12-31 23:00:00"),
    ]

    # aggregate time series
    data = results_ts_to_oemof_b3(data)

    data = dp.aggregate_timeseries(data, "region")

    data = dp.unstack_timeseries(data)

    data = normalize_to_max(data)

    # relabel data
    data = plots.map_labels(data, LABELS)

    for start_date, end_date in timeframe:

        # filter timeseries
        df_time_filtered = plots.filter_timeseries(data, start_date, end_date)

        if df_time_filtered.empty:
            logger.warning(f"Data in '{STORAGE_LEVEL_FILE}' is empty, cannot plot.")

        plt.rcParams.update({"font.size": 14})

        fig, axs = multiplot_df(
            df_time_filtered, figsize=(9, 5), linewidth=1, colors=COLORS
        )

        plt.subplots_adjust(hspace=0.1)

        plt.xlabel("Date", fontdict={"size": 17})

        # format x-axis representing the dates
        ax = axs[-1]
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        file_name = (
            "storage_level"
            + "_"
            + start_date[5:7]
            + end_date[5:7]
            + config.settings.general.plot_filetype
        )
        plt.savefig(os.path.join(plotted, file_name), bbox_inches="tight")
