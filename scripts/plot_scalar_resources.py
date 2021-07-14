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
        df = pd.read_csv(path, sep=";", index_col=0)
        return df

    # Load scalar data
    scalars = load_scalars(resources)

    # TODO: filter

    # TODO: pivot

    # plot
    fig, ax = plt.subplots()

    scalars.plot.bar(ax=ax)

    plt.savefig(target)
