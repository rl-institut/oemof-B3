# coding: utf-8
r"""
Inputs
-------
in_path1 : str
    ``raw/weatherdata``: path of input directory with weather data
in_path2 : str
    ``raw/distribution_households.csv``: path of input file with household distributions data
    as .csv
in_path3 : str
    ``raw/holidays.csv``: path of input file with holidays of all states in Germany as .csv
in_path4 : str
    ``raw/building_class.csv``: path of input file with building classes of all states in Germany
    as .csv
in_path5 : str
    ``raw/scalars/demands.csv``: path of scalar data as .csv
out_path1 : str
    ``results/_resources/scal_load_heat.csv``: path of output file with aggregated scalar data as
    .csv
out_path2 : str
    ``results/_resources/ts_load_heat.csv``: path of output file with timeseries data as .csv
logfile : str
    ``logs/{scenario}.log``: path to logfile

Outputs
---------
pandas.DataFrame
    with grouped and aggregated data of heat demands.
    Data is grouped by region, energy source, technology and chp capability and contains
    net capacity and efficiency.

Description
-------------
The script produces heat demand profiles using the demandlib.
For this purpose, it reads the scalar input data and filters them according to the corresponding
heat demand. By processing historical weather data as well as a household distribution in single-
and multi-family houses that is assumed to be constant and the holidays belonging to the evaluated
year, demandlib creates heat profiles, which are additionally normalized.
Since the consumers trade, commerce and services (german: Gewerbe, Handel und Dienstleistungen
(ghd)) and private household (hh) are processed individually by demandlib, they are also passed
individually in the scalar input data. The script summarizes the respective demand of the consumers
and stores it in scalar resources.
"""
import datetime
import itertools
import os
import sys

import numpy as np
import pandas as pd
from demandlib import bdew

import oemof_b3.tools.data_processing as dp
from oemof_b3.config import config


def get_shares_from_hh_distribution(path, region):
    """
    This function calculates the share of single family houses (Einfamilienhaus: efh)
    and multi-family houses (Mehrfamilienhaus: mfh) from the household distribution
    in input data

    Parameters
    ----------
    path : str
        Path to data

    region : str
        Region (eg. Brandenburg)

    Returns
    -------
    share_efh : float
        Share of efh in household distribution

    share_mfh : float
        Share of mfh in household distribution
    """
    # Get share of EFH and MFH from distribution of households
    distribution_hh = pd.read_csv(path)
    distribution_hh_reg = distribution_hh[distribution_hh["region"] == region]

    share_efh = (
        distribution_hh_reg["sfh"]
        / np.add(distribution_hh_reg["sfh"], distribution_hh_reg["mfh"])
    ).values[0]
    share_mfh = (
        distribution_hh_reg["mfh"]
        / np.add(distribution_hh_reg["sfh"], distribution_hh_reg["mfh"])
    ).values[0]

    return share_efh, share_mfh


def find_regional_files(path, region):
    """
    This function returns a list of file names in a directory that match the specified region.

    Parameters
    ----------
    path : str
        Path to data

    region : str
        Region (eg. Brandenburg)

    Returns
    -------
    files_region : list
        List of file names matching region
    """
    files_region = [file for file in os.listdir(path) if f"_{region}_" in file]
    files_region = sorted(files_region)

    if not files_region:
        raise FileNotFoundError(
            f"No data of region {region} could be found in directory: {path}."
        )

    return files_region


def get_year(file_name):
    """
    This function returns a year from file name

    Parameters
    ----------
    file_name : str
        Name of file with year in it

    Returns
    -------
    year : int
        Year
    """
    # Add array with years to be searched for in file name
    years_search_array = np.arange(1990, 2051)
    newline = "\n"

    year_in_file = [
        year_searched
        for year_searched in years_search_array
        if str(year_searched) in file_name
    ]
    if len(year_in_file) == 1:
        year = year_in_file[0]
    else:
        raise ValueError(
            f"Your file {file_name} is missing a year or has multiple years "
            f"in its name." + newline + "Please provide data for a single year "
            "with that year in the file name."
        )

    return year


def get_holidays(year, region, path_holidays):
    """
    This function determines all holidays of a given region in a given year

    Parameters
    ----------
    path_holidays : str
        Input path
    year : int
        Year

    Returns
    -------
    holidays_dict : dict
        Dictionary with holidays

    """
    # Read all national holidays per state
    all_holidays = pd.read_csv(path_holidays)
    holidays_dict = {}

    # Get holidays in region
    holidays_filtered = all_holidays.loc[all_holidays["year"] == year]
    holidays_filtered = holidays_filtered[
        holidays_filtered["region"].str.contains(region)
    ]

    for row in holidays_filtered.iterrows():
        holidays_dict[
            datetime.date(row[1]["year"], row[1]["month"], row[1]["day"])
        ] = row[1]["holiday"]

    return holidays_dict


