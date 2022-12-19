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
    ``results/{scenario}/{scenario}.log``: path to logfile

Outputs
---------
Plots of scalar results with a file format defined by the *plot_filetype* variable in
``oemof_b3/config/settings.yaml``.

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

from oemof_b3.config import config
from oemof_b3.config.config import COLORS, LABELS
from oemof_b3.tools import data_processing as dp
from oemof_b3.tools.plots import (
    ScalarPlot,
    add_vertical_line_in_plot,
    aggregate_regions,
    draw_standalone_legend,
    set_hierarchical_xlabels,
    set_scenario_labels,
)

logger = logging.getLogger()


def plot_invest_out(carrier):
    var_name = f"invest_out_{carrier}"
    unit = "W"
    output_path_plot = os.path.join(
        target, var_name + config.settings.general.plot_filetype
    )

    plot = ScalarPlot(scalars)
    plot.select_data(var_name=var_name)
    plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
    fig, ax = plot.draw_plot(unit=unit, title=None)
    plot.save_plot(output_path_plot)


def plot_storage_capacity(carrier):
    title = f"storage_capacity_{carrier}"
    output_path_plot = os.path.join(
        target, title + config.settings.general.plot_filetype
    )
    var_name = "storage_capacity"
    unit = "Wh"

    plot = ScalarPlot(scalars)
    plot.select_data(var_name=var_name, carrier=carrier)
    plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
    fig, ax = plot.draw_plot(unit=unit, title=None)
    plot.save_plot(output_path_plot)


def plot_storage_invest(carrier):
    title = f"storage_invest_{carrier}"
    output_path_plot = os.path.join(
        target, f"{title}" + config.settings.general.plot_filetype
    )
    var_name = "invest"
    unit = "Wh"

    plot = ScalarPlot(scalars)
    plot.select_data(var_name=var_name, carrier=carrier)
    plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
    plot.draw_plot(unit=unit, title=None)
    plot.save_plot(output_path_plot)


