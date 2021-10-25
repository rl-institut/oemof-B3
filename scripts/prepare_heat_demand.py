import sys
import datetime
from demandlib import bdew
import pandas as pd
import numpy as np
import os

import oemof_b3.tools.data_processing as dp


def calculate_heat_load(temperature, region, scenario):
    """
    This function calculates a heat load profile of Industry, trade,
    service (ghd: Gewerbe, Handel, Dienstleistung) and Household (hh: Haushalt)
    sectors

    Parameters
    ----------
    year : int
        Year of the heat load
    temperature : pd.DataFrame
         DataFrame that contains series of temperatures in a column name
         temp_air
    region : str
        Region the heat load is investigated for
    scenario : str
        Scenario the heat load is investigated for

    Returns
    -------
    heat_load_total : pd.DataFrame
         DataFrame that contains the calculated total heat load

    """
    # Get all holidays of the region in examined year
    all_holidays = pd.read_csv(in_path2)
    holidays = {}

    # Read time series template
    ts_template = dp.load_b3_timeseries(in_path5, sep=";")
    ts_heat_load = pd.DataFrame(columns=ts_template.columns)

    years = np.arange(2010, 2020)

    for index, year in enumerate(years):
        for row in all_holidays.iterrows():
            if year == row[1]["year"] and region in row[1]["region"]:
                holidays[
                    datetime.date(row[1]["year"], row[1]["month"], row[1]["day"])
                ] = row[1]["holiday"]

        # Get heat demands of ghd and hh sectors in the region
        sc = dp.load_b3_scalars(in_path3)

        for row in sc.iterrows():
            if row[1]["scenario"] == scenario and row[1]["region"] == region:
                if "ghd" in row[1]["name"] or "GHD" in row[1]["name"]:
                    total_demand_ghd = row[1]["var_value"]
                elif (
                    "hh" in row[1]["name"]
                    or "HH" in row[1]["name"]
                    or "household" in row[1]["name"]
                ):
                    total_demand_hh = row[1]["var_value"]

        # Apply distribution for hh sector in order to calculate single family house
        # (sfh / efh: Einfamilienhaus) and multi family house (mfh: Mehrfamilienhaus)
        # demands
        distribution_households = pd.read_csv(in_path1)

        for row in distribution_households.iterrows():
            if region in row[1]["region"]:
                share_efh = row[1]["sfh"] / (row[1]["sfh"] + row[1]["mfh"])
                share_mfh = row[1]["mfh"] / (row[1]["sfh"] + row[1]["mfh"])

        demand = pd.DataFrame(
            index=pd.date_range(datetime.datetime(year, 1, 1, 0), periods=8760, freq="H")
        )

        # Calcualate sfh (efh: Einfamilienhaus) heat load
        demand["efh"] = bdew.HeatBuilding(
            demand.index,
            holidays=holidays,
            temperature=temperature,
            shlp_type="EFH",
            building_class=1,
            wind_class=1,
            annual_heat_demand=share_efh * total_demand_hh,
            name="EFH",
            ww_incl=True,
        ).get_bdew_profile()

        # Calculate mfh (mfh: Mehrfamilienhaus) heat load
        demand["mfh"] = bdew.HeatBuilding(
            demand.index,
            holidays=holidays,
            temperature=temperature,
            shlp_type="MFH",
            building_class=2,
            wind_class=0,
            annual_heat_demand=share_mfh * total_demand_hh,
            name="MFH",
            ww_incl=True,
        ).get_bdew_profile()

        # Calculate industry, trade, service (ghd: Gewerbe, Handel, Dienstleistung)
        # heat load
        demand["ghd"] = bdew.HeatBuilding(
            demand.index,
            holidays=holidays,
            temperature=temperature,
            shlp_type="ghd",
            wind_class=0,
            annual_heat_demand=total_demand_ghd,
            name="ghd",
            ww_incl=True,
        ).get_bdew_profile()

        # Calculate total heat load
        heat_load_total = pd.DataFrame(data={"Heat_load_" + str(region) + "_" + str(year) + "_in_GWh": demand.sum(axis=1)})

        new_row_items = dp.stack_timeseries(heat_load_total)
        new_row_items["id_ts"] = index
        new_row_items["region"] = region
        new_row_items["scenario"] = scenario

        ts_template_columns = ts_template.columns

        ts_prepared = dp.format_header(
            df=new_row_items, header=ts_template.columns, index_name="id_ts"
        )
        new_row = pd.DataFrame(data={new_row_items}, columns=ts_template.columns)

        ts_heat_load = pd.concat([ts_heat_load, new_row], ignore_index=True)


    return heat_load_total


if __name__ == "__main__":
    path_this_file = os.path.realpath(__file__)
    raw_data = os.path.abspath(
        os.path.join(path_this_file, os.pardir, os.pardir, "raw")
    )
    schema = os.path.abspath(
        os.path.join(path_this_file, os.pardir, os.pardir, "oemof_b3", "schema")
    )

    in_path1 = os.path.join(raw_data, "distribution_households.csv")  # path to household distributions data
    in_path2 = os.path.join(raw_data, "holidays.csv") # path to holidays
    in_path3 = os.path.join(raw_data, "scalars.csv")  # path to b3 schema scalars.csv
    in_path4 = os.path.join(raw_data, "weatherdata.csv")  # path to weather data
    in_path5 = os.path.join(schema, "timeseries.csv")
    out_path = os.path.join(raw_data, "heat_load.csv")

    # in_path1 = sys.argv[1]  # path to household distributions data
    # in_path2 = sys.argv[2]  # path to holidays
    # in_path3 = sys.argv[3]  # path to b3 schema scalars.csv
    # in_path4 = sys.argv[4]  # path to weather data
    # in_path5 = sys.argv[5]  # path to template of times series format
    # out_path = sys.argv[6]

    temperature_BE_2018 = pd.read_csv(in_path4, usecols=[4], header=0)
    region_BE = "BE"
    scenario_base = "base"

    heat_load = calculate_heat_load(temperature_BE_2018, region_BE, scenario_base)
    heat_load.to_csv(out_path)
