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
    prepare_scalar_data,
    swap_levels,
    draw_plot,
    draw_subplots,
    save_plot,
    add_vertical_line_in_plot,
    aggregate_regions,
    draw_standalone_legend,
    set_hierarchical_xlabels,
    set_scenario_labels,
)

logger = logging.getLogger()

POS_VLINE = 3


def try_to_plot(func):
    def decorated_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Could not plot '{func.__name__}' because: {e}.")

    return decorated_func


@try_to_plot
def plot_invest_out(carrier):
    var_name = f"invest_out_{carrier}"
    unit = "W"
    output_path_plot = os.path.join(
        target, var_name + config.settings.general.plot_filetype
    )

    df = dp.multi_filter_df(scalars, var_name=var_name)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    draw_plot(df, unit=unit, title=None)
    save_plot(output_path_plot)


@try_to_plot
def plot_storage_capacity(carrier):
    title = f"storage_capacity_{carrier}"
    output_path_plot = os.path.join(
        target, title + config.settings.general.plot_filetype
    )
    var_name = "storage_capacity"
    unit = "Wh"

    df = dp.multi_filter_df(scalars, var_name=var_name, carrier=carrier)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    draw_plot(df, unit=unit, title=None)
    save_plot(output_path_plot)


@try_to_plot
def plot_storage_invest(carrier):
    title = f"storage_invest_{carrier}"
    output_path_plot = os.path.join(
        target, f"{title}" + config.settings.general.plot_filetype
    )
    var_name = "invest"
    unit = "Wh"

    df = dp.multi_filter_df(scalars, var_name=var_name, carrier=carrier)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    draw_plot(df, unit=unit, title=None)
    save_plot(output_path_plot)


@try_to_plot
def plot_flow_out(carrier):
    title = f"production_{carrier}"
    output_path_plot = os.path.join(
        target, f"{title}" + config.settings.general.plot_filetype
    )
    var_name = f"flow_out_{carrier}"
    unit = "Wh"

    df = dp.multi_filter_df(scalars, var_name=var_name)
    df = dp.filter_df(
        df,
        "type",
        ["storage", "asymmetric_storage", "link"],
        inverse=True,
    )
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    draw_plot(df, unit=unit, title=None)
    save_plot(output_path_plot)


@try_to_plot
def plot_storage_out(carrier):
    title = f"storage_out_{carrier}"
    output_path_plot = os.path.join(
        target, f"{title}" + config.settings.general.plot_filetype
    )
    var_name = f"flow_out_{carrier}"
    unit = "Wh"

    df = dp.multi_filter_df(var_name=var_name)
    df = dp.filter_df(df, "type", ["storage", "asymmetric_storage"])
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    draw_plot(df, unit=unit, title=None)
    save_plot(output_path_plot)


