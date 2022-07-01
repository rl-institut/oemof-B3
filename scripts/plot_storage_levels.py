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
    ``logs/{scenario}.log``: path to logfile

Outputs
---------
.pdf
    dispatch plot in pdf-format.
.png
    dispatch plot in png-format.
.html
    interactive plotly dispatch plot in html-format.

Description
-------------
The script creates storage level plots.

The static plots are saved as pdf-files and the interactive plotly plots as html-files
in a new directory called plotted.
Timeframes and the carrier for the plot can be chosen.
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots
import matplotlib.dates as mdates

from oemof_b3.config import config


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


if __name__ == "__main__":
    postprocessed = sys.argv[1]
    plotted = sys.argv[2]
    logfile = sys.argv[3]

    logger = config.add_snake_logger(logfile, "plot_storage_levels")

    # create the directory plotted where all plots are saved
    if not os.path.exists(plotted):
        os.makedirs(plotted)

    STORAGE_LEVEL_FILE = os.path.join(
        postprocessed, "sequences/by_variable/storage_content.csv"
    )
    MW_to_W = 1e6
    IMAGETYPE = ".png"

    data = pd.read_csv(
        STORAGE_LEVEL_FILE, header=[0, 1, 2], parse_dates=[0], index_col=[0]
    )

    # select carrier
    carriers = ["electricity", "heat_central", "heat_decentral"]

    # convert data to SI-unit

    data = data * MW_to_W

    # prepare data

    # static dispatch plot
    # plot one winter and one summer month and the whole year
    # select timeframe
    year = data.index[0].year
    timeframe = [
        (f"{year}-01-01 00:00:00", f"{year}-01-31 23:00:00"),
        (f"{year}-07-01 00:00:00", f"{year}-07-31 23:00:00"),
        (f"{year}-01-01 00:00:00", f"{year}-12-31 23:00:00"),
    ]

    for start_date, end_date in timeframe:
        fig, ax = plt.subplots(figsize=(12, 5))

        # filter timeseries
        df_time_filtered = plots.filter_timeseries(data, start_date, end_date)

        if df_time_filtered.empty:
            logger.warning(f"Data in '{STORAGE_LEVEL_FILE}' is empty, cannot plot.")

        # plot time filtered data
        df_time_filtered.plot()

        plt.grid()
        plt.xlabel("Date", fontdict={"size": 17})
        plt.ylabel("Storage level", fontdict={"size": 17})
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        # format x-axis representing the dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
        )

        # # Put a legend below current axis
        plt.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.15),
            fancybox=True,
            ncol=1,
            fontsize=14,
        )

        fig.tight_layout()
        file_name = "storage_level" + "_" + start_date[5:7] + end_date[5:7] + IMAGETYPE
        plt.savefig(os.path.join(plotted, file_name), bbox_inches="tight")
