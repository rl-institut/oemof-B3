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
import numpy as np
import oemoflex.tools.plots as plots
import pandas as pd
from oemoflex.tools.plots import plot_grouped_bar
from oemoflex.tools.helpers import load_yaml

from oemof_b3.config.config import LABELS, COLORS
from oemof_b3.config import config
from oemof_b3.tools import data_processing as dp

logger = logging.getLogger()


def aggregate_regions(df):
    # this is a work-around to use the dataprocessing function for postprocessed data,
    # which is in a similar but not in the same format as preprocessed oemof_b3 resources.
    _df = df.copy()
    _df.reset_index(inplace=True)
    _df = _df.rename(columns={"scenario": "scenario_key"})
    agg_method = {
        "var_value": sum,
        "name": lambda x: "None",
    }
    _df = dp.aggregate_scalars(_df, "region", agg_method=agg_method)
    _df = _df.rename(columns={"scenario_key": "scenario"})
    _df["name"] = _df.apply(lambda x: x["carrier"] + "-" + x["tech"], 1)
    _df = _df.set_index("scenario")
    return _df


def draw_standalone_legend(c_dict):
    import matplotlib.patches as mpatches

    fig = plt.figure(figsize=(14, 14))
    patches = [
        mpatches.Patch(color=color, label=label) for label, color in c_dict.items()
    ]
    fig.legend(
        patches,
        c_dict.keys(),
        loc="center",
        ncol=4,
        fontsize=14,
        frameon=False,
    )
    plt.tight_layout()
    return fig


def set_scenario_labels(df):
    """Replaces scenario name with scenario label if possible"""

    def get_scenario_label(scenario):
        try:
            scenario_settings = load_yaml(f"scenarios/{scenario}.yml")
        except FileNotFoundError:
            return scenario
        return scenario_settings.get("label", scenario)

    df.index = df.index.map(get_scenario_label)
    return df


def prepare_scalar_data(df, colors_odict, labels_dict, conv_number, tolerance=1e-3):
    # drop data that is almost zero
    def _drop_near_zeros(df, tolerance):
        df = df.loc[abs(df["var_value"]) > tolerance]
        return df

    df = _drop_near_zeros(df, tolerance)

    if df.empty:
        return df

    # remember order of scenarios
    scenario_order = df.index.unique()

    # pivot
    df_pivot = pd.pivot_table(
        df, index=["scenario", "region", "var_name"], columns="name", values="var_value"
    )

    # restore order of scenarios after pivoting
    df_pivot = df_pivot.reindex(scenario_order, level="scenario")

    def drop_constant_multiindex_levels(df):
        _df = df.copy()
        drop_levels = [
            name for name in _df.index.names if len(_df.index.unique(name)) <= 1
        ]
        _df.index = _df.index.droplevel(drop_levels)
        return _df

    # Drop levels that are all the same, e.g. 'ALL' for aggregated regions
    df_pivot = drop_constant_multiindex_levels(df_pivot)

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


