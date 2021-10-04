import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots


def sort_by_downtime(df, epsilon=1e-6):

    _df = df.copy()

    n_nonzero = (_df >= epsilon).sum()

    n_nonzero = n_nonzero.sort_values(ascending=False)

    df_sorted = _df[n_nonzero.index]

    return df_sorted


def plot_stacked_load_duration(ax, df):
    offset = 0
    for col, series in df.iteritems():
        series += offset
        ax.axhline(offset, c="k", linewidth=0.5)
        ax.fill_between(series.index, offset, series, label=col)
        offset = series.max()

    return ax


if __name__ == "__main__":
    postprocessed = sys.argv[1]

    plotted = sys.argv[2]

    # create the directory plotted where all plots are saved
    if not os.path.exists(plotted):
        os.makedirs(plotted)

    # TODO: Do this with all electricity timeseries using a function that can be used \
    # for plot_dispatch as well.
    path_ts = os.path.join(postprocessed, "sequences", "bus", "BE-electricity.csv")

    df = pd.read_csv(path_ts, index_col=0, header=[0, 1, 2], parse_dates=True)

    # sort
    df = df.apply(sorted, 0)

    df = df.reset_index(drop=True)

    df = plots.map_labels(df)

    df = df[df.columns.drop(["El. demand", "BAT charge", "Export"])]

    fig, ax = plt.subplots(figsize=(12, 7))

    # sort by number of nonzero
    df_sorted = sort_by_downtime(df)

    # plot load duration
    plot_stacked_load_duration(ax, df_sorted)

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85])

    ax.set_xlim(0, len(df.index))

    # Put a legend below current axis
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        fancybox=True,
        ncol=4,
        fontsize=14,
    )

    fig.tight_layout()

    plt.savefig(os.path.join(plotted, "load_duration.png"))
