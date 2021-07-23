r"""
Inputs
-------

Outputs
---------

Description
-------------

"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import oemoflex.tools.plots as plots
from oemoflex.tools.plots import colors_odict

if __name__ == "__main__":
    resources = sys.argv[1]

    target = sys.argv[2]

    target_dir = os.path.dirname(target)

    # create the directory plotted where all plots are saved
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    def load_scalars(path):
        df = pd.read_csv(path, sep=",", index_col=0)
        return df

    # Load scalar data
    scalars = load_scalars(resources)

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

    # User input
    var_name = "capacity_net_el"
    ylabel = "Leistung [MW]"

    def prepare_conv_pp_scalars(var_name, carrier_dict=carrier_dict):
        # select var_name to be plotted
        selected_df = scalars[scalars["var_name"] == var_name].copy()

        # CONV_PP specific
        selected_df.loc[(selected_df["region"] != "Berlin"), "region"] = "Brandenburg"
        # capitalize carrier names
        selected_df["carrier"].replace(carrier_dict, inplace=True)
        # aggregate carriers in regions
        selected_df_agg = selected_df.groupby(
            ["scenario", "region", "carrier", "var_name"]
        ).sum()
        selected_df_agg.reset_index(inplace=True)

        # apply pivot table
        df_pivot = pd.pivot_table(
            selected_df_agg,
            index=["region"],
            columns="carrier",
            values="var_value",
        )

        # colors
        color_keys = df_pivot.columns

        return df_pivot, color_keys

    def plot_scalar_resources(df, color_keys):
        alpha = 0.3
        fontsize = 14
        plt.rcParams.update({"font.size": fontsize})

        fig, ax = plt.subplots(figsize=(12,6))
        df.plot.bar(ax=ax,
                    color=[colors_odict[key] for key in color_keys],
                    width=0.8,
                    zorder=2,
                    stacked=False,
                    ylabel=ylabel,
                    rot=0
                    )

        for spine in ["top", "left", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_alpha(alpha)
        ax.tick_params(axis="both", length=0, pad=7)

        ax.grid(axis="y", zorder=1, color="black", alpha=alpha)
        ax.set_xlabel(xlabel=None)

        plt.legend(title=None)

        plt.tight_layout()
        plt.savefig(target, bbox_inches="tight")


    df_pivot, color_keys = prepare_conv_pp_scalars(var_name=var_name)
    plot_scalar_resources(df_pivot, color_keys)