def plot_flow_out(carrier):
    title = f"production_{carrier}"
    output_path_plot = os.path.join(
        target, f"{title}" + config.settings.general.plot_filetype
    )
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
    output_path_plot = os.path.join(
        target, f"{title}" + config.settings.general.plot_filetype
    )
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
    output_path_plot = os.path.join(
        target, "energy_usage" + config.settings.general.plot_filetype
    )
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
        ax.tick_params(
            axis="both",
            labelsize=config.settings.plot_scalar_results.tick_label_size,
        )

        add_vertical_line_in_plot(ax, position=6)

        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def plot_flow_out_multi_carrier(carriers):
    var_name = [f"flow_out_{carrier}" for carrier in carriers]
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "summed_energy" + config.settings.general.plot_filetype
    )
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
        ax.tick_params(
            axis="both",
            labelsize=config.settings.plot_scalar_results.tick_label_size,
        )

        add_vertical_line_in_plot(ax, position=6)

        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def plot_demands(carriers):
    var_name = [f"flow_in_{carrier}" for carrier in carriers]
    tech = "demand"
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "demands" + config.settings.general.plot_filetype
    )
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
        ax.tick_params(
            axis="both",
            labelsize=config.settings.plot_scalar_results.tick_label_size,
        )

        add_vertical_line_in_plot(ax, position=6)

        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def subplot_invest_out_multi_carrier(carriers):
    var_name = [f"invest_out_{carrier}" for carrier in carriers]
    unit = "W"
    output_path_plot = os.path.join(
        target,
        "invested_capacity_subplots" + config.settings.general.plot_filetype,
    )
    plot = ScalarPlot(scalars)
    plot.select_data(var_name=var_name)

    # replacing invest_out_<carrier> with <carrier> to subplot by carrier
    plot.selected_scalars.replace({"invest_out_*": ""}, regex=True, inplace=True)
    plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
    plot.swap_levels()

    fig, axs = plot.draw_subplots(unit=unit, title=None, figsize=(11, 13))

    try:
        for ax in axs:
            add_vertical_line_in_plot(ax, position=6)
            ax.tick_params(
                axis="both",
                labelsize=config.settings.plot_scalar_results.tick_label_size,
            )
        plt.tight_layout()
        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def subplot_storage_invest_multi_carrier(carriers):
    var_name = "invest"
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "storage_invest_subplots" + config.settings.general.plot_filetype
    )
    plot = ScalarPlot(scalars)
    plot.select_data(var_name=var_name)

    # replacing invest with <carrier> to subplot by carrier
    plot.selected_scalars["var_name"] = plot.selected_scalars["carrier"]
    plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
    plot.swap_levels()
    plot.draw_subplots(unit=unit, title=None, figsize=(11, 13))

    try:
        plt.tight_layout()
        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def subplot_demands(carriers):
    var_name = [f"flow_in_{carrier}" for carrier in carriers]
    tech = "demand"
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "demands_subplots" + config.settings.general.plot_filetype
    )
    plot = ScalarPlot(scalars)
    plot.select_data(var_name=var_name, tech=tech)
    plot.selected_scalars.replace({"flow_in_*": ""}, regex=True, inplace=True)
    plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
    plot.swap_levels()

    fig, axs = plot.draw_subplots(unit=unit, title=None, figsize=(11, 13))

    try:
        for ax in axs:
            add_vertical_line_in_plot(ax, position=6)
            ax.tick_params(
                axis="both",
                labelsize=config.settings.plot_scalar_results.tick_label_size,
            )
        plt.tight_layout()
        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def subplot_energy_usage_multi_carrier(carriers):
    var_name = [f"flow_in_{carrier}" for carrier in carriers]
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "energy_usage_subplots" + config.settings.general.plot_filetype
    )
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

    try:
        for ax in axs:
            add_vertical_line_in_plot(ax, position=6)
            ax.tick_params(
                axis="both",
                labelsize=config.settings.plot_scalar_results.tick_label_size,
            )
        plt.tight_layout()
        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def subplot_flow_out_multi_carrier(carriers):
    var_name = [f"flow_out_{carrier}" for carrier in carriers]
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "summed_energy_subplots" + config.settings.general.plot_filetype
    )
    plot = ScalarPlot(scalars)
    plot.select_data(var_name=var_name)
    plot.selected_scalars = dp.filter_df(
        plot.selected_scalars, column_name="type", values="storage", inverse=True
    )
    plot.selected_scalars.replace({"flow_out_*": ""}, regex=True, inplace=True)
    plot.prepare_data(agg_regions=config.settings.plot_scalar_results.agg_regions)
    plot.swap_levels()

    fig, axs = plot.draw_subplots(unit=unit, title=None, figsize=(11, 13))

    try:
        for ax in axs:
            add_vertical_line_in_plot(ax, position=6)
            ax.tick_params(
                axis="both",
                labelsize=config.settings.plot_scalar_results.tick_label_size,
            )
        plt.tight_layout()
        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def plot_demands_stacked_carriers(carriers):
    var_name = [f"flow_in_{carrier}" for carrier in carriers]
    tech = "demand"
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "demands_stacked" + config.settings.general.plot_filetype
    )
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
    plot.prepared_scalar_data = plot.prepared_scalar_data.filter(items=["var_value"])

    # Convert to SI units
    plot.prepared_scalar_data *= MW_TO_W

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
        ax.tick_params(
            axis="both",
            labelsize=config.settings.plot_scalar_results.tick_label_size,
        )
        plt.xticks(rotation=45, ha="right")

        add_vertical_line_in_plot(ax, position=6)

        plot.save_plot(output_path_plot)

    except Exception as e:  # noqa 722
        logger.warning(f"Could not plot {output_path_plot}: {e}.")


def load_scalars(path):
    df = pd.read_csv(path, sep=config.settings.general.separator, index_col=0)
    return df


if __name__ == "__main__":
    scalars_path = os.path.join(sys.argv[1], "scalars.csv")
    target = sys.argv[2]

    logger = config.add_snake_logger("plot_scalar_results")

    # User input
    CARRIERS = ["electricity", "heat_central", "heat_decentral", "h2", "ch4"]
    CARRIERS_WO_CH4 = ["electricity", "heat_central", "heat_decentral", "h2"]
    MW_TO_W = 1e6
    IGNORE_DROP_LEVEL = config.settings.plot_scalar_results.ignore_drop_level

    # create the directory plotted where all plots are saved
    if not os.path.exists(target):
        os.makedirs(target)

    # Load scalar data
    scalars = load_scalars(scalars_path)
    scalars = set_scenario_labels(scalars)

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
        plt.savefig(
            os.path.join(target, "legend" + config.settings.general.plot_filetype)
        )
