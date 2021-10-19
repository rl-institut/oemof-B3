import sys
import datetime
from demandlib import bdew
import pandas as pd


def calculate_heat_load(year, temperature, region, scenario):
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

    for row in all_holidays.iterrows():
        if region in row[1]["region"]:
            holidays[
                datetime.date(row[1]["year"], row[1]["month"], row[1]["day"])
            ] = row[1]["holiday"]
    # TODO: Build a check for year

    # Get heat demands of ghd and hh sectors in the region
    sc = pd.read_csv(in_path3)

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
    heat_load_total = pd.DataFrame(data={"heat load in GWh": demand.sum(axis=1)})

    return heat_load_total


if __name__ == "__main__":
    in_path1 = sys.argv[1]  # path to household distributions data
    in_path2 = sys.argv[2]  # path to holidays
    in_path3 = sys.argv[3]  # path to b3 schema scalars.csv
    in_path4 = sys.argv[4]  # path to weather data
    out_path = sys.argv[5]

    temperature_BE_2018 = pd.read_csv(in_path4, usecols=[4], header=0)
    year_base = 2018  # TODO: Hardcoded in function instead? Decision wanted.
    region_BE = "BE"
    scenario_base = "base"

    heat_load = calculate_heat_load(
        year_base, temperature_BE_2018, region_BE, scenario_base
    )
    heat_load.to_csv(out_path)
