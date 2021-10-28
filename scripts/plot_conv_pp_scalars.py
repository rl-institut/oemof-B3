r"""
Inputs
-------
resources : str
    path of input file with data of prepared conventional power plant data as .csv
target : str
    path of output file with plot

Outputs
---------
matplotlib.figure.Figure
    plotted conventional power plant data

Description
-------------
The script takes prepared data of conventional power plants from OPSD, prepares the
data further and plots the data.
"""
import os
import sys

import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots
import pandas as pd

import oemof_b3.tools.data_processing as dp
from oemof_b3 import colors_odict

# User input
var_name = "capacity_net_el"
# converting from MW to W
conv_number = 1e6
german_translation = True


# GENERAL
unit_dict = {"capacity_net_el": "W"}
carrier_dict = {
    "biomass": "Biomass",
    "ch4": "CH4",
    "hard coal": "Hard coal",
    "oil": "Oil",
    "lignite": "Lignite",
    "other": "Other",
}

german_labels = {
    "Biomass": "Biomasse",
    "CH4": "Erdgas",
    "Hard coal": "Steinkohle",
    "Oil": "Öl",
    "Lignite": "Braunkohle",
    "Other": "Andere",
}


def prepare_conv_pp_scalars(df_conv_pp_scalars, var_name, conv_number, carrier_dict=carrier_dict):
    r"""
    This function prepares the scalar data file of the conventional power plants in
    Berlin and Brandenburg. It aggregates power plants with the same carrier in a
    region and puts the data in a pivot table to allow to plot a grouped
    bar plot.

    Parameters
    ----------
    df_conv_pp_scalars: pd.DataFrame
        contains all conventional power plants in Berlin and Brandenburg
    var_name: string
        indicates the var_name which shall be plotted
    conv_number: int
         converts the value to SI unit, i.e. W
    carrier_dict: dict
         capitalizes carrier names
    Returns
    -------
    df_pivot : pandas.DataFrame
        Unique unit
    color_keys: pandas.Index
        determines order of carriers in plot
    color_dict: dict
        contains colors for different carriers for plotting
    """
    # select var_name to be plotted
    selected_df = df_conv_pp_scalars[df_conv_pp_scalars["var_name"] == var_name].copy()

    # CONV_PP specific
    selected_df.loc[(selected_df["region"] != "Berlin"), "region"] = "Brandenburg"
    # capitalize carrier names
    selected_df["carrier"].replace(carrier_dict, inplace=True)
    # aggregate carriers in regions
    selected_df_agg = dp.aggregate_scalars(df=selected_df, columns_to_aggregate=["tech"])

    # apply pivot table
    df_pivot = pd.pivot_table(
        selected_df_agg,
        index=["region"],
        columns="carrier",
        values="var_value",
    )

    # colors
    if german_translation:
        color_keys = df_pivot.columns
        german_color_dict = {}
        for key in color_keys:
            german_color_dict[german_labels[key]] = colors_odict[key]
        df_pivot.rename(columns=german_labels, inplace=True)
        german_color_keys = df_pivot.columns
        color_keys = german_color_keys
        color_dict = german_color_dict
    else:
        color_keys = df_pivot.columns
        color_dict = colors_odict
    # convert to SI unit:
    if conv_number:
        df_pivot *= conv_number

    return df_pivot, color_keys, color_dict


def plot_conv_pp_scalars(df, color_keys, color_dict, unit_dict):
    r"""
    This function plots the net installed capacity of conventional power plants
    in Berlin and Brandenburg in a grouped bar plot.

    Parameters
    ----------
    df: pd.DataFrame
        pivot table with aggregated net installed capacity based on carrier
        of conventional power plants in Berlin and Brandenburg
    color_keys: pandas.Index
        determines order of carriers in plot
    color_dict: dict
        contains colors for different carriers for plotting
    unit_dict: dict
        contains units to var_name which is plotted
    """
    alpha = 0.3
    fontsize = 14
    plt.rcParams.update({"font.size": fontsize})

    fig, ax = plt.subplots(figsize=(12, 6))
    # apply EngFormatter if power is plotted
    if unit_dict[var_name] == "W":
        ax = plots._eng_format(ax, "W")
    df.plot.bar(
        ax=ax,
        color=[color_dict[key] for key in color_keys],
        width=0.8,
        zorder=2,
        stacked=False,
        rot=0,
    )

    for spine in ["top", "left", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_alpha(alpha)
    ax.tick_params(axis="both", length=0, pad=7)

    ax.grid(axis="y", zorder=1, color="black", alpha=alpha)
    ax.set_xlabel(xlabel=None)
    ax.legend(labels=german_labels)
    plt.legend(title=None, frameon=True, framealpha=1)

    plt.tight_layout()
    plt.savefig(target, bbox_inches="tight")


if __name__ == "__main__":
    resources = sys.argv[1]

    target = sys.argv[2]

    target_dir = os.path.dirname(target)

    # create the directory plotted where all plots are saved
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Load scalar data
    df_conv_pp_scalars = dp.load_b3_scalars(resources)

    df_pivot, color_keys, color_dict = prepare_conv_pp_scalars(
        df_conv_pp_scalars=df_conv_pp_scalars, var_name=var_name, conv_number=conv_number
    )
    plot_conv_pp_scalars(df_pivot, color_keys, color_dict, unit_dict)