@try_to_plot
def plot_invest_out_multi_carrier(carriers):
    var_name = [f"invest_out_{carrier}" for carrier in carriers]
    unit = "W"
    output_path_plot = os.path.join(
        target, "energy_usage" + config.settings.general.plot_filetype
    )
    df = dp.multi_filter_df(scalars, var_name=var_name)
    df = df.replace({"invest_out_*": ""}, regex=True)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    df = swap_levels(df)
    df = df.sort_index(level=0)
    fig, ax = draw_plot(df, unit=unit, title=None)
    # rotate hierarchical labels
    ax.texts.clear()
    set_hierarchical_xlabels(
        df.index,
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

    add_vertical_line_in_plot(ax, position=POS_VLINE)

    save_plot(output_path_plot)


@try_to_plot
def plot_flow_out_multi_carrier(carriers):
    var_name = [f"flow_out_{carrier}" for carrier in carriers]
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "summed_energy" + config.settings.general.plot_filetype
    )

    df = dp.multi_filter_df(scalars, var_name=var_name)
    df = dp.filter_df(df, column_name="type", values="storage", inverse=True)
    df = df.replace({"flow_out_*": ""}, regex=True)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    df = swap_levels(df)
    df = df.sort_index(level=0)
    fig, ax = draw_plot(df, unit=unit, title=None)

    # rotate hierarchical labels
    ax.texts.clear()
    set_hierarchical_xlabels(
        df.index,
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

    add_vertical_line_in_plot(ax, position=POS_VLINE)

    save_plot(output_path_plot)


@try_to_plot
def plot_demands(carriers):
    var_name = [f"flow_in_{carrier}" for carrier in carriers]
    tech = "demand"
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "demands" + config.settings.general.plot_filetype
    )

    df = dp.multi_filter_df(scalars, var_name=var_name, tech=tech)
    df = df.replace({"flow_in_*": ""}, regex=True)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    df = swap_levels(df)
    df = df.sort_index(level=0)
    fig, ax = draw_plot(df, unit=unit, title=None)

    # rotate hierarchical labels
    ax.texts.clear()
    set_hierarchical_xlabels(
        df.index,
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

    add_vertical_line_in_plot(ax, position=POS_VLINE)

    save_plot(output_path_plot)


@try_to_plot
def subplot_invest_out_multi_carrier(carriers):
    var_name = [f"invest_out_{carrier}" for carrier in carriers]
    unit = "W"
    output_path_plot = os.path.join(
        target,
        "invested_capacity_subplots" + config.settings.general.plot_filetype,
    )

    df = dp.multi_filter_df(scalars, var_name=var_name)

    # replacing invest_out_<carrier> with <carrier> to subplot by carrier
    df = df.replace({"invest_out_*": ""}, regex=True)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    df = swap_levels(df)

    fig, axs = draw_subplots(df, unit=unit, title=None, figsize=(11, 13))

    for ax in axs:
        add_vertical_line_in_plot(ax, position=POS_VLINE)
        ax.tick_params(
            axis="both",
            labelsize=config.settings.plot_scalar_results.tick_label_size,
        )
    plt.tight_layout()
    save_plot(output_path_plot)


@try_to_plot
def subplot_storage_invest_multi_carrier(carriers):
    var_name = "invest"
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "storage_invest_subplots" + config.settings.general.plot_filetype
    )

    df = dp.multi_filter_df(scalars, var_name=var_name)

    # replacing invest with <carrier> to subplot by carrier
    df["var_name"] = df["carrier"]
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    df = swap_levels(df)
    draw_subplots(df, unit=unit, title=None, figsize=(11, 13))

    plt.tight_layout()
    save_plot(output_path_plot)


@try_to_plot
def subplot_demands(carriers):
    var_name = [f"flow_in_{carrier}" for carrier in carriers]
    tech = "demand"
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "demands_subplots" + config.settings.general.plot_filetype
    )

    df = dp.multi_filter_df(scalars, var_name=var_name, tech=tech)
    df = df.replace({"flow_in_*": ""}, regex=True)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    df = swap_levels(df)

    fig, axs = draw_subplots(df, unit=unit, title=None, figsize=(11, 13))

    for ax in axs:
        add_vertical_line_in_plot(ax, position=POS_VLINE)
        ax.tick_params(
            axis="both",
            labelsize=config.settings.plot_scalar_results.tick_label_size,
        )
    plt.tight_layout()
    save_plot(output_path_plot)


@try_to_plot
def subplot_energy_usage_multi_carrier(carriers):
    var_name = [f"flow_in_{carrier}" for carrier in carriers]
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "energy_usage_subplots" + config.settings.general.plot_filetype
    )

    df = dp.multi_filter_df(scalars, var_name=var_name)
    # exclude storage charging
    df = dp.filter_df(df, column_name="type", values="storage", inverse=True)
    df = df.replace({"flow_in_*": ""}, regex=True)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    df = swap_levels(df)

    fig, axs = draw_subplots(df, unit=unit, title=None, figsize=(11, 13))

    for ax in axs:
        add_vertical_line_in_plot(ax, position=POS_VLINE)
        ax.tick_params(
            axis="both",
            labelsize=config.settings.plot_scalar_results.tick_label_size,
        )
    plt.tight_layout()
    save_plot(output_path_plot)


