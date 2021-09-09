# coding: utf-8
r"""
Inputs
-------
filename_wind : str
    Path incl. file name to area and power potential of wind energy
filename_pv : str
    Path incl. file name to area and power potential of pv

Outputs
---------
output_file : str
    Path incl. file name to output

Description
-------------
Processes the area and power potential of pv and wind energy resulting from script
'prepare_re_potential.py' and saves results for "Landkreise" and total values for Brandenburg in
 `output_file`.

Saves the following data for "Landkreise" and aggregated values for Brandenburg:
    - power potential in GW for wind and pv in columns 'Leistung Wind [GW]' and 'Leistung PV [GW]'
    - area potential in km² for wind and pv in columns 'Fläche Wind [km2]' and 'Fläche PV [km2]'

"""

import pandas as pd
import sys

if __name__ == "__main__":
    filename_wind = sys.argv[1]
    filename_pv = sys.argv[2]
    output_file = sys.argv[3]

    # prepare wind pot
    wind_pot = pd.read_csv(filename_wind, sep=";").set_index("NUTS")
    wind_pot["power_potential"] = wind_pot["power_potential"] / 1000
    wind_pot["area"] = wind_pot["area"] / 1e6
    wind_pot_prepared = wind_pot[["Kreis", "area", "power_potential"]].rename(
        columns={"area": "Fläche Wind [km2]", "power_potential": "Leistung Wind [GW]"}
    )

    # prepare pv pot
    pv_pot = pd.read_csv(filename_pv, sep=";").set_index("NUTS")
    pv_pot["power_potential"] = pv_pot["power_potential"] / 1000
    pv_pot["area"] = pv_pot["area"] / 1e6
    pv_pot_prepared = pv_pot[["area", "power_potential"]].rename(
        columns={"area": "Fläche PV [km2]", "power_potential": "Leistung PV [GW]"}
    )

    potentials = pd.concat([wind_pot_prepared, pv_pot_prepared], axis=1)
    potentials = potentials.round(1)

    # sum up area and power potential of Brandenburg
    potential_bb = (
        pd.DataFrame(potentials.sum(axis=0)).transpose().rename({0: "Brandenburg"})
    )
    potential_bb["Kreis"] = "Summe Brandenburg"
    potentials = pd.concat([potentials, potential_bb], axis=0)

    potentials.to_csv(output_file, sep=";")
