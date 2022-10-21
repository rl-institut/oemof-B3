r"""
Inputs
-------
resources : str
    ``results/_resources/{resource}.csv``: path of input file with data of prepared conventional
    power plant data as .csv
var_name : str
    Indicates the var_name which shall be plotted
target : str
    path of output file with plot

Outputs
---------
Plot of conventional power plant data

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
from oemof_b3.config.config import LABELS, COLORS
from oemof_b3.config import config

# User input
# converting from MW to W
UNIT = "W"
MW_TO_W = 1e6


def prepare_conv_pp_scalars(df_conv_pp_scalars, var_name, conv_number, label_mapping):
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

    Returns
    -------
    df_pivot : pandas.DataFrame
        Unique unit
    color_dict: dict
        contains colors for different carriers for plotting
    """
    # select var_name to be plotted
    selected_df = df_conv_pp_scalars[df_conv_pp_scalars["var_name"] == var_name].copy()

    assert not selected_df.empty, f"Variable name '{var_name}' not found in data."

    # CONV_PP specific
    selected_df.loc[(selected_df["region"] != "Berlin"), "region"] = "Brandenburg"

    # aggregate carriers in regions
    selected_df_agg = dp.aggregate_scalars(
        df=selected_df, columns_to_aggregate=["tech"]
    )

    # convert to SI unit:
    if conv_number:
        selected_df_agg.loc[:, "var_value"] *= conv_number

    selected_df_agg["carrier"].replace(label_mapping, inplace=True)

    # apply pivot table
    df_pivot = pd.pivot_table(
        selected_df_agg,
        index=["region"],
        columns="carrier",
        values="var_value",
    )

    return df_pivot


def plot_grouped_bar(ax, df, color_dict, unit, stacked=False):
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
    stacked : boolean
        Stack bars of a group. False by default.
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
        stacked=stacked,
        rot=0,
    )

    for spine in ["top", "left", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_alpha(alpha)
    ax.tick_params(axis="both", length=0, pad=7)

    ax.grid(axis="y", zorder=1, color="black", alpha=alpha)
    ax.set_xlabel(xlabel=None)
    ax.legend()
    plt.legend(title=None, frameon=True, framealpha=1)

    plt.tight_layout()

    return ax


if __name__ == "__main__":
    resources = sys.argv[1]

    var_name = sys.argv[2]

    target = sys.argv[3]

    target_dir = os.path.dirname(target)

    # create the directory plotted where all plots are saved
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Load scalar data
    df_conv_pp_scalars = dp.load_b3_scalars(resources)

    df_pivot = prepare_conv_pp_scalars(
        df_conv_pp_scalars=df_conv_pp_scalars,
        var_name=var_name,
        conv_number=MW_TO_W,
        label_mapping=LABELS,
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    # TODO: Check if oemoflex' function can be imported and used here
    plot_grouped_bar(ax, df_pivot, COLORS, UNIT)

    plt.savefig(target + config.settings.general.plot_filetype, bbox_inches="tight")
