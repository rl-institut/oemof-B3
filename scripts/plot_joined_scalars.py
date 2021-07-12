import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import OrderedDict
import oemoflex.tools.plots as plots

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

var_name = q

names_dict = {"BE-biomass-st":"Biomass","BB-biomass-st":"Biomass",
              "BE-electricity-curtailment":"El. curtailment","BB-electricity-curtailment":"El. Curtailment",
              "BE-electricity-demand":"El demand","BB-electricity-demand":"El. Demand",
              "BE-electricity-liion-battery":"Liion Battery","BB-electricity-liion-battery":"Liion Battery",
              "BE-electricity-shortage":"El. shortage","BB-electricity-shortage":"El. Shortage",
              "BE-BB-electricity-transmission":"El. Transmission",
              "BE-ch4-gt": "CH4", "BB-ch4-gt": "CH4",
              "BE-solar-pv":"PV","BB-solar-pv":"PV",
              "BE-wind-onshore":"Wind on","BB-wind-onshore":"Wind on",
              }

unit_dict = {"capacity":"W"}

# load colors dict which also determines the ordering
colors_csv = pd.read_csv("colors.csv", header=[0], index_col=[0])
colors_csv = colors_csv.T
colors_odict = OrderedDict()
for i in colors_csv.columns:
    colors_odict[i] = colors_csv.loc["Color", i]

# import data
data_path = r"C:\Users\meinm\Documents\Git\oemof-B3\results\joined_scenarios\examples\scalars.csv"
scalars = pd.read_csv(data_path)

# select data with chosen var_name
selected_scalar_data = scalars[scalars['var_name'] == var_name]


def prepare_scalar_data(df, colors_odict, names_dict):
    # rename
    df = df.copy()
    df["name"] = df["name"].replace(names_dict)
    # pivot
    df_pivot = pd.pivot_table(df, index=["scenario","region"], columns="name", values="var_value")

    # cannot remove cells with replace 0 with nan and remove it because it can be 0 and should still be plotted, e.g. storage_capacity
    #pv.replace({0:np.nan}, inplace=True)
    #pv.dropna(axis = "index", how="all", inplace=True)
    #pv.dropna(axis = "columns", how="all", inplace=True)

    # define ordering and assign color
    order = list(colors_odict)
    colors=[]
    concrete_order=[]
    for i in order:
        if i not in df_pivot.columns:
            continue
        colors.append(colors_odict[i])
        concrete_order.append(i)
    df_pivot = df_pivot[concrete_order]

    return df_pivot, colors


def plot_scalars(df, colors, unit_dict, var_name):

    # Create figure with a subplot for each scenario with a relative width
    # proportionate to the number of regions
    scenarios = df.index.levels[0]
    nplots = scenarios.size
    plots_width_ratios = [df.xs(scenario).index.size for scenario in scenarios]
    fig, axes = plt.subplots(nrows=1, ncols=nplots, sharey=True, figsize=(12, 6),
                             gridspec_kw=dict(width_ratios=plots_width_ratios, wspace=0))

    # Loop through array of axes to create grouped bar chart for each scenario
    alpha = 0.3  # used for grid lines, bottom spine and separation lines between scenarios
    for scenario, ax in zip(scenarios, axes):
        # df.xs() Return cross-section from the Series/DataFrame. Here: return data of one scenario.
        df_scenario = df.xs(scenario)
        # apply EngFormatter
        if unit_dict[var_name] == "W":
            ax, df_scenario = plots.eng_format(ax, df_scenario, "W", 1000)

        # Create bar chart with grid lines and no spines except bottom one
        df_scenario.plot.bar(ax=ax, legend=None, zorder=2, color=colors, width=0.8, stacked=False)
        ax.grid(axis='y', zorder=1, color='black', alpha=alpha)
        for spine in ['top', 'left', 'right']:
            ax.spines[spine].set_visible(False)
        ax.spines['bottom'].set_alpha(alpha)

        # Set and place x labels for scenarios
        ax.set_xlabel(scenario)
        ax.xaxis.set_label_coords(x=0.5, y=-0.2)

        # Format major tick labels for region names: note that long names are
        # rewritten on two lines.
        ticklabels = [name.replace(' ', '\n') if len(name) > 10 else name
                      for name in df.xs(scenario).index]
        ax.set_xticklabels(ticklabels, rotation=0, ha='center')

        ax.tick_params(axis='both', length=0, pad=7)

        # Set and format minor tick marks for separation lines between scenarios: note
        # that except for the first subplot, only the right tick mark is drawn to avoid
        # duplicate overlapping lines so that when an alpha different from 1 is chosen
        # (like in this example) all the lines look the same
        if ax.get_subplotspec().is_first_col():
            ax.set_xticks([*ax.get_xlim()], minor=True)
        else:
            ax.set_xticks([ax.get_xlim()[1]], minor=True)
        ax.tick_params(which='minor', length=55, width=0.8, color=[0, 0, 0, alpha])

    # Add legend using the labels and handles from the last subplot
    fig.legend(*ax.get_legend_handles_labels(), frameon=False,)

    fig.suptitle(var_name + ' by scenario and region', y=1.02, size=14)

    plt.tight_layout()
    plt.savefig(var_name + ".png",bbox_inches='tight')


# prepare data
print(selected_scalar_data)
prepared_scalar_data, colors = prepare_scalar_data(df=selected_scalar_data, colors_odict=colors_odict, names_dict=names_dict)
print(prepared_scalar_data)
# plot data
plot_scalars(df = prepared_scalar_data, colors=colors, unit_dict=unit_dict, var_name=var_name)
plt.show()