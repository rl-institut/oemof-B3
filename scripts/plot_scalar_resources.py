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

    def unstack_scalars(df):
        _df = df.copy()
        _df = _df.unstack("var_name")

        return _df

    scalars.set_index(["region", "carrier", "tech", "var_name"], inplace=True)
    scalars = scalars["var_value"]

    # There are duplicate entries for those capacities where we distinguish chp=yes/no
    # TODO: Rethink this
    scalars = scalars.loc[scalars.index.duplicated()]

    # unstack
    scalars_prepared = unstack_scalars(scalars)

    # filter
    scalars_prepared = scalars_prepared["capacity_net_el"]

    # Set numeric datatype
    scalars_prepared = scalars_prepared.astype(float)

    # plot
    fig, ax = plt.subplots()

    scalars_prepared.plot.bar(ax=ax)

    plt.tight_layout()

    plt.savefig(target)
