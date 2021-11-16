import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots
from oemof_b3 import labels_dict, colors_odict


def sort_by_downtime(df, epsilon=1e-6):

    _df = df.copy()

    n_nonzero = (_df >= epsilon).sum()

    n_nonzero = n_nonzero.sort_values(ascending=False)

    df_sorted = _df[n_nonzero.index]

    return df_sorted


def plot_stacked_load_duration(ax, df, colors_dict=None):
    def stacked_plot(df):

        offset = 0
        for col, series in df.iteritems():
            series += offset

            ax.axhline(offset, c="k", linewidth=0.5)

            if colors_dict:
                ax.fill_between(
                    series.index, offset, series, label=col, color=colors_dict[col]
                )
            else:
                ax.fill_between(series.index, offset, series, label=col)

            offset = series.loc[abs(series).idxmax()]

    df_pos = df.loc[:, (df > 0).any()]
    df_neg = df.loc[:, (df < 0).any()]

    stacked_plot(df_pos)
    stacked_plot(df_neg)

    return ax


if __name__ == "__main__":
    postprocessed = sys.argv[1]

    plotted = sys.argv[2]

    # create the directory plotted where all plots are saved
    if not os.path.exists(plotted):
        os.makedirs(plotted)

    # TODO: Do this with all electricity timeseries using a function that can be used \
    # for plot_dispatch as well.

    bus_directory = os.path.join(postprocessed, "sequences/bus/")

    bus_files = os.listdir(bus_directory)

    carriers = ["electricity", "heat_central", "heat_decentral"]

    selected_bus_files = [
        file for file in bus_files for carrier in carriers if carrier in file
    ]

    for bus_file in selected_bus_files:

        bus_name = os.path.splitext(bus_file)[0]

        path_ts = os.path.join(bus_directory, bus_file)

        df = pd.read_csv(path_ts, index_col=0, header=[0, 1, 2], parse_dates=True)

        # sort
        df = df.apply(sorted, 0)

        df = df.reset_index(drop=True)

        df = df.iloc[::-1]

        df = df.reset_index(drop=True)

        df, df_demand = plots.prepare_dispatch_data(
            df, bus_name, "demand", labels_dict=labels_dict
        )

        fig, ax = plt.subplots(figsize=(12, 7))

        # sort by number of nonzero
        df_sorted = sort_by_downtime(df)

        # plot load duration
        plot_stacked_load_duration(ax, df_sorted, colors_dict=colors_odict)

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
        )

        ax.set_xlim(0, len(df.index))

        # Put a legend below current axis
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.1),
            fancybox=True,
            ncol=4,
            fontsize=14,
        )

        plt.savefig(os.path.join(plotted, bus_name + ".png"))