def get_building_class(region, path_building_class):
    """
    This function reads building classes of German states from input path
    and returns the building class of given region

    Parameters
    ----------
    region : str
        Region (eg. Brandenburg)
    path_building_class : str
        Input path

    Returns
    -------
    building_class : str
         Building class (German: Baualtersklasse) can assume values in range 1-11
         eg. 5 in case of BB and 3 in case of B
    """
    # Read all national holidays per state
    all_building_classes = pd.read_csv(path_building_class)
    building_class_df = all_building_classes.loc[
        all_building_classes["region"] == region
    ]
    building_class = building_class_df["building_class"].values[0]

    return building_class


def check_central_decentral(demands, value, consumer, carrier):
    """
    This function adds yearly demands per consumer and carrier to existing column
    in DataFrame and otherwise to a new column in this DataFrame

    Parameters
    ----------
    demands : pd.DataFrame
         DataFrame that contains yearly demands
    value : float
         Value of the yearly demand
    consumer : str
         Name of the consumer (eg.: ghd, efh, mfh)
    carrier : str
         Name of carrier (eg.: heat_central, heat_decentral)

    Returns
    -------
    demands : pd.DataFrame
         Updated DataFrame that contains yearly demands
    """
    col_name = consumer + "_" + carrier

    if col_name in demands.columns:
        demands[col_name].values[0] = np.add(demands[col_name].values[0], value)
    else:
        demands[col_name] = [value]
    return demands


def get_heat_demand(scalars, scenario, carrier, region):
    """
    This function returns ghd and hh demands together with their unit of a given region and a
    given scenario

    Parameters
    ----------
    scalars : DataFrame
        Dataframe with scalars
    scenario : str
        Scenario e.g. "2040-el_eff"
    carrier : str
         Name of carrier (eg.: heat_central, heat_decentral)
    region : str
        Region (eg. Brandenburg)

    Returns
    -------
    demands : DataFrame
        Dataframe with total yearly demand of central and decentral heat per consumer
        (eg.: ghd, hh)
    demand_unit : str
        Unit of total demands (eg. GWh)

    """
    consumers = ["ghd", "hh"]
    demands = pd.DataFrame()

    sc_filtered = dp.filter_df(scalars, "type", "load")
    sc_filtered = dp.filter_df(sc_filtered, "carrier", carrier)
    sc_filtered = dp.filter_df(sc_filtered, "region", region)
    sc_filtered = dp.filter_df(sc_filtered, "scenario_key", scenario)
    if sc_filtered.empty or sc_filtered["var_value"].isna().all():
        raise ValueError(
            f"No scalar data found that matches "
            f"scenario='{scenario}', "
            f"carrier='{carrier}', "
            f"region='{region}'"
        )

    if not (sc_filtered["var_unit"].values[0] == sc_filtered["var_unit"].values).all():
        raise ValueError(
            f"Unit mismatch in scalar data of heat demands. "
            f"Please make sure units match in {in_path5}."
        )

    demand_unit = list(set(sc_filtered["var_unit"]))

    for consumer in consumers:
        sc_filtered_consumer = sc_filtered[sc_filtered["tech"].str.contains(consumer)]

        if len(sc_filtered_consumer) > 1:
            logger.warning(
                f"There is duplicate demand of carrier '{carrier}', consumer "
                f"'{consumer}', region '{region}' and scenario '{scenario}' in {in_path5}."
                + "\n"
                + "The demand is going to be summed up. "
                "Otherwise you have to rerun the calculation and provide only one demand of the "
                "same carrier, consumer, region and scenario."
            )

        for demand_value in sc_filtered_consumer["var_value"].values:
            check_central_decentral(demands, demand_value, consumer, carrier)

    return demands, demand_unit


