# coding: utf-8
r"""
Inputs
-------
scalars_path : str
    ``results/{scenario}/postprocessed/``: path to directory containing postprocessed results.
target : str
    ``results/{scenario}/plotted/scalars/``: path where a new directory is
    created and the plots are saved.
logfile : str
    ``logs/{scenario}.log``: path to logfile

Outputs
---------
.png
    plots in .png format.

Description
-------------
The result scalars of all scenarios are plotted in a single plot.
"""
import logging
import os
import sys

import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots
import pandas as pd
from oemoflex.tools.plots import plot_grouped_bar

from oemof_b3.tools import data_processing as dp
from oemof_b3 import colors_odict, labels_dict
from oemof_b3.config import config


logger = logging.getLogger()


def aggregate_regions(df):
    # this is a work-around to use the dataprocessing function for postprocessed data,
    # which is in a similar but not in the same format as preprocessed oemof_b3 resources.
    _df = df.copy()
    _df.reset_index(inplace=True)
    _df = _df.rename(columns={"scenario": "scenario_key"})
    _df = dp.aggregate_scalars(_df, "region")
    _df = _df.rename(columns={"scenario_key": "scenario"})
    _df["name"] = _df.apply(lambda x: x["carrier"] + "-" + x["tech"], 1)
    _df = _df.set_index("scenario")
    return _df


def prepare_scalar_data(df, colors_odict, labels_dict, conv_number):
    # pivot
    df_pivot = pd.pivot_table(
        df, index=["scenario", "region", "var_name"], columns="name", values="var_value"
    )

    # rename and aggregate duplicated columns
    df_pivot = plots.map_labels(df_pivot, labels_dict)
    df_pivot = df_pivot.groupby(level=0, axis=1).sum()

    # define ordering and use concrete_order as keys for colors_odict in plot_scalars
    def sort_by_ranking(to_sort, order):
        ranking = {key: i for i, key in enumerate(order)}
        try:
            concrete_order = [ranking[key] for key in to_sort]
        except KeyError as e:
            raise KeyError(f"Missing label for label {e}")

        sorted_list = [x for _, x in sorted(zip(concrete_order, to_sort))]

        return sorted_list

    sorted_labels = sort_by_ranking(df_pivot.columns, colors_odict)

    df_pivot = df_pivot[sorted_labels]

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
        self.plotted = False

    def select_data(self, **kwargs):
        self.selected_scalars = self.scalars.copy()
        for key, value in kwargs.items():
            self.selected_scalars = dp.filter_df(self.selected_scalars, key, value)

        if self.selected_scalars.empty:
            logger.info("No data to plot.")

        return self.selected_scalars

    def prepare_data(self, agg_regions=False):

        self.prepared_scalar_data = self.selected_scalars.copy()

        if agg_regions:
            self.prepared_scalar_data = aggregate_regions(self.prepared_scalar_data)

        self.prepared_scalar_data = prepare_scalar_data(
            df=self.prepared_scalar_data,
            colors_odict=colors_odict,
            labels_dict=labels_dict,
            conv_number=MW_TO_W,
        )

        return self.prepared_scalar_data

    def draw_plot(self, unit, title):
        # do not plot if the data is empty or all zeros.
        if (
            self.prepared_scalar_data.empty
            or (self.prepared_scalar_data == 0).all().all()
        ):
            logger.warning("Data is empty or all zero")
            return None, None

        fig, ax = plt.subplots()
        plot_grouped_bar(
            ax, self.prepared_scalar_data, colors_odict, unit=unit, stacked=True
        )
        ax.set_title(title)
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
        )
        set_hierarchical_xlabels(self.prepared_scalar_data.index)
        # Put a legend below current axis
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.18),
            fancybox=True,
            ncol=4,
            fontsize=14,
        )

        self.plotted = True

        return fig, ax

    def save_plot(self, output_path_plot):
        if self.plotted:
            plt.savefig(output_path_plot, bbox_inches="tight")
            logger.info(f"Plot has been saved to: {output_path_plot}.")


def set_hierarchical_xlabels(
    index,
    ax=None,
    hlines=False,
    bar_xmargin=0.1,
    bar_yinterval=0.1,
    rotation=0,
    ha=None,
):
    r"""
    adapted from https://linuxtut.com/ 'Draw hierarchical axis labels with matplotlib + pandas'
    """
    from itertools import groupby
    from matplotlib.lines import Line2D

    ax = ax or plt.gca()

    assert isinstance(index, pd.MultiIndex)
    labels = ax.set_xticklabels([s for *_, s in index])

    if rotation != 0:
        for lb in labels:
            lb.set_rotation(rotation)
            lb.set_ha(ha)

    transform = ax.get_xaxis_transform()

    n_levels = index.nlevels
    n_intervals = len(index.codes) - 1
    if isinstance(bar_yinterval, (float, int)):
        bar_yinterval = [bar_yinterval] * n_intervals

    elif len(bar_yinterval) != n_intervals:
        raise ValueError("Wrong length for bar_yinterval. Must be either 1 or ")

    for i in range(1, n_levels):
        bar_ypos = -sum(bar_yinterval[:i])
        xpos0 = -0.5  # Coordinates on the left side of the target group

        for (*_, code), codes_iter in groupby(zip(*index.codes[:-i])):
            xpos1 = xpos0 + sum(
                1 for _ in codes_iter
            )  # Coordinates on the right side of the target group
            ax.text(
                (xpos0 + xpos1) / 2,
                bar_ypos - 0.02,
                index.levels[-i - 1][code],
                transform=transform,
                ha="center",
                va="top",
            )
            if hlines:
                ax.add_line(
                    Line2D(
                        [xpos0 + bar_xmargin, xpos1 - bar_xmargin],
                        [bar_ypos],
                        transform=transform,
                        color="k",
                        clip_on=False,
                    )
                )
            xpos0 = xpos1


