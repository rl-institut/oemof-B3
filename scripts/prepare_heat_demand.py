# coding: utf-8
r"""
Inputs
-------
in_path1 : str
    path of input directory with raw data
in_path2 : str
    path of input file with household distributions data as .csv
in_path3 : str
    path of input file with holidays of all states in Germany as .csv
in_path4 : str
    path of template for scalar data as .csv
in_path5 : str
    path of input file with times series format as .csv
out_path : str
    path of output file with prepared data as .csv

Outputs
---------
pandas.DataFrame
    with grouped and aggregated data of heat demands.
    Data is grouped by region, energy source, technology and chp capability and contains
    net capacity and efficiency.

Description
-------------
The script...

"""
import sys
import datetime
import os
from demandlib import bdew
import pandas as pd
import numpy as np


import oemof_b3.tools.data_processing as dp


def get_holidays(path, year, region):
    """
    This function determines all holidays of a given region in a given year

    Parameters
    ----------
    path : str
        input path
    year : int
        year e.g. 2018
    region : str
        region e.g. BB as Brandenburg

    Returns
    -------
    holidays : dict
        dictionary with holidays

    """
    # Read all national holidays per state
    all_holidays = pd.read_csv(path)
    holidays = {}

    # Get holidays in region
    for row in all_holidays.iterrows():
        if year == row[1]["year"] and region in row[1]["region"]:
            holidays[
                datetime.date(row[1]["year"], row[1]["month"], row[1]["day"])
            ] = row[1]["holiday"]

    return holidays


def check_central_decentral(demands, value, consumer, type):
    """
    This function checks whether
    Parameters
    ----------
    demands : pd.DataFrame
         DataFrame that contains yearly demands
    value : float
         Value of the yearly demand
    consumer : str
         Name of the consumer (eg.: ghd, efh, mfh)
    type : str
         Specification of heat demand: central or decentral

    Returns
    -------
    demands : pd.DataFrame
         Updated DataFrame that contains yearly demands
    """
    if consumer + "_" + type in demands.columns:
        demands[consumer + "_" + type] = np.sum(demands[consumer + "_" + type], [value])
    else:
        demands[consumer + "_" + type] = [value]
    return demands


def get_heat_demand(path, region, scenario):
    """
    This function returns ghd and hh demands together with their unit of a given region and a
    given scenario

    Parameters
    ----------
    path : str
        input path
    region : str
        region e.g. BB as Brandenburg
    scenario : str
        scenario e.g. "base"

    Returns
    -------
    demand_ghd : float
        total demand ghd
    demand_hh : float
        total demand hh
    demand_ghd_unit : str
        unit of total demands

    """
    # Read state heat demands of ghd and hh sectors
    sc = dp.load_b3_scalars(path)  # TODO: Add ', sep=";"' if from schema
    consumers = ["ghd", "efh", "mfh"]
    types = ["central", "decentral"]
    demands = pd.DataFrame()
    units = []

    for row in sc.iterrows():
        # Get heat demands in region
        if (
            "heat" in row[1]["carrier"]
            and "demand" in row[1]["tech"]
            and row[1]["scenario"] == scenario
            and row[1]["region"] == region
        ):
            for consumer in consumers:
                for type in types:
                    if (
                        consumer in row[1]["name"]
                        and type in row[1]["name"]
                        and "de" + type not in row[1]["name"]
                    ):
                        check_central_decentral(
                            demands, row[1]["var_value"], consumer, type
                        )
                        units.append(row[1]["var_unit"])

    if len(list(set(units))) != 1:
        raise ValueError(
            f"Unit mismatch in scalar data of heat demands. "
            f"Please make sure units match in {path}."
        )

    return demands, list(set(units))


