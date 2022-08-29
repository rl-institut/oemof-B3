import os
import sys
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import oemof_b3.tools.data_processing as dp
import oemoflex.tools.plots as plots
from oemof_b3.config.config import LABELS, COLORS, add_snake_logger
from datetime import datetime


def get_non_normalized_profile(
    non_normalized_profile, profile, demands, scenario, region, carrier
):
    demand = dp.filter_df(demands, "region", region)
    demand = dp.filter_df(demand, "carrier", carrier.split("-")[0])
    demand = dp.filter_df(demand, "scenario_key", scenario)

    demand = demand["var_value"].values.sum()

    non_normalized_profile[carrier + "_" + region] = profile[carrier] * demand

    return non_normalized_profile


if __name__ == "__main__":
    resources = sys.argv[1]
    scalars = sys.argv[2]
    output_path = sys.argv[3]

    logfile = sys.argv[4]

    logger = add_snake_logger(logfile, "plot_storage_levels")

    REGION = "B"
    TIMEINDEX_START = "2017-01-01 00:00:00"
    H_PER_DAY = 24
    DAYS = 14

    # Load all timeseries resources that has "load" in its nam
    paths = [
        os.path.join(resources, path)
        for path in os.listdir(resources)
        if "ts_load" in os.path.basename(path) and ".csv" in os.path.basename(path)
    ]

    # create the directory plots where all plots are saved if it does not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Load yearly demands
    sc = dp.load_b3_scalars(scalars)
    demands = dp.filter_df(sc, "type", "load")

    # Load timeseries with normalized profiles
    ts = dp.multi_load_b3_timeseries(paths)

    # Filter timeseries
    ts = dp.filter_df(ts, "timeindex_start", TIMEINDEX_START)

    # Get all scenario keys from timeseries
    scenario_keys = ts["scenario_key"].unique()

    # Get all regions from timeseries
    regions = ts["region"].unique()

    # Get all regions from timeseries
    carriers = ts["var_name"].unique()

    year = TIMEINDEX_START.split("-")[0]
    timeframe = [
        (f"{year}-01-01 00:00:00", f"{year}-12-31 23:00:00"),
        (f"{year}-01-01 00:00:00", f"{year}-01-31 23:00:00"),
        (f"{year}-07-01 00:00:00", f"{year}-07-31 23:00:00"),
    ]

    for scenario in scenario_keys:
        if scenario != "ALL":
            df_demand_profiles = pd.DataFrame()
            for start_date, end_date in timeframe:
                for carrier in carriers:
                    # Create DataFrame with only carrier data
                    ts_scenario_carrier = ts.copy()
                    ts_scenario_carrier = dp.filter_df(
                        ts_scenario_carrier, "scenario_key", [scenario, "ALL"]
                    )
                    ts_scenario_carrier = dp.filter_df(
                        ts_scenario_carrier, "var_name", carrier
                    )

                    if len(ts_scenario_carrier) != len(regions):
                        raise ValueError(
                            f"There probably is multiple data of {carrier} and scenario key"
                            f" {scenario}. "
                            f"Please provide only one time series per region, scenario key and "
                            f"carrier."
                        )

                    # Add empty Dataframe for non normalized profiles
                    non_normalized_profile = pd.DataFrame()
                    for region in regions:
                        # Create DataFrame with only region data
                        ts_scenario_carrier_region = ts_scenario_carrier.copy()
                        ts_scenario_carrier_region = dp.filter_df(
                            ts_scenario_carrier_region, "region", region
                        )
                        ts_scenario_carrier_region = dp.unstack_timeseries(
                            ts_scenario_carrier_region
                        )

                        # Write non normalized data in non_normalized_profile
                        non_normalized_profile = get_non_normalized_profile(
                            non_normalized_profile,
                            ts_scenario_carrier_region,
                            demands,
                            scenario,
                            region,
                            carrier,
                        )

                    # Aggregate columns of profile region wise
                    df_demand_profiles[
                        carrier.split("-profile")[0]
                    ] = non_normalized_profile.sum(axis=1)

                    df_demand_profiles_filtered = plots.filter_timeseries(
                        df_demand_profiles, start_date, end_date
                    )

                # Plot profiles
                number_of_subplots = len(df_demand_profiles_filtered.columns)
                fig, axs = plt.subplots(number_of_subplots, 1, figsize=(12, 5))

                for column in df_demand_profiles_filtered.columns:
                    if column in LABELS.keys():
                        df_demand_profiles_filtered.rename(
                            columns={column: LABELS[column]}, inplace=True
                        )

                for ax, col in zip(axs, df_demand_profiles_filtered.columns):
                    plots.lineplot(
                        ax=ax,
                        df=df_demand_profiles_filtered[[col]].copy(),
                        colors_odict=COLORS,
                    )

                    # format x-axis representing the dates
                    plt.gca().xaxis.set_major_formatter(
                        mdates.DateFormatter("%Y-%m-%d")
                    )
                    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())

                    handles, labels = ax.get_legend_handles_labels()

                    ax.legend(
                        handles=handles,
                        labels=labels,
                        loc="center left",
                        bbox_to_anchor=(1.0, 0, 0, 1),
                        fancybox=True,
                        ncol=4,
                        fontsize=14,
                    )

                    ax.tick_params(axis="x", labelsize=14)
                    ax.tick_params(axis="y", labelsize=14)
                    ax.axes.get_xaxis().set_visible(False)

                fig.text(
                    0.02,
                    0.5,
                    "Leistung",
                    ha="center",
                    va="center",
                    rotation="vertical",
                    fontdict={"size": 17},
                )
                ax.axes.get_xaxis().set_visible(True)
                # remove year from xticks
                formatter = mdates.DateFormatter("%m-%d")
                ax.xaxis.set_major_formatter(formatter)
                locator = mdates.AutoDateLocator()
                ax.xaxis.set_major_locator(locator)

                plt.xlabel("Datum (mm-dd)", loc="center", fontdict={"size": 17})

                fig.tight_layout(rect=(0.025, 0, 1, 1))

                date_diff = datetime.strptime(
                    start_date, "%Y-%m-%d %H:%M:%S"
                ) - datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                if abs(date_diff.days) >= 31:
                    file_name = (
                        "ts_load_"
                        + scenario
                        + "_"
                        + start_date[5:7]
                        + "-"
                        + end_date[5:7]
                        + ".pdf"
                    )
                    plt.savefig(
                        os.path.join(output_path, file_name), bbox_inches="tight"
                    )
                    file_name = (
                        "ts_load_"
                        + scenario
                        + "_"
                        + start_date[5:7]
                        + "-"
                        + end_date[5:7]
                        + ".png"
                    )
                    plt.savefig(
                        os.path.join(output_path, file_name), bbox_inches="tight"
                    )
                else:
                    file_name = "ts_load_" + scenario + "_" + start_date[5:7] + ".pdf"
                    plt.savefig(
                        os.path.join(output_path, file_name), bbox_inches="tight"
                    )
                    file_name = "ts_load_" + scenario + "_" + start_date[5:7] + ".png"
                    plt.savefig(
                        os.path.join(output_path, file_name), bbox_inches="tight"
                    )
