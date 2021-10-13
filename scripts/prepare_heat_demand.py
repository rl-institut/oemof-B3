import demandlib.bdew as bdew
import datetime
import pandas as pd
import numpy as np


def calculate_heat_load(year, temperature, region):

    # TODO: csv with all holidays in reference year (2018 ?), 2040 and 2050 that is read in.
    #  Columns should be "year, month, day, holiday, state". All other rows than these with state == region
    #  will be dropped. For each holiday in this Dataframe the a dictionary 'holiday' is updated with the
    #  values in the rows
    holidays = {
        datetime.date(2018, 1, 1): "Neujahr",
        datetime.date(2018, 3, 30): "Karfreitag",
        datetime.date(2018, 4, 1): "Ostersonntag",
        datetime.date(2018, 4, 2): "Ostermontag",
        datetime.date(2018, 5, 1): "Maifeiertag",
        datetime.date(2018, 5, 10): "Christi Himmelfahrt",
        datetime.date(2018, 5, 20): "Pfingstsonntag",
        datetime.date(2018, 5, 21): "Pfingstmontag",
        datetime.date(2018, 10, 3): "Tag der deutschen Einheit",
        datetime.date(2018, 12, 25): "1. Weihnachtstag",
        datetime.date(2018, 12, 26): "2. Weihnachtstag",
    }
    if region is "BB":
        holidays.update({datetime.date(2018, 10, 31): "Reformationstag"})

    # TODO: In order to make this independent from region
    #  load shares and demands from csv
    # TODO: Assumptions households also for 2040 and 2050?
    if region is "BE":
        EFH_2017 = 1049
        MFH_2017 = 955
        share_EFH_2017 = EFH_2017 / np.add(EFH_2017, MFH_2017)
        share_MFH_2017 = MFH_2017 / np.add(EFH_2017, MFH_2017)
    elif region is "BB":
        EFH_2017 = 480
        MFH_2017 = 769
        share_EFH_2017 = EFH_2017 / np.add(EFH_2017, MFH_2017)
        share_MFH_2017 = MFH_2017 / np.add(EFH_2017, MFH_2017)

    if year == 2018:
        if region is "BE":
            total_demand_hh = 17415.94
            total_demand_ghd = 11502.47
        if region is "BB":
            total_demand_hh = 21935.15
            total_demand_ghd = 6046.97
    elif year == 2040:
        raise ValueError("Sorry 2040 is not implemented yet")
    elif year == 2050:
        if region is "BE":
            total_demand_hh = 8587.27
            total_demand_ghd = 5702.26
        if region is "BB":
            total_demand_hh = 10815.56
            total_demand_ghd = 2997.74

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
        annual_heat_demand=share_EFH_2017 * total_demand_hh,
        name="EFH",
        ww_incl=True,
    ).get_bdew_profile()

    result_annual_heat_demand_efh = sum(demand["efh"])
    print("Sum of heat demand 'efh': ", result_annual_heat_demand_efh)

    # Multi family house (mfh: Mehrfamilienhaus)
    demand["mfh"] = bdew.HeatBuilding(
        demand.index,
        holidays=holidays,
        temperature=temperature,
        shlp_type="MFH",
        building_class=2,
        wind_class=0,
        annual_heat_demand=share_MFH_2017 * total_demand_hh,
        name="MFH",
        ww_incl=True,
    ).get_bdew_profile()
    result_annual_heat_demand_mfh = sum(demand["mfh"])
    print("Sum of heat demand 'mfh': ", result_annual_heat_demand_mfh)

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
    result_annual_heat_demand_ghd = sum(demand["ghd"])
    print("Sum of heat demand 'ghd': ", result_annual_heat_demand_ghd)


if __name__ == "__main__":
    year = 2018
    temperature = pd.Series(np.ones(8760) * np.random.choice(np.arange(20, 30)))
    region = "BE"

    calculate_heat_load(year, temperature, region)
