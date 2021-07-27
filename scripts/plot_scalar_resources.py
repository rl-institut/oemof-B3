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

    german_labels = {
        "Biomass": "Biomasse",
        "CH4": "Erdgas",
        "Hard coal": "Steinkohle",
        "Oil": "Öl",
        "Lignite": "Braunkohle",
        "Other": "Andere",
    }

    # User input
    var_name = "capacity_net_el"
    conv_number = 1000 * 1000

    def prepare_conv_pp_scalars(var_name, conv_number, carrier_dict=carrier_dict):
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
        german_color_dict = {}
        for key in color_keys:
            german_color_dict[german_labels[key]] = colors_odict[key]
        df_pivot.rename(columns=german_labels, inplace=True)
        german_color_keys = df_pivot.columns
        # convert to SI unit:
        if conv_number:
            df_pivot *= conv_number

        return df_pivot, german_color_keys, german_color_dict

    def plot_scalar_resources(df, color_keys, color_dict, unit_dict):
        alpha = 0.3
        fontsize = 14
        plt.rcParams.update({"font.size": fontsize})

        fig, ax = plt.subplots(figsize=(12, 6))
        # apply EngFormatter if power is plotted
        if unit_dict[var_name] == "W":
            ax = plots.eng_format(ax, "W")
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

    df_pivot, german_color_keys, german_color_dict = prepare_conv_pp_scalars(
        var_name=var_name, conv_number=conv_number
    )
    plot_scalar_resources(df_pivot, german_color_keys, german_color_dict, unit_dict)
