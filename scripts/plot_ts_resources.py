import os
import sys

import matplotlib.pyplot as plt

import oemof_b3.tools.data_processing as dp


if __name__ == "__main__":
    resources = sys.argv[1]
    scalars = sys.argv[2]
    output_path = sys.argv[3]

    logfile = sys.argv[4]

    logger = add_snake_logger(logfile, "plot_storage_levels")

    REGION = "B"
    TIMEINDEX_START = "2015-01-01 00:00:00"
    H_PER_DAY = 24
    DAYS = 14

    # Load all timeseries resources that has "load" in its nam
    paths = [
        os.path.join(input_path, path)
        for path in os.listdir(input_path)
        if "ts_load" in os.path.basename(path)
    ]

    ts = dp.multi_load_b3_timeseries(paths)

    # Filter timeseries
    ts = dp.filter_df(ts, "region", REGION)

    ts = dp.filter_df(ts, "timeindex_start", TIMEINDEX_START)

    ts = dp.unstack_timeseries(ts)

    # Plot
    n_cols = ts.shape[1]
    fig, axs = plt.subplots(n_cols, 1, figsize=(8, 12))
    for i, col in enumerate(ts.columns):
        ts.iloc[: H_PER_DAY * DAYS, i].plot(ax=axs[i])
        axs[i].set_ylabel(col)
    plt.savefig(output_path)