def calculate_heat_load(carrier, holidays, temperature, yearly_demands, building_class):
    """
    This function calculates a heat load profile of Industry, trade,
    service (ghd: Gewerbe, Handel, Dienstleistung) and Household (hh: Haushalt)
    sectors

    Parameters
    ----------
    carrier : str
         Name of carrier (eg.: heat_central, heat_decentral)
    holidays : dict
        Dictionary with holidays
    temperature : DataFrame
         DataFrame with temperatures
    yearly_demands: DataFrame
         DataFrame with yearly demands per consumer
    building_class : str
         Building class (German: Baualtersklasse) can assume values in range 1-11
         eg. 5 in case of BB and 3 in case of B

    Returns
    -------
    heat_load_total : pd.DataFrame
         DataFrame with total normalized heat load in year aggretated by consumers
         (eg.: ghd, efh, mfh)

    """
    # Add empty DataFrame for yearly heat loads
    heat_load_total = pd.DataFrame()

    # Add DataFrame time index for consumers heat loads
    heat_load_consumer = pd.DataFrame(
        index=pd.date_range(
            datetime.datetime(year, 1, 1, 0), periods=len(temperature), freq="H"
        )
    )

    # Calculate sfh (efh: Einfamilienhaus) heat load
    heat_load_consumer["efh" + "_" + carrier] = bdew.HeatBuilding(
        heat_load_consumer.index,
        holidays=holidays,
        temperature=temperature,
        shlp_type="EFH",
        building_class=building_class,
        wind_class=0,
        annual_heat_demand=share_efh * yearly_demands["hh" + "_" + carrier][0],
        name="EFH",
        ww_incl=True,
    ).get_bdew_profile()

    # Calculate mfh (mfh: Mehrfamilienhaus) heat load
    heat_load_consumer["mfh" + "_" + carrier] = bdew.HeatBuilding(
        heat_load_consumer.index,
        holidays=holidays,
        temperature=temperature,
        shlp_type="MFH",
        building_class=building_class,
        wind_class=0,
        annual_heat_demand=share_mfh * yearly_demands["hh" + "_" + carrier][0],
        name="MFH",
        ww_incl=True,
    ).get_bdew_profile()

    # Calculate industry, trade, service (ghd: Gewerbe, Handel, Dienstleistung)
    # heat load using gha profile of retail and wholesale (Einzel- und Großhandel)
    # which has lower share of process heat
    heat_load_consumer["ghd" + "_" + carrier] = bdew.HeatBuilding(
        heat_load_consumer.index,
        holidays=holidays,
        temperature=temperature,
        shlp_type="GHA",
        wind_class=0,
        annual_heat_demand=yearly_demands["ghd" + "_" + carrier][0],
        name="ghd",
        ww_incl=True,
    ).get_bdew_profile()

    # Calculate total heat load in year
    heat_load_total[carrier + "-demand-profile"] = heat_load_consumer.sum(axis=1)

    # Normalize heat load profile
    heat_load_total[carrier + "-demand-profile"] = np.divide(
        heat_load_total[carrier + "-demand-profile"],
        heat_load_total[carrier + "-demand-profile"].sum(),
    )

    return heat_load_total


if __name__ == "__main__":
    in_path1 = sys.argv[1]  # path to weather data
    in_path2 = sys.argv[2]  # path to household distributions data
    in_path3 = sys.argv[3]  # path to holidays
    in_path4 = sys.argv[4]  # path to building class
    in_path5 = sys.argv[5]  # path to csv with b3 scalars
    out_path1 = sys.argv[6]
    out_path2 = sys.argv[7]
    logfile = sys.argv[8]

    logger = config.add_snake_logger(logfile, "prepare_heat_demand")

    CARRIERS = ["heat_central", "heat_decentral"]

    # Read state heat demands of ghd and hh sectors
    sc = dp.load_b3_scalars(in_path5)

    # filter for heat demand data
    sc_filtered = dp.filter_df(sc, "type", "load")

    sc_filtered = dp.filter_df(sc_filtered, "carrier", CARRIERS)

    # get regions from data
    regions = sc_filtered.loc[:, "region"].unique()

    scenarios = sc_filtered.loc[:, "scenario_key"].unique()

    # Create empty data frame for results / output
    total_heat_load = pd.DataFrame(columns=dp.HEADER_B3_TS)

    for region, scenario in itertools.product(regions, scenarios):
        share_efh, share_mfh = get_shares_from_hh_distribution(in_path2, region)

        weather_file_names = find_regional_files(in_path1, region)

        for weather_file_name, carrier in itertools.product(
            weather_file_names, CARRIERS
        ):
            # Read year from weather file name
            year = get_year(weather_file_name)

            # Get holidays
            holidays = get_holidays(year, region, in_path3)

            # Read temperature from weather data
            path_weather_data = os.path.join(in_path1, weather_file_name)
            temperature = pd.read_csv(path_weather_data, usecols=["temp_air"], header=0)

            # Get building class
            building_class = get_building_class(region, in_path4)

            # Get heat demand in region and scenario
            yearly_demands, sc_demand_unit = get_heat_demand(
                sc, scenario, carrier, region
            )

            heat_load_year = calculate_heat_load(
                carrier, holidays, temperature, yearly_demands, building_class
            )

            heat_load_ts_info = {
                "region": region,
                "scenario_key": scenario,
                "var_unit": sc_demand_unit,
            }

            heat_load_year = dp.prepare_b3_timeseries(
                heat_load_year, **heat_load_ts_info
            )

            # Append stacked heat load of year to stacked time series with total heat load
            total_heat_load = pd.concat(
                [total_heat_load, heat_load_year], ignore_index=True, sort=False
            )

    # aggregate heat demand for different sectors (hh, ghd, i)
    demand_per_sector = dp.filter_df(
        sc, "tech", ["demand_hh", "demand_ghd", "demand_i"]
    )
    aggregated_demands = dp.aggregate_scalars(
        demand_per_sector,
        "tech",
        {
            "var_value": sum,
            "var_unit": dp.aggregate_units,
            "source": dp.aggregate_units,
        },
    )
    aggregated_demands.loc[:, "tech"] = "demand"

    aggregated_demands.loc[:, "name"] = aggregated_demands.apply(
        lambda x: "-".join([x["region"], x["carrier"], x["tech"]]), 1
    )

    dp.save_df(aggregated_demands, out_path1)

    # Rearrange stacked time series
    head_load = dp.format_header(
        df=total_heat_load,
        header=dp.HEADER_B3_TS,
        index_name=config.settings.general.ts_index_name,
    )
    dp.save_df(head_load, out_path2)
