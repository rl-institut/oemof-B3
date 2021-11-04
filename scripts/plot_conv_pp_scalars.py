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
unit = "W"


# GENERAL
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


def prepare_conv_pp_scalars(
    df_conv_pp_scalars, var_name, conv_number, carrier_dict=carrier_dict
):
    r"""
    This function converts scalar data in oeomof-b3 format to a format that can be passed to
    `plot_grouped_bar` .

    It aggregates power plants with the same carrier.

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
    color_dict: dict
        contains colors for different carriers for plotting
    """
    # select var_name to be plotted
    selected_df = df_conv_pp_scalars[df_conv_pp_scalars["var_name"] == var_name].copy()

    # CONV_PP specific
    selected_df.loc[(selected_df["region"] != "Berlin"), "region"] = "Brandenburg"

    # aggregate carriers in regions
    selected_df_agg = dp.aggregate_scalars(
        df=selected_df, columns_to_aggregate=["tech"]
    )

    # capitalize carrier names
    selected_df_agg["carrier"].replace(carrier_dict, inplace=True)

    # convert to SI unit:
    if conv_number:
        selected_df_agg.loc[:, "var_value"] *= conv_number

    # Translate to German

    # apply pivot table
    df_pivot = pd.pivot_table(
        selected_df_agg,
        index=["region"],
        columns="carrier",
        values="var_value",
    )

    # colors
    if german_translation:
        german_color_dict = {}
        for key in df_pivot.columns:
            german_color_dict[german_labels[key]] = colors_odict[key]
        color_dict = german_color_dict
        df_pivot.rename(columns=german_labels, inplace=True)
    else:
        color_dict = colors_odict

    return df_pivot, color_dict


def plot_grouped_bar(ax, df, color_dict, unit):
    r"""
    This function plots scalar data as grouped bar plot. The index of the DataFrame
    will be interpreted as groups (e.g. regions), the columns as different categories (e.g. energy
    carriers) within the groups which will be plotted in different colors.

    Parameters
    ----------
    ax: matplotlib Axes object
        Axes to draw the plot.
    df: pd.DataFrame
        DataFrame with an index defining the groups and columns defining the bars of different color
        with in the group.
    color_dict: dict
        Dictionary defining colors of the categories
    unit: str
        Unit of the variables
    """
    alpha = 0.3
    fontsize = 14
    plt.rcParams.update({"font.size": fontsize})

    # apply EngFormatter if power is plotted
    ax = plots._eng_format(ax, unit)

    df.plot.bar(
        ax=ax,
        color=[color_dict[key] for key in df.columns],
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

    return ax


if __name__ == "__main__":
    resources = sys.argv[1]

    target = sys.argv[2]

    target_dir = os.path.dirname(target)

    # create the directory plotted where all plots are saved
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Load scalar data
    df_conv_pp_scalars = dp.load_b3_scalars(resources)

    df_pivot, color_dict = prepare_conv_pp_scalars(
        df_conv_pp_scalars=df_conv_pp_scalars,
        var_name=var_name,
        conv_number=conv_number,
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_grouped_bar(ax, df_pivot, color_dict, unit)

    plt.savefig(target, bbox_inches="tight")