import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import oemoflex.tools.plots as plots
from oemoflex.tools.plots import colors_odict

if __name__ == "__main__":
    scalars_path = sys.argv[1]

    target = sys.argv[2]

    target_dir = os.path.dirname(target)

    # create the directory plotted where all plots are saved
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    def load_scalars(path):
        df = pd.read_csv(path, sep=",", index_col=0)
        return df

    # Load scalar data
    scalars = load_scalars(scalars_path)

    # import data
    #data_path = r"C:\Users\meinm\Documents\Git\oemof-B3\results\joined_scenarios\examples\scalars.csv"
    #scalars = pd.read_csv(data_path)

    q = "capacity"
    w = "flow_in_electricity_from_bus"
    e = "flow_in_electricity_to_bus"
    r = "flow_out_electricity_from_bus"
    t = "flow_out_electricity_to_bus"
    z = "transmission_losses"

    u = "flow_in_biomass"
    i = "flow_out_electricity"
    o = "invest_out_electricity"
    p = "summed_variable_costs_in_biomass"
    a = "summed_variable_costs_out_electricity"
    s = "flow_in_electricity"
    d = "invest"
    f = "invest_in_electricity"
    g = "storage_capacity"
    h = "storage_losses"
    j = "flow_in_ch4"
    k = "summed_variable_costs_in_ch4"

    # User input
    var_name = q
    regions = ["BB", "BE"]  # BE_BB
    conv_number = 1000

    unit_dict = {"capacity": "W"}

    # select data with chosen var_name
    selected_scalar_data = scalars[scalars["var_name"] == var_name]
    selected_scalar_data = selected_scalar_data[
        selected_scalar_data["region"].isin(regions)
    ]

    def prepare_scalar_data(df, colors_odict, conv_number=conv_number):
        # pivot
        df_pivot = pd.pivot_table(
            df, index=["scenario", "region"], columns="name", values="var_value"
        )
        # rename and aggregate duplicated columns
        df_pivot=plots.map_labels(df_pivot)
        df_pivot = df_pivot.groupby(level=0, axis=1).sum()
        # define ordering and use concrete_order as keys for colors_odict in plot_scalars()
        order = list(colors_odict)
        concrete_order = []
        for i in order:
            if i not in df_pivot.columns:
                continue
            concrete_order.append(i)
        df_pivot = df_pivot[concrete_order]

        # convert data to SI-Units
        if conv_number is not None:
            df_pivot *= conv_number

        return df_pivot, concrete_order


    def plot_scalars(df, var_name, color_keys, unit_dict=unit_dict, fontsize=14):
        plt.rcParams.update({"font.size": fontsize})
        # Create figure with a subplot for each scenario with a relative width
        # proportionate to the number of regions
        scenarios = df.index.levels[0]
        nplots = scenarios.size
        plots_width_ratios = [df.xs(scenario).index.size for scenario in scenarios]
        fig, axes = plt.subplots(
            nrows=1,
            ncols=nplots,
            sharey=True,
            figsize=(12, 6),
            gridspec_kw=dict(width_ratios=plots_width_ratios, wspace=0),
        )
        # make sure axes is in iterable object
        # CHANGE BACK to OLD version!
        if isinstance(axes, np.ndarray):
            axes_list = axes
        else:
            axes_list = []
            axes_list.append(axes)

        # Loop through array of axes to create grouped bar chart for each scenario
        alpha = (
            0.3  # used for grid lines, bottom spine and separation lines between scenarios
        )
        for scenario, ax in zip(scenarios, axes_list):
            # df.xs() Return cross-section from the Series/DataFrame. Here: return data of one scenario.
            df_scenario = df.xs(scenario)
            # apply EngFormatter if power is plotted
            if unit_dict[var_name] == "W":
                ax = plots.eng_format(ax, "W")

            # Create bar chart with grid lines and no spines except bottom one
            df_scenario.plot.bar(
                ax=ax,
                legend=None,
                zorder=2,
                color=[colors_odict[key] for key in color_keys],
                width=0.8,
                stacked=False,
            )
            ax.grid(axis="y", zorder=1, color="black", alpha=alpha)
            for spine in ["top", "left", "right"]:
                ax.spines[spine].set_visible(False)
            ax.spines["bottom"].set_alpha(alpha)

            # Set and place x labels for scenarios
            ax.set_xlabel(scenario)
            ax.xaxis.set_label_coords(x=0.5, y=-0.2)

            # Format major tick labels for region names: note that long names are
            # rewritten on two lines.
            ticklabels = [
                name.replace(" ", "\n") if len(name) > 10 else name
                for name in df.xs(scenario).index
            ]
            ax.set_xticklabels(ticklabels, rotation=0, ha="center")

            ax.tick_params(axis="both", length=0, pad=7)

            # Set and format minor tick marks for separation lines between scenarios: note
            # that except for the first subplot, only the right tick mark is drawn to avoid
            # duplicate overlapping lines so that when an alpha different from 1 is chosen
            # (like in this example) all the lines look the same
            if ax.get_subplotspec().is_first_col():
                ax.set_xticks([*ax.get_xlim()], minor=True)
            else:
                ax.set_xticks([ax.get_xlim()[1]], minor=True)
            ax.tick_params(which="minor", length=55, width=0.8, color=[0, 0, 0, alpha])

        # Add legend using the labels and handles from the last subplot
        fig.legend(*ax.get_legend_handles_labels(), frameon=True, framealpha=1)

        #plt.ylabel(ylabel=ylabel)

        plt.tight_layout()
        plt.savefig("joined_scalars.png", bbox_inches="tight")
        #plt.savefig(target, bbox_inches="tight")


    # prepare data
    prepared_scalar_data, colors = prepare_scalar_data(
        df=selected_scalar_data, colors_odict=colors_odict,
    )
    # plot data
    plot_scalars(
        df=prepared_scalar_data,
        color_keys=colors,
        unit_dict=unit_dict,
        var_name=var_name,
    )
