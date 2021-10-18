import datetime
import os
from demandlib import bdew
import pandas as pd


def calculate_heat_load(year, temperature, region, scenario):

    all_holidays = pd.read_csv(os.path.join(raw_data, "holidays.csv"))

    holidays = {}

    for row in all_holidays.iterrows():
        if region in row[1]["region"]:
            holidays[
                datetime.date(row[1]["year"], row[1]["month"], row[1]["day"])
            ] = row[1]["holiday"]

    sc = pd.read_csv(os.path.join(raw_data, "scalars.csv"))

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

    distribution_households = pd.read_csv(
        os.path.join(raw_data, "distribution_households.csv")
    )
    for row in distribution_households.iterrows():
        if region in row[1]["region"]:
            share_efh = row[1]["sfh"] / (row[1]["sfh"] + row[1]["mfh"])
            share_mfh = row[1]["mfh"] / (row[1]["sfh"] + row[1]["mfh"])

    demand = pd.DataFrame(
        index=pd.date_range(datetime.datetime(year, 1, 1, 0), periods=8760, freq="H")
    )

    # Single family house (efh: Einfamilienhaus)
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

    # Multi family house (mfh: Mehrfamilienhaus)
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

    # Industry, trade, service (ghd: Gewerbe, Handel, Dienstleistung)
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
    heat_load_total = pd.DataFrame(data={"heat load in GWh": demand.sum(axis=1)})
    return heat_load_total


if __name__ == "__main__":
    path_this_file = os.path.realpath(__file__)
    raw_data = os.path.abspath(
        os.path.join(path_this_file, os.pardir, os.pardir, "raw")
    )

    temperature_BE_2017 = pd.read_csv(
        os.path.join(raw_data, "weatherdata_52.52437_13.41053_2017.csv"),
        usecols=[4],
        header=0,
    )
    year_base = 2018  # TODO: Hardcoded in function instead? Decision wanted.
    region = "BE"
    scenario = "base"

    heat_load = calculate_heat_load(year_base, temperature_BE_2017, region, scenario)