# Add vertical line in plot
def add_vertical_line_in_plot(ax, df):
    _df = df.copy()

    index_length = len(_df.index)
    count_el = []
    count_gas = []

    # Get index positions of el and gas scenarios
    for pos, x in enumerate(list(_df.index)):
        # Case for single index
        if isinstance(x, (list, tuple)):
            if "el" in x[1]:
                count_el.append(pos)
            elif "moreCH4" in x[1] or "lessCH4" in x[1]:
                count_gas.append(pos)
        # Case for multi index
        else:
            if "el" in x:
                count_el.append(pos)
            elif "moreCH4" in x or "lessCH4" in x:
                count_gas.append(pos)

    # If they are in order (el first followed by gas)
    if [*count_el, *count_gas] == list(np.arange(0, index_length)):
        # Make second x-axis for vertical line
        ax_n = ax.twiny()

        # Pseudo plot for correct distribution of x-ticks
        ax_n.plot(
            np.arange(index_length * 2),
            np.zeros((index_length * 2, len(_df.columns))),
            alpha=0,
        )
        # Plot vertical line on secondary x-axis
        ax_n.axvline(x=(len(count_el) * 2) - 0.5, color="black", linewidth=1)

        # Reset ticks and tick labels of secondary x-axis
        ax_n.tick_params(width=0)
        ax_n.set_xticklabels([])


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
            colors_odict=COLORS,
            labels_dict=LABELS,
            conv_number=MW_TO_W,
        )

        return self.prepared_scalar_data

    def swap_levels(self, swaplevels=(0, 1)):

        if self.prepared_scalar_data is None:
            logger.warning("No prepared data found")

        elif not isinstance(self.prepared_scalar_data.index, pd.MultiIndex):
            logger.warning("Index is no  pandas MultiIndex. Cannot swap levels")

        else:
            self.prepared_scalar_data = self.prepared_scalar_data.swaplevel(*swaplevels)

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
        plot_grouped_bar(ax, self.prepared_scalar_data, COLORS, unit=unit, stacked=True)
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

    def draw_subplots(
        self, unit, title, figsize=None, facet_level=0, rotation=45, ha="right"
    ):
        # do not plot if the data is empty or all zeros.
        if (
            self.prepared_scalar_data.empty
            or (self.prepared_scalar_data == 0).all().all()
        ):
            logger.warning("Data is empty or all zero")
            return None, None

        # Set fig size to default size if no fig size is passed
        if not figsize:
            figsize = plt.rcParams.get("figure.figsize")

        fig = plt.figure(figsize=figsize)

        def set_index_full_product(df):
            r"""
            Ensures that the the MultiIndex covers the full product of the levels.
            """
            # df.index.levels messes up the order of the levels, but we want to keep it
            ordered_levels = [
                df.index.get_level_values(level).unique()
                for level in range(df.index.nlevels)
            ]

            index_full_product = pd.MultiIndex.from_product(ordered_levels)

            return df.reindex(index_full_product)

        self.prepared_scalar_data = set_index_full_product(self.prepared_scalar_data)

        grouped = self.prepared_scalar_data.groupby(level=facet_level)
        n_facets = len(grouped)

        for i, (facet_name, df) in enumerate(grouped):
            df = df.reset_index(level=[0], drop=True)
            df = df.fillna(0)
            df = df.loc[:, (df != 0).any(axis=0)]

            ax = fig.add_subplot(n_facets, 1, i + 1)

            plot_grouped_bar(ax, df, COLORS, unit=unit, stacked=True)

            ax.set_title(facet_name)

            # rotate xticklabels
            labels = ax.get_xticklabels()
            for lb in labels:
                lb.set_rotation(rotation)
                lb.set_ha(ha)

            ax.legend(
                loc="center left",
                bbox_to_anchor=(1.0, 0, 0, 1),
                fancybox=True,
                ncol=1,
                fontsize=14,
            )
            ax.tick_params("both", labelsize=TICK_LABEL_SIZE)

        fig.suptitle(title, fontsize="x-large")

        self.plotted = True

        # show only ticklabels of last plot
        axs = fig.get_axes()

        for ax in axs[:-1]:
            ax.tick_params(labelbottom=False)

        return fig, axs

    def save_plot(self, output_path_plot):
        if self.plotted:
            plt.savefig(output_path_plot, bbox_inches="tight")
            logger.info(f"Plot has been saved to: {output_path_plot}.")


def get_auto_bar_yinterval(index, space_per_letter, rotation):
    # set intervals according to maximal length of labels
    label_len_max = [
        max([len(v) for v in index.get_level_values(i)]) for i in index.names
    ]

    bar_yinterval = [space_per_letter * i for i in label_len_max][:-1]

    # if there is rotation, reduce the interval
    bar_yinterval = [
        interval * abs(np.sin(rotation)) + space_per_letter
        for interval, rotation in zip(bar_yinterval, rotation)
    ]

    return bar_yinterval


