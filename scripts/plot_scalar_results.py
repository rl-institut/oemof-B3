# coding: utf-8
r"""
Inputs
-------
scalars_path : str
    ``results/{scenario}/postprocessed/``: path to directory containing postprocessed results.
target : str
    ``results/{scenario}/plotted/scalars/``: path where a new directory is
    created and the plots are saved.

Outputs
---------
.png
    plots in .png format.

Description
-------------
The result scalars of all scenarios are plotted in a single plot.
"""
import os
import sys

import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots
import pandas as pd
from oemoflex.tools.plots import plot_grouped_bar

from oemof_b3.tools import data_processing as dp
from oemof_b3 import colors_odict, labels_dict


def prepare_scalar_data(df, colors_odict, labels_dict, conv_number):
    # pivot
    df_pivot = pd.pivot_table(
        df, index=["scenario", "region"], columns="name", values="var_value"
    )

    # rename and aggregate duplicated columns
    df_pivot = plots.map_labels(df_pivot, labels_dict)
    df_pivot = df_pivot.groupby(level=0, axis=1).sum()

    # define ordering and use concrete_order as keys for colors_odict in plot_scalars()
    concrete_order = list(
        label for label in colors_odict.keys() if label in df_pivot.columns
    )
    df_pivot = df_pivot[concrete_order]

    # convert data to SI-Units
    if conv_number is not None:
        df_pivot *= conv_number

    return df_pivot


def load_scalars(path):
    df = pd.read_csv(path, sep=",", index_col=0)
    return df


if __name__ == "__main__":
    scalars_path = os.path.join(sys.argv[1], "scalars.csv")

    target = sys.argv[2]

    # User input
    REGIONS = ["BB", "B"]  # BE_BB
    MW_TO_W = 1e6
    VAR_NAMES = [
        "capacity",
        "flow_out_electricity",
        "invest_out_electricity",
        "flow_out_heat_central",
        "invest_out_heat_central",
        "flow_out_heat_decentral",
        "invest_out_heat_decentral",
    ]
    UNITS = {
        "capacity": "W",
        "flow_out_electricity": "Wh",
        "invest_out_electricity": "W",
        "flow_out_heat_central": "Wh",
        "invest_out_heat_central": "W",
        "flow_out_heat_decentral": "Wh",
        "invest_out_heat_decentral": "W",
    }

    # create the directory plotted where all plots are saved
    if not os.path.exists(target):
        os.makedirs(target)

    # Load scalar data
    scalars = load_scalars(scalars_path)

    # To obey flake8
    colors_odict = colors_odict

    for var_name in VAR_NAMES:

        # select data with chosen var_name
        selected_scalar_data = dp.filter_df(scalars, "var_name", var_name)
        selected_scalar_data = dp.filter_df(selected_scalar_data, "region", REGIONS)

        if selected_scalar_data.empty:
            print(f"No data to plot for '{var_name}'.")
            continue

        # prepare data
        prepared_scalar_data = prepare_scalar_data(
            df=selected_scalar_data,
            colors_odict=colors_odict,
            labels_dict=labels_dict,
            conv_number=MW_TO_W,
        )

        # plot data
        fig, ax = plt.subplots()
        plot_grouped_bar(
            ax, prepared_scalar_data, colors_odict, unit=UNITS[var_name], stacked=True
        )
        ax.set_title(var_name)
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
        )
        # Put a legend below current axis
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.1),
            fancybox=True,
            ncol=4,
            fontsize=14,
        )
        output_path_plot = os.path.join(target, var_name + ".png")
        plt.savefig(output_path_plot, bbox_inches="tight")
        print(f"User info: Plot of '{var_name}' has been saved to: {output_path_plot}.")