def calculate_heat_load(region, scenario):
    """
    This function calculates a heat load profile of Industry, trade,
    service (ghd: Gewerbe, Handel, Dienstleistung) and Household (hh: Haushalt)
    sectors

    Parameters
    ----------
    region : str
        region e.g. BB as Brandenburg
    scenario : str
        scenario e.g. "base"

    Returns
    -------
    heat_load_total : pd.DataFrame
         DataFrame that contains the calculated total heat load

    """
    # Set examined years
    years = np.arange(2010, 2020)

    # Read time series template
    ts_template = dp.load_b3_timeseries(in_path5, sep=";")

    # Add empty data frame for results / output
    heat_load = pd.DataFrame(columns=ts_template.columns)

    for index, year in enumerate(years):
        # Get holidays
        holidays = get_holidays(in_path3, year, region)

        # Read weather data
        path_weather_data = os.path.join(
            in_path1, "weatherdata_" + region + "_" + str(year) + ".csv"
        )
        temperature = pd.read_csv(path_weather_data, usecols=["temp_air"], header=0)

        # Get heat demand in region and scenario
        yearly_demands, sc_demand_unit = get_heat_demand(in_path4, region, scenario)

        types = ["central", "decentral"]

        # Add DataFrame time index for demands
        demand = pd.DataFrame(
            index=pd.date_range(
                datetime.datetime(year, 1, 1, 0), periods=len(temperature), freq="H"
            )
        )

        for type in types:
            # Calculate sfh (efh: Einfamilienhaus) heat load
            demand["efh" + "_" + type] = bdew.HeatBuilding(
                demand.index,
                holidays=holidays,
                temperature=temperature,
                shlp_type="EFH",
                building_class=6,
                wind_class=0,
                annual_heat_demand=yearly_demands["efh" + "_" + type],
                name="EFH",
                ww_incl=True,
            ).get_bdew_profile()

            # Calculate mfh (mfh: Mehrfamilienhaus) heat load
            demand["mfh" + "_" + type] = bdew.HeatBuilding(
                demand.index,
                holidays=holidays,
                temperature=temperature,
                shlp_type="MFH",
                building_class=2,
                wind_class=0,
                annual_heat_demand=yearly_demands["mfh" + "_" + type],
                name="MFH",
                ww_incl=True,
            ).get_bdew_profile()

            # Calculate industry, trade, service (ghd: Gewerbe, Handel, Dienstleistung)
            # heat load
            demand["ghd" + "_" + type] = bdew.HeatBuilding(
                demand.index,
                holidays=holidays,
                temperature=temperature,
                shlp_type="ghd",
                wind_class=0,
                annual_heat_demand=yearly_demands["ghd" + "_" + type],
                name="ghd",
                ww_incl=True,
            ).get_bdew_profile()

        # Calculate total heat load in year
        heat_load_year = pd.DataFrame(
            data={"Heat_load_" + str(region) + "_" + str(year): demand.sum(axis=1)}
        )

        # Stack time series with total heat load in year
        heat_load_year_stacked = dp.stack_timeseries(heat_load_year)

        # Add index, region and scenario information time series with total heat load
        # in year
        heat_load_year_stacked["id_ts"] = index
        heat_load_year_stacked["region"] = region
        heat_load_year_stacked["scenario"] = scenario
        heat_load_year_stacked["var_unit"] = sc_demand_unit

        # Rearrange stacked time series
        heat_load_year_stacked = dp.format_header(
            df=heat_load_year_stacked, header=ts_template.columns, index_name="id_ts"
        )

        # Append stacked heat load of year to stacked time series with total heat loads
        heat_load = pd.concat([heat_load, heat_load_year_stacked], ignore_index=True)

    return heat_load


if __name__ == "__main__":
    # path_this_file = os.path.realpath(__file__)
    # raw_data = os.path.abspath(
    #     os.path.join(path_this_file, os.pardir, os.pardir, "raw")
    # )
    # schema = os.path.abspath(
    #     os.path.join(path_this_file, os.pardir, os.pardir, "oemof_b3", "schema")
    # )
    # results = os.path.abspath(
    #     os.path.join(path_this_file, os.pardir, os.pardir, "results", "_resources")
    # )
    #
    # in_path1 = os.path.join(raw_data, "weatherdata")  # path to weather data
    # in_path2 = os.path.join(
    #     raw_data, "distribution_households.csv"
    # )  # path to household distributions data
    # in_path3 = os.path.join(raw_data, "holidays.csv")  # path to holidays
    # in_path4 = os.path.join(raw_data, "scalars.csv")  # path to b3 schema scalars.csv
    # in_path5 = os.path.join(schema, "timeseries.csv")
    # out_path = os.path.join(results, "load_profile_heat.csv")

    in_path1 = sys.argv[1]  # path to weather data
    in_path2 = sys.argv[2]  # path to household distributions data
    in_path3 = sys.argv[3]  # path to holidays
    in_path4 = sys.argv[4]  # path to b3 scalars.csv
    in_path5 = sys.argv[5]  # path to template of times series format
    out_path = sys.argv[6]

    REGION = "BB"
    SCENARIO = "base"

    heat_load = calculate_heat_load(REGION, SCENARIO)
    heat_load.to_csv(out_path)
