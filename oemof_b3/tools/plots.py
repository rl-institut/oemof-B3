import logging

import matplotlib.pyplot as plt
import numpy as np
import oemoflex.tools.plots as plots
import pandas as pd
from oemoflex.tools.plots import plot_grouped_bar

from oemof_b3.config import config
from oemof_b3.config.config import COLORS, LABELS, load_yaml
from oemof_b3.tools import data_processing as dp

logger = config.add_snake_logger("data_processing")

MW_TO_W = 1e6
IGNORE_DROP_LEVEL = config.settings.plot_scalar_results.ignore_drop_level


def aggregate_regions(df):
    # this is a work-around to use the dataprocessing function for postprocessed data,
    # which is in a similar but not in the same format as preprocessed oemof_b3 resources.
    _df = df.copy()
    _df.reset_index(inplace=True)
    _df = _df.rename(columns={"scenario": "scenario_key"})
    agg_method = {
        "var_value": sum,
        "name": lambda x: "None",
    }
    _df = dp.aggregate_scalars(_df, "region", agg_method=agg_method)
    _df = _df.rename(columns={"scenario_key": "scenario"})
    _df["name"] = _df.apply(lambda x: x["carrier"] + "-" + x["tech"], 1)
    _df = _df.set_index("scenario")
    return _df


def draw_standalone_legend(c_dict):
    import matplotlib.patches as mpatches

    fig = plt.figure(figsize=(14, 14))
    patches = [
        mpatches.Patch(color=color, label=label) for label, color in c_dict.items()
    ]
    fig.legend(
        patches,
        c_dict.keys(),
        loc="center",
        ncol=4,
        fontsize=14,
        frameon=False,
    )
    plt.tight_layout()
    return fig


def set_scenario_labels(df):
    """Replaces scenario name with scenario label if possible"""

    def get_scenario_label(scenario):
        try:
            scenario_settings = load_yaml(f"scenarios/{scenario}.yml")
        except FileNotFoundError:
            return scenario
        return scenario_settings.get("label", scenario)

    df.index = df.index.map(get_scenario_label)
    return df


def prepare_scalar_data(
    df, colors_odict, labels_dict, conv_number, ignore_drop_level, tolerance=1e-3
):
    # drop data that is almost zero
    def _drop_near_zeros(df, tolerance):
        df = df.loc[abs(df["var_value"]) > tolerance]
        return df

    df = _drop_near_zeros(df, tolerance)

    if df.empty:
        return df

    # remember order of scenarios
    scenario_order = df.index.unique()

    # pivot
    df_pivot = pd.pivot_table(
        df,
        index=["scenario_key", "region", "var_name"],
        columns="name",
        values="var_value",
    )

    # restore order of scenarios after pivoting
    df_pivot = df_pivot.reindex(scenario_order, level="scenario_key")

    def drop_constant_multiindex_levels(df, ignore_drop_level=False):
        _df = df.copy()
        drop_levels = [
            name for name in _df.index.names if len(_df.index.unique(name)) <= 1
        ]
        if ignore_drop_level and ignore_drop_level in drop_levels:
            drop_levels.remove(ignore_drop_level)
        _df.index = _df.index.droplevel(drop_levels)
        return _df

    # Drop levels that are all the same, e.g. 'ALL' for aggregated regions
    df_pivot = drop_constant_multiindex_levels(df_pivot, ignore_drop_level)

    # rename and aggregate duplicated columns
    df_pivot = plots.map_labels(df_pivot, labels_dict)
    df_pivot = df_pivot.groupby(level=0, axis=1).sum()

    # define ordering and use concrete_order as keys for colors_odict in plot_scalars
    def sort_by_ranking(to_sort, order):
        ranking = {key: i for i, key in enumerate(order)}
        try:
            concrete_order = [ranking[key] for key in to_sort]
        except KeyError as e:
            raise KeyError(f"Missing label for label {e}")

        sorted_list = [x for _, x in sorted(zip(concrete_order, to_sort))]

        return sorted_list

    sorted_labels = sort_by_ranking(df_pivot.columns, colors_odict)

    df_pivot = df_pivot[sorted_labels]

    # convert data to SI-Units
    if conv_number is not None:
        df_pivot *= conv_number

    return df_pivot


