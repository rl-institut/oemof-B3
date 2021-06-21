import os
import sys

import pandas as pd
import plotly.express as px


def prepare_parallel_coord_data(scalars, var_value):
    idx = pd.IndexSlice

    scalars_in = scalars.copy()

    # select var_value
    values = scalars_in.loc[idx[:, :, var_value], :]

    # drop other columns (region, type, carrier, tech)
    values = values.loc[:, "var_value"]

    # reshape
    values = values.unstack([1, 2])
    values.reset_index(inplace=True)
    values.columns = values.columns.droplevel(1)

    return values


if __name__ == "__main__":
    joined = sys.argv[1]

    plotted_joined = sys.argv[2]

    # create the directory where all joined scenario plots are saved
    if not os.path.exists(plotted_joined):
        os.makedirs(plotted_joined)

    scalars = pd.read_csv(joined, index_col=[0, 1, 2])

    var_value = "capacity"

    capacity = prepare_parallel_coord_data(scalars, var_value)

    # Hack to get numeric indices for the colors
    capacity["scenario"] = capacity.index

    fig = px.parallel_coordinates(
        capacity,
        color="scenario",
        color_continuous_scale=px.colors.diverging.Tealrose,
        color_continuous_midpoint=2,
    )

    fig.write_html(
        file=os.path.join(plotted_joined, "parallel_coords_interactive.html"),
        # include_plotlyjs=False,
        # full_html=False
    )
