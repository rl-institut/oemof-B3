import datetime
import demandlib.bdew as bdew
import demandlib.particular_profiles as profiles
from datetime import time as settime
from workalendar.europe import Germany
import matplotlib.pyplot as plt


cal = Germany()
holidays = dict(cal.holidays(2015))


def power_example(
        ann_el_demand_per_sector=None,
        testmode=False):
    if ann_el_demand_per_sector is None:
        ann_el_demand_per_sector = {
            'g0': 4604, # G0: Gewerbe allgemein
            'h0': 4138, # H0: Haushalt
            'i0': 7172, # I0: Industrieprofil aus eigenen Daten, NICHT von BDEW
        }
    year = 2015

    # read standard load profiles
    e_slp = bdew.ElecSlp(year, holidays=holidays)

    # multiply given annual demand with timeseries
    elec_demand = e_slp.get_profile(ann_el_demand_per_sector,
                                    dyn_function_h0=False)

    # Add the slp for the industrial group
    ilp = profiles.IndustrialLoadProfile(e_slp.date_time_index,
                                         holidays=holidays)

    # Beginning and end of workday, weekdays and weekend days, and scaling
    # factors by default
    if 'i0' in ann_el_demand_per_sector:
        elec_demand['i0'] = ilp.simple_profile(ann_el_demand_per_sector['i0'])

    if not testmode:
        print("Be aware that the values in the DataFrame are 15 minute values"
              + "with a power unit. If you sum up a table with 15min values"
              + "the result will be of the unit 'kW15minutes'.")
        print(elec_demand.sum())

        print("You will have to divide the result by 4 to get kWh.")
        print(elec_demand.sum() / 4)

        print("Or resample the DataFrame to hourly values using the mean() "
              "method.")

        # Resample 15-minute values to hourly values.
        elec_demand = elec_demand.resample('H').mean()
        print(elec_demand.sum())

        if plt is not None:
            # Plot demand
            ax = elec_demand.plot()
            ax.set_xlabel("Date")
            ax.set_xlim([datetime.date(2015, 1, 26), datetime.date(2015, 1, 28)])
            ax.set_ylabel("Power demand")
            plt.show()

    return elec_demand


if __name__ == '__main__':
    print(power_example())