def add_vertical_line_in_plot(ax, position, linewidth=1, color="black"):
    r"""
    Add vertical line to axes.
    """
    spacing = 1

    # Plot vertical line on secondary x-axis
    ax.axvline(x=(position - 0.5) * spacing, color=color, linewidth=linewidth)


class ScalarPlot:
    def __init__(self, scalars):
        self.scalars = scalars
        self.selected_scalars = None
        self.prepared_scalar_data = None
        self.plotted = False

    def select_data(self, **kwargs):
        self.selected_scalars = self.scalars.copy()
        for key, value in kwargs.items():
            self.selected_scalars = dp.filter_df(self.selected_scalars, key, value)

        if self.selected_scalars.empty:
            logger.info("No data to plot.")

        return self.selected_scalars

    def prepare_data(self, agg_regions=False):

        self.prepared_scalar_data = self.selected_scalars.copy()

        if agg_regions:
            self.prepared_scalar_data = aggregate_regions(self.prepared_scalar_data)

        self.prepared_scalar_data = prepare_scalar_data(
            df=self.prepared_scalar_data,
            colors_odict=COLORS,
            labels_dict=LABELS,
            conv_number=MW_TO_W,
            ignore_drop_level=IGNORE_DROP_LEVEL,
        )

        return self.prepared_scalar_data

    def swap_levels(self, swaplevels=(0, 1)):

        if self.prepared_scalar_data is None:
            logger.warning("No prepared data found")

        elif not isinstance(self.prepared_scalar_data.index, pd.MultiIndex):
            logger.warning("Index is no  pandas MultiIndex. Cannot swap levels")

        else:
            self.prepared_scalar_data = self.prepared_scalar_data.swaplevel(*swaplevels)

        return self.prepared_scalar_data

    def draw_plot(self, unit, title):
        # do not plot if the data is empty or all zeros.
        if (
            self.prepared_scalar_data.empty
            or (self.prepared_scalar_data == 0).all().all()
        ):
            logger.warning("Data is empty or all zero")
            return None, None
        print(self.prepared_scalar_data)
        fig, ax = plt.subplots()
        plot_grouped_bar(ax, self.prepared_scalar_data, COLORS, unit=unit, stacked=True)
        ax.set_title(title)
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
        )
        set_hierarchical_xlabels(self.prepared_scalar_data.index)
        # Put a legend below current axis
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.18),
            fancybox=True,
            ncol=4,
            fontsize=14,
        )

        self.plotted = True

        return fig, ax

    def draw_subplots(
        self, unit, title, figsize=None, facet_level=0, rotation=45, ha="right"
    ):
        # do not plot if the data is empty or all zeros.
        if (
            self.prepared_scalar_data.empty
            or (self.prepared_scalar_data == 0).all().all()
        ):
            logger.warning("Data is empty or all zero")
            return None, None

        # Set fig size to default size if no fig size is passed
        if not figsize:
            figsize = plt.rcParams.get("figure.figsize")

        fig = plt.figure(figsize=figsize)

        def set_index_full_product(df):
            r"""
            Ensures that the the MultiIndex covers the full product of the levels.
            """
            if not isinstance(df, pd.MultiIndex):
                return df

            # df.index.levels messes up the order of the levels, but we want to keep it
            ordered_levels = [
                df.index.get_level_values(level).unique()
                for level in range(df.index.nlevels)
            ]

            index_full_product = pd.MultiIndex.from_product(ordered_levels)

            return df.reindex(index_full_product)

        self.prepared_scalar_data = set_index_full_product(self.prepared_scalar_data)

        grouped = self.prepared_scalar_data.groupby(level=facet_level)
        n_facets = len(grouped)

        for i, (facet_name, df) in enumerate(grouped):
            df = df.reset_index(level=[0], drop=True)
            df = df.fillna(0)
            df = df.loc[:, (df != 0).any(axis=0)]

            ax = fig.add_subplot(n_facets, 1, i + 1)

            if not df.empty:
                plot_grouped_bar(ax, df, COLORS, unit=unit, stacked=True)
            else:
                logger.warning("Data is empty - nothing to plot!")

            ax.set_title(facet_name)

            # rotate xticklabels
            labels = ax.get_xticklabels()
            for lb in labels:
                lb.set_rotation(rotation)
                lb.set_ha(ha)

            ax.legend(
                loc="center left",
                bbox_to_anchor=(1.0, 0, 0, 1),
                fancybox=True,
                ncol=1,
                fontsize=14,
            )
            ax.tick_params(
                "both", labelsize=config.settings.plot_scalar_results.tick_label_size
            )

        fig.suptitle(title, fontsize="x-large")

        self.plotted = True

        # show only ticklabels of last plot
        axs = fig.get_axes()

        for ax in axs[:-1]:
            ax.tick_params(labelbottom=False)

        return fig, axs

    def save_plot(self, output_path_plot):
        if self.plotted:
            plt.savefig(output_path_plot, bbox_inches="tight")
            logger.info(f"Plot has been saved to: {output_path_plot}.")