if __name__ == "__main__":
    scalars_path = os.path.join(sys.argv[1], "scalars.csv")
    target = sys.argv[2]
    logfile = sys.argv[3]

    logger = config.add_snake_logger(logfile, "plot_scalar_results")

    # User input
    CARRIERS = ["electricity", "heat_central", "heat_decentral", "h2"]
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
        plot.select_data(var_name=var_name)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.draw_plot(unit=unit, title=var_name)
        plot.save_plot(output_path_plot)

    def plot_invest_out(carrier):
        var_name = f"invest_out_{carrier}"
        unit = "W"
        output_path_plot = os.path.join(target, var_name + ".png")

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.draw_plot(unit=unit, title=var_name)
        plot.save_plot(output_path_plot)

    def plot_storage_capacity(carrier):
        title = f"storage_capacity_{carrier}"
        output_path_plot = os.path.join(target, title + ".png")
        var_name = "storage_capacity"
        unit = "Wh"

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, carrier=carrier)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.draw_plot(unit=unit, title=title)
        plot.save_plot(output_path_plot)

    def plot_storage_invest(carrier):
        title = f"storage_invest_{carrier}"
        output_path_plot = os.path.join(target, f"{title}.png")
        var_name = "invest"
        unit = "Wh"

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, carrier=carrier)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.draw_plot(unit=unit, title=title)
        plot.save_plot(output_path_plot)

    def plot_flow_out(carrier):
        title = f"production_{carrier}"
        output_path_plot = os.path.join(target, f"{title}.png")
        var_name = f"flow_out_{carrier}"
        unit = "Wh"

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.selected_scalars = dp.filter_df(
            plot.selected_scalars,
            "type",
            ["storage", "asymmetric_storage", "link"],
            inverse=True,
        )
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.draw_plot(unit=unit, title=title)
        plot.save_plot(output_path_plot)

    def plot_storage_out(carrier):
        title = f"storage_out_{carrier}"
        output_path_plot = os.path.join(target, f"{title}.png")
        var_name = f"flow_out_{carrier}"
        unit = "Wh"

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.selected_scalars = dp.filter_df(
            plot.selected_scalars, "type", ["storage", "asymmetric_storage"]
        )
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.draw_plot(unit=unit, title=title)
        plot.save_plot(output_path_plot)

    def plot_invest_out_multi_carrier(carriers):
        var_name = [f"invest_out_{carrier}" for carrier in carriers]
        unit = "W"
        output_path_plot = os.path.join(
            target, "invest_out_" + "_".join(carriers) + ".png"
        )
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.selected_scalars.replace({"invest_out_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        fig, ax = plot.draw_plot(unit=unit, title=var_name)

        try:
            # rotate hierarchical labels
            ax.texts.clear()
            set_hierarchical_xlabels(
                plot.prepared_scalar_data.index,
                ax=ax,
                bar_yinterval=0.2,
                rotation=20,
                ha="right",
            )

            # Move the legend below current axis
            ax.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.42),
                fancybox=True,
                ncol=4,
                fontsize=14,
            )
            ax.set_title("invest_out " + " ".join(carriers))

            plot.save_plot(output_path_plot)

        except:  # noqa 722
            logger.warning("Could not plot.")

    def plot_flow_out_multi_carrier(carriers):
        var_name = [f"flow_out_{carrier}" for carrier in carriers]
        unit = "Wh"
        output_path_plot = os.path.join(
            target, "flow_out_" + "_".join(carriers) + ".png"
        )
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.selected_scalars.replace({"flow_out_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        fig, ax = plot.draw_plot(unit=unit, title=var_name)

        try:
            # rotate hierarchical labels
            ax.texts.clear()
            set_hierarchical_xlabels(
                plot.prepared_scalar_data.index,
                ax=ax,
                bar_yinterval=0.2,
                rotation=20,
                ha="right",
            )

            # Move the legend below current axis
            ax.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.42),
                fancybox=True,
                ncol=4,
                fontsize=14,
            )
            ax.set_title("flow_out " + " ".join(carriers))

            plot.save_plot(output_path_plot)
        except:  # noqa 722
            logger.warning("Could not plot.")

    def plot_demands(carriers):
        var_name = [f"flow_in_{carrier}" for carrier in carriers]
        tech = "demand"
        unit = "Wh"
        output_path_plot = os.path.join(target, "demand_" + "_".join(carriers) + ".png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, tech=tech)
        plot.selected_scalars.replace({"flow_in_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        fig, ax = plot.draw_plot(unit=unit, title=var_name)

        try:
            # rotate hierarchical labels
            ax.texts.clear()
            set_hierarchical_xlabels(
                plot.prepared_scalar_data.index,
                ax=ax,
                bar_yinterval=[0.4, 0.1],
                rotation=90,
                ha="right",
                hlines=True,
            )

            # Move the legend below current axis
            ax.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.42),
                fancybox=True,
                ncol=4,
                fontsize=14,
            )
            ax.set_title("demand " + " ".join(carriers))

            plot.save_plot(output_path_plot)
        except:  # noqa 722
            logger.warning("Could not plot.")

    plot_capacity()
    plot_invest_out_multi_carrier(CARRIERS)
    plot_flow_out_multi_carrier(CARRIERS)
    plot_demands(CARRIERS)

    # for carrier in CARRIERS:
    #     plot_storage_capacity(carrier)
    #     plot_invest_out(carrier)
    #     plot_storage_invest(carrier)
    #     plot_flow_out(carrier)
    #     plot_storage_out(carrier)
