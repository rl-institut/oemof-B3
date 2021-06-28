import os
import sys

import pandas as pd
import plotly.express as px


def prepare_parallel_coord_data(scalars):

    _scalars = scalars.copy()

    # drop other columns (region, type, carrier, tech)
    _scalars = _scalars.set_index(['scenario', 'carrier', 'tech', 'var_name'])

    _scalars = _scalars.loc[:, "var_value"]

    # reshape
    _scalars = _scalars.unstack(['carrier', 'tech', 'var_name'])

    _scalars.reset_index(inplace=True)

    # flatten columns
    _scalars.columns = _scalars.columns.map(lambda x: '-'.join(x))

    return _scalars


def aggregate_regions(scalars):

    _scalars = scalars.copy()

    _scalars = _scalars.groupby(['scenario', 'carrier', 'tech', 'var_name']).sum()

    _scalars.reset_index(inplace=True)

    return _scalars


if __name__ == "__main__":
    joined = sys.argv[1]

    plotted_joined = sys.argv[2]

    # create the directory where all joined scenario plots are saved
    if not os.path.exists(plotted_joined):
        os.makedirs(plotted_joined)

    scalars = pd.read_csv(joined)

    # aggregate regions
    scalars = aggregate_regions(scalars)

    # select var_name
    var_name = "capacity"

    selected_scalars = scalars.loc[scalars['var_name'] == var_name]

    par_coord_scalars = prepare_parallel_coord_data(selected_scalars)

    fig = px.parallel_coordinates(
        par_coord_scalars,
        color=par_coord_scalars.index,
        color_continuous_scale=px.colors.diverging.Tealrose,
    )

    fig.write_html(
        file=os.path.join(plotted_joined, "parallel_coords_interactive.html"),
        # include_plotlyjs=False,
        # full_html=False
    )