def get_auto_bar_yinterval(index, space_per_letter, rotation):
    # set intervals according to maximal length of labels
    label_len_max = [
        max([len(v) for v in index.get_level_values(i)]) for i in index.names
    ]

    bar_yinterval = [space_per_letter * i for i in label_len_max][:-1]

    # if there is rotation, reduce the interval
    bar_yinterval = [
        interval * abs(np.sin(rotation)) + space_per_letter
        for interval, rotation in zip(bar_yinterval, rotation)
    ]

    return bar_yinterval


# TODO: This function could move to oemoflex once it is more mature
def set_hierarchical_xlabels(
    index,
    ax=None,
    hlines=False,
    bar_xmargin=0.1,
    bar_yinterval=None,
    rotation=0,
    ha=None,
):
    r"""
    adapted from https://linuxtut.com/ 'Draw hierarchical axis labels with matplotlib + pandas'
    """
    from itertools import groupby

    from matplotlib.lines import Line2D

    ax = ax or plt.gca()

    if not isinstance(index, pd.MultiIndex):
        logging.info(
            "Index is not a pd.MultiIndex. Need a multiindex to set hierarchical labels."
        )
        return None

    labels = ax.set_xticklabels([s for *_, s in index])

    transform = ax.get_xaxis_transform()

    n_levels = index.nlevels
    n_intervals = len(index.codes) - 1

    if isinstance(rotation, (float, int)):
        rotation = [rotation] * n_levels

    elif len(rotation) != n_levels:
        raise ValueError(
            "Number of values for rotation must be 1 or match number of index levels."
        )

    if bar_yinterval is None:
        SPACE_PER_LETTER = 0.05
        bar_yinterval = get_auto_bar_yinterval(index, SPACE_PER_LETTER, rotation)

    if isinstance(bar_yinterval, (float, int)):
        bar_yinterval = [bar_yinterval] * n_intervals

    elif len(bar_yinterval) != n_intervals:
        raise ValueError(
            "Must either pass one value for bar_yinterval or a list of values that matches the"
            "number of index levels minus one."
        )

    if rotation[0] != 0:
        for lb in labels:
            lb.set_rotation(rotation[0])
            lb.set_ha(ha)

    for i in range(1, n_levels):
        bar_ypos = -sum(bar_yinterval[:i])
        xpos0 = -0.5  # Coordinates on the left side of the target group

        for (*_, code), codes_iter in groupby(zip(*index.codes[:-i])):
            xpos1 = xpos0 + sum(
                1 for _ in codes_iter
            )  # Coordinates on the right side of the target group
            ax.text(
                (xpos0 + xpos1) / 2,
                bar_ypos - 0.02,
                index.levels[-i - 1][code],
                transform=transform,
                rotation=rotation[i],
                ha="center",
                va="top",
            )
            if hlines:
                ax.add_line(
                    Line2D(
                        [xpos0 + bar_xmargin, xpos1 - bar_xmargin],
                        [bar_ypos],
                        transform=transform,
                        color="k",
                        clip_on=False,
                    )
                )
            xpos0 = xpos1
