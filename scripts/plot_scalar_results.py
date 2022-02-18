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


class ScalarPlot:
    def __init__(self, scalars):
        self.scalars = scalars
        self.selected_scalars = None
        self.prepared_scalar_data = None

    def select_data(self, **kwargs):
        self.selected_scalars = self.scalars.copy()
        for key, value in kwargs.items():
            self.selected_scalars = dp.filter_df(self.selected_scalars, key, value)

        if self.selected_scalars.empty:
            print("No data to plot.")

        return self.selected_scalars

    def prepare_data(self):
        self.prepared_scalar_data = prepare_scalar_data(
            df=self.selected_scalars,
            colors_odict=colors_odict,
            labels_dict=labels_dict,
            conv_number=MW_TO_W,
        )

        return self.prepared_scalar_data

    def draw_plot(self, unit, title):
        fig, ax = plt.subplots()
        try:
            plot_grouped_bar(
                ax, self.prepared_scalar_data, colors_odict, unit=unit, stacked=True
            )
            ax.set_title(title)
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

            return fig, ax
        except:
            print("Could not plot.")

    def save_plot(self, output_path_plot):
        plt.savefig(output_path_plot, bbox_inches="tight")
        print(f"User info: Plot has been saved to: {output_path_plot}.")


if __name__ == "__main__":
    scalars_path = os.path.join(sys.argv[1], "scalars.csv")

    target = sys.argv[2]

    # User input
    REGIONS = ["BB", "B"]  # BE_BB
    MW_TO_W = 1e6

    # create the directory plotted where all plots are saved
    if not os.path.exists(target):
        os.makedirs(target)

    # Load scalar data
    scalars = load_scalars(scalars_path)

    # To obey flake8
    colors_odict = colors_odict

    def plot_capacity():
        var_name = "capacity"
        unit = "W"
        output_path_plot = os.path.join(target, var_name + ".png")

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, region=REGIONS)
        plot.prepare_data()
        plot.draw_plot(unit=unit, title=var_name)
        plot.save_plot(output_path_plot)

    def plot_invest_out(carrier):
        var_name = f"invest_out_{carrier}"
        unit = "W"
        output_path_plot = os.path.join(target, var_name + ".png")

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, region=REGIONS)
        plot.prepare_data()
        plot.draw_plot(unit=unit, title=var_name)
        plot.save_plot(output_path_plot)

    def plot_storage_capacity():
        var_name = "storage_capacity"
        unit = "W"
        output_path_plot = os.path.join(target, var_name + ".png")

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, region=REGIONS)
        plot.prepare_data()
        plot.draw_plot(unit=unit, title=var_name)
        plot.save_plot(output_path_plot)

    def plot_flow_out(carrier):
        title = f"production_{carrier}"
        output_path_plot = os.path.join(target, f"{title}.png")
        var_name = f"flow_out_{carrier}"
        unit = "Wh"

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, region=REGIONS)
        plot.selected_scalars = dp.filter_df(
            plot.selected_scalars,
            "type",
            ["storage", "asymmetric_storage", "link"],
            inverse=True,
        )
        plot.prepare_data()
        plot.draw_plot(unit=unit, title=title)
        plot.save_plot(output_path_plot)

    def plot_storage_out(carrier):
        title = f"storage_out_{carrier}"
        output_path_plot = os.path.join(target, f"{title}.png")
        var_name = f"flow_out_{carrier}"
        unit = "Wh"

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, region=REGIONS)
        plot.selected_scalars = dp.filter_df(
            plot.selected_scalars, "type", ["storage", "asymmetric_storage"]
        )
        plot.prepare_data()
        plot.draw_plot(unit=unit, title=title)
        plot.save_plot(output_path_plot)

    plot_capacity()
    plot_storage_capacity()
    plot_invest_out("electricity")
    plot_flow_out("electricity")
    plot_storage_out("electricity")