@try_to_plot
def subplot_flow_out_multi_carrier(carriers):
    var_name = [f"flow_out_{carrier}" for carrier in carriers]
    unit = "Wh"
    output_path_plot = os.path.join(
        target, "summed_energy_subplots" + config.settings.general.plot_filetype
    )

    df = dp.multi_filter_df(scalars, var_name=var_name)
    df = dp.filter_df(df, column_name="type", values="storage", inverse=True)
    df = df.replace({"flow_out_*": ""}, regex=True)
    if config.settings.plot_scalar_results.agg_regions:
        df = aggregate_regions(df)
    df = prepare_scalar_data(df)
    df = swap_levels(df)

    fig, axs = draw_subplots(df, unit=unit, title=None, figsize=(11, 13))

    for ax in axs:
        add_vertical_line_in_plot(ax, position=POS_VLINE)
        ax.tick_params(
            axis="both",
            labelsize=config.settings.plot_scalar_results.tick_label_size,
        )
    plt.tight_layout()
    save_plot(output_path_plot)


@try_to_plot
def plot_demands_stacked_carriers(carriers):
    var_name = [f"flow_in_{carrier}" for carrier in carriers]
    tech = "demand"
    unit = "Wh"
    MW_TO_W = 1e6
    output_path_plot = os.path.join(
        target, "demands_stacked" + config.settings.general.plot_filetype
    )

    df = dp.multi_filter_df(scalars, var_name=var_name)
    # Show only demands
    df = dp.filter_df(df, column_name="tech", values=tech, inverse=False)
    # Remove "flow_in_" from var_name
    df = df.replace({"flow_in_*": ""}, regex=True)
    # Aggregate regions
    df = aggregate_regions(df)
    # Drop index
    df = df.reset_index()
    # Set index to "scenario" and "var_name"
    df = df.set_index(["scenario_key", "var_name"])

    # Show only var_value of prepared scalar data
    df = df.filter(items=["var_value"])

    # Convert to SI units
    df *= MW_TO_W

    # Remember index to apply it after unstacking
    index = df.index.get_level_values(0).unique()
    # Unstack prepared and filtered data regarding carriers
    df = df.unstack("var_name")

    # Reindex to keep previous scenario order
    df = df.reindex(index)

    # Get names of data's columns
    column_names = df.columns

    # Reset multiindex
    df = df.T.reset_index(drop=True).T

    # Rename the columns to their respective energy carrier and append "-demand" to match
    # the naming convention
    for column_num, column_name in enumerate(column_names):
        df = df.rename(columns={column_num: column_name[1] + "-demand"})

    # rename and aggregate duplicated columns
    df = plots.map_labels(df, LABELS)

    fig, ax = draw_plot(df, unit=unit, title=var_name)

    # Reset plot title
    ax.set_title("")

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

    add_vertical_line_in_plot(ax, position=POS_VLINE)

    save_plot(output_path_plot)


def load_scalar_results(path, sep=config.settings.general.separator):

    df = pd.read_csv(path, sep=sep)

    df = df.rename(columns={"scenario": "scenario_key"})

    df["var_value"] = pd.to_numeric(df["var_value"], errors="coerce").fillna(
        df["var_value"]
    )

    df = dp.format_header(
        df, dp.HEADER_B3_SCAL, config.settings.general.scal_index_name
    )

    return df


if __name__ == "__main__":
    scalars_path = os.path.join(sys.argv[1], "scalars.csv")
    target = sys.argv[2]

    logger = config.add_snake_logger("plot_scalar_results")

    # User input
    CARRIERS = ["electricity", "heat_central", "heat_decentral", "h2", "ch4"]
    CARRIERS_WO_CH4 = ["electricity", "heat_central", "heat_decentral", "h2"]

    # create the directory plotted where all plots are saved
    if not os.path.exists(target):
        os.makedirs(target)

    # Load scalar data
    scalars = load_scalar_results(scalars_path)
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