# TODO: This function could move to oemoflex once it is more mature
def set_hierarchical_xlabels(
    index,
    ax=None,
    hlines=False,
    bar_xmargin=0.1,
    bar_yinterval=None,
    rotation=0,
    ha=None,
):
    r"""
    adapted from https://linuxtut.com/ 'Draw hierarchical axis labels with matplotlib + pandas'
    """
    from itertools import groupby
    from matplotlib.lines import Line2D

    ax = ax or plt.gca()

    if not isinstance(index, pd.MultiIndex):
        logging.info(
            "Index is not a pd.MultiIndex. Need a multiindex to set hierarchical labels."
        )
        return None

    labels = ax.set_xticklabels([s for *_, s in index])

    transform = ax.get_xaxis_transform()

    n_levels = index.nlevels
    n_intervals = len(index.codes) - 1

    if isinstance(rotation, (float, int)):
        rotation = [rotation] * n_levels

    elif len(rotation) != n_levels:
        raise ValueError(
            "Number of values for rotation must be 1 or match number of index levels."
        )

    if bar_yinterval is None:
        SPACE_PER_LETTER = 0.05
        bar_yinterval = get_auto_bar_yinterval(index, SPACE_PER_LETTER, rotation)

    if isinstance(bar_yinterval, (float, int)):
        bar_yinterval = [bar_yinterval] * n_intervals

    elif len(bar_yinterval) != n_intervals:
        raise ValueError(
            "Must either pass one value for bar_yinterval or a list of values that matches the"
            "number of index levels minus one."
        )

    if rotation[0] != 0:
        for lb in labels:
            lb.set_rotation(rotation[0])
            lb.set_ha(ha)

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
                rotation=rotation[i],
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
    CARRIERS = ["electricity", "heat_central", "heat_decentral", "h2", "ch4"]
    CARRIERS_WO_CH4 = ["electricity", "heat_central", "heat_decentral", "h2"]
    MW_TO_W = 1e6
    TICK_LABEL_SIZE = 12

    # create the directory plotted where all plots are saved
    if not os.path.exists(target):
        os.makedirs(target)

    # Load scalar data
    scalars = load_scalars(scalars_path)
    scalars = set_scenario_labels(scalars)

    def plot_capacities():
        var_name = "capacity"
        unit = "W"
        output_path_plot = os.path.join(target, "capacities.png")

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        fig, ax = plot.draw_plot(unit=unit, title=None)
        try:
            # Move the legend below current axis
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(1, 1),
                fancybox=True,
                ncol=1,
                fontsize=14,
            )
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)
            plt.xticks(rotation=45, ha="right")

            add_vertical_line_in_plot(ax, plot.prepared_scalar_data)

            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def plot_invest_out(carrier):
        var_name = f"invest_out_{carrier}"
        unit = "W"
        output_path_plot = os.path.join(target, var_name + ".png")

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        fig, ax = plot.draw_plot(unit=unit, title=None)
        plot.save_plot(output_path_plot)

    def plot_storage_capacity(carrier):
        title = f"storage_capacity_{carrier}"
        output_path_plot = os.path.join(target, title + ".png")
        var_name = "storage_capacity"
        unit = "Wh"

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, carrier=carrier)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        fig, ax = plot.draw_plot(unit=unit, title=None)
        plot.save_plot(output_path_plot)

    def plot_storage_invest(carrier):
        title = f"storage_invest_{carrier}"
        output_path_plot = os.path.join(target, f"{title}.png")
        var_name = "invest"
        unit = "Wh"

        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, carrier=carrier)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.draw_plot(unit=unit, title=None)
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
        plot.draw_plot(unit=unit, title=None)
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
        plot.draw_plot(unit=unit, title=None)
        plot.save_plot(output_path_plot)

    def plot_invest_out_multi_carrier(carriers):
        var_name = [f"invest_out_{carrier}" for carrier in carriers]
        unit = "W"
        output_path_plot = os.path.join(target, "energy_usage.png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.selected_scalars.replace({"invest_out_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.swap_levels()
        plot.prepared_scalar_data.sort_index(level=0, inplace=True)
        fig, ax = plot.draw_plot(unit=unit, title=None)

        try:
            # rotate hierarchical labels
            ax.texts.clear()
            set_hierarchical_xlabels(
                plot.prepared_scalar_data.index,
                ax=ax,
                rotation=[70, 70],
                ha="right",
                hlines=True,
            )

            # Move the legend below current axis
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(1, 1),
                fancybox=True,
                ncol=2,
                fontsize=14,
            )
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)

            add_vertical_line_in_plot(ax, plot.prepared_scalar_data)

            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def plot_flow_out_multi_carrier(carriers):
        var_name = [f"flow_out_{carrier}" for carrier in carriers]
        unit = "Wh"
        output_path_plot = os.path.join(target, "summed_energy.png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.selected_scalars = dp.filter_df(
            plot.selected_scalars, column_name="type", values="storage", inverse=True
        )
        plot.selected_scalars.replace({"flow_out_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.swap_levels()
        plot.prepared_scalar_data.sort_index(level=0, inplace=True)
        fig, ax = plot.draw_plot(unit=unit, title=None)

        try:
            # rotate hierarchical labels
            ax.texts.clear()
            set_hierarchical_xlabels(
                plot.prepared_scalar_data.index,
                ax=ax,
                rotation=[70, 70],
                ha="right",
                hlines=True,
            )

            # Move the legend below current axis
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(1, 1),
                fancybox=True,
                ncol=2,
                fontsize=14,
            )
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)

            add_vertical_line_in_plot(ax, plot.prepared_scalar_data)

            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def plot_demands(carriers):
        var_name = [f"flow_in_{carrier}" for carrier in carriers]
        tech = "demand"
        unit = "Wh"
        output_path_plot = os.path.join(target, "demands.png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, tech=tech)
        plot.selected_scalars.replace({"flow_in_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.swap_levels()
        plot.prepared_scalar_data.sort_index(level=0, inplace=True)
        fig, ax = plot.draw_plot(unit=unit, title=None)

        try:
            # rotate hierarchical labels
            ax.texts.clear()
            set_hierarchical_xlabels(
                plot.prepared_scalar_data.index,
                ax=ax,
                rotation=[70, 70],
                ha="right",
                hlines=True,
            )

            # Move the legend below current axis
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(1, 1),
                fancybox=True,
                ncol=1,
                fontsize=14,
            )
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)

            add_vertical_line_in_plot(ax, plot.prepared_scalar_data)

            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def subplot_invest_out_multi_carrier(carriers):
        var_name = [f"invest_out_{carrier}" for carrier in carriers]
        unit = "W"
        output_path_plot = os.path.join(
            target,
            "invested_capacity_subplots.png",
        )
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)

        # replacing invest_out_<carrier> with <carrier> to subplot by carrier
        plot.selected_scalars.replace({"invest_out_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.swap_levels()

        fig, axs = plot.draw_subplots(unit=unit, title=None, figsize=(11, 13))

        for ax in axs:
            add_vertical_line_in_plot(ax, plot.selected_scalars)
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)

        try:
            plt.tight_layout()
            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def subplot_storage_invest_multi_carrier(carriers):
        var_name = "invest"
        unit = "Wh"
        output_path_plot = os.path.join(target, "storage_invest_subplots.png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)

        # replacing invest with <carrier> to subplot by carrier
        plot.selected_scalars["var_name"] = plot.selected_scalars["carrier"]
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.swap_levels()
        plot.draw_subplots(unit=unit, title=None, figsize=(11, 11))

        try:
            plt.tight_layout()
            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def subplot_demands(carriers):
        var_name = [f"flow_in_{carrier}" for carrier in carriers]
        tech = "demand"
        unit = "Wh"
        output_path_plot = os.path.join(target, "demands_subplots.png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name, tech=tech)
        plot.selected_scalars.replace({"flow_in_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.swap_levels()

        fig, axs = plot.draw_subplots(unit=unit, title=None, figsize=(11, 13))

        for ax in axs:
            add_vertical_line_in_plot(ax, plot.selected_scalars)
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)

        try:
            plt.tight_layout()
            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def subplot_energy_usage_multi_carrier(carriers):
        var_name = [f"flow_in_{carrier}" for carrier in carriers]
        unit = "Wh"
        output_path_plot = os.path.join(target, "energy_usage_subplots.png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        # exclude storage charging
        plot.selected_scalars = dp.filter_df(
            plot.selected_scalars, column_name="type", values="storage", inverse=True
        )
        plot.selected_scalars.replace({"flow_in_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.swap_levels()

        fig, axs = plot.draw_subplots(unit=unit, title=None, figsize=(11, 13))

        for ax in axs:
            add_vertical_line_in_plot(ax, plot.selected_scalars)
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)

        try:
            plt.tight_layout()
            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def subplot_flow_out_multi_carrier(carriers):
        var_name = [f"flow_out_{carrier}" for carrier in carriers]
        unit = "Wh"
        output_path_plot = os.path.join(target, "summed_energy_subplots.png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        plot.selected_scalars = dp.filter_df(
            plot.selected_scalars, column_name="type", values="storage", inverse=True
        )
        plot.selected_scalars.replace({"flow_out_*": ""}, regex=True, inplace=True)
        plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
        plot.swap_levels()

        fig, axs = plot.draw_subplots(unit=unit, title=None, figsize=(11, 13))

        for ax in axs:
            add_vertical_line_in_plot(ax, plot.selected_scalars)
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)

        try:
            plt.tight_layout()
            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    def plot_demands_stacked_carriers(carriers):
        var_name = [f"flow_in_{carrier}" for carrier in carriers]
        tech = "demand"
        unit = "Wh"
        output_path_plot = os.path.join(target, "demands_stacked.png")
        plot = ScalarPlot(scalars)
        plot.select_data(var_name=var_name)
        # Show only demands
        plot.selected_scalars = dp.filter_df(
            plot.selected_scalars, column_name="tech", values=tech, inverse=False
        )
        # Remove "flow_in_" from var_name
        plot.selected_scalars.replace({"flow_in_*": ""}, regex=True, inplace=True)
        # Aggregate regions
        plot.prepared_scalar_data = aggregate_regions(plot.selected_scalars)
        # Drop index
        plot.prepared_scalar_data = plot.prepared_scalar_data.reset_index()
        # Set index to "scenario" and "var_name"
        plot.prepared_scalar_data = plot.prepared_scalar_data.set_index(
            ["scenario", "var_name"]
        )

        # Show only var_value of prepared scalar data
        plot.prepared_scalar_data = plot.prepared_scalar_data.filter(
            items=["var_value"]
        )

        # Remember index to apply it after unstacking
        index = plot.prepared_scalar_data.index.get_level_values(0).unique()
        # Unstack prepared and filtered data regarding carriers
        plot.prepared_scalar_data = plot.prepared_scalar_data.unstack("var_name")

        # Reindex to keep previous scenario order
        plot.prepared_scalar_data = plot.prepared_scalar_data.reindex(index)

        # Get names of data's columns
        column_names = plot.prepared_scalar_data.columns
        # Reset multiindex
        plot.prepared_scalar_data = plot.prepared_scalar_data.T.reset_index(drop=True).T

        # Rename the columns to their respective energy carrier and append "-demand" to match
        # the naming convention
        for column_num, column_name in enumerate(column_names):
            plot.prepared_scalar_data.rename(
                columns={column_num: column_name[1] + "-demand"}, inplace=True
            )

        # rename and aggregate duplicated columns
        plot.prepared_scalar_data = plots.map_labels(plot.prepared_scalar_data, LABELS)

        fig, ax = plot.draw_plot(unit=unit, title=var_name)

        # Reset plot title
        ax.set_title("")

        try:
            # Move the legend below current axis
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(1, 1),
                fancybox=True,
                ncol=1,
                fontsize=14,
            )
            ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE)
            plt.xticks(rotation=45, ha="right")

            add_vertical_line_in_plot(ax, plot.prepared_scalar_data)

            plot.save_plot(output_path_plot)

        except Exception as e:  # noqa 722
            logger.warning(f"Could not plot {output_path_plot}: {e}.")

    plot_capacities()
    plot_invest_out_multi_carrier(CARRIERS_WO_CH4)
    plot_flow_out_multi_carrier(CARRIERS_WO_CH4)
    plot_demands(CARRIERS)
    subplot_invest_out_multi_carrier(CARRIERS_WO_CH4)
    subplot_storage_invest_multi_carrier(CARRIERS_WO_CH4)
    subplot_flow_out_multi_carrier(CARRIERS_WO_CH4)
    subplot_demands(CARRIERS)
    subplot_energy_usage_multi_carrier(CARRIERS)
    plot_demands_stacked_carriers(CARRIERS)

    standalone_legend = False
    if standalone_legend:
        fig = draw_standalone_legend(COLORS)
        plt.savefig(os.path.join(target, "legend.png"))

    # for carrier in CARRIERS:
    #     plot_storage_capacity(carrier)
    #     plot_invest_out(carrier)
    #     plot_storage_invest(carrier)
    #     plot_flow_out(carrier)
    #     plot_storage_out(carrier)
