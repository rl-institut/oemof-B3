# coding: utf-8
r"""
Inputs
-------
filename_wind : str
    Path incl. file name to area and power potential of wind energy
filename_pv : str
    Path incl. file name to area and power potential of pv
filename_scalar_template : str
    Path incl. file name to template for scalar data

Outputs
---------
output_scalars : str
    Path incl. file name to scalar output as input to energy system model
output_tables : str
    Path incl. file name to output for results documentation

Description
-------------
Processes the area and power potential of pv and wind energy resulting from script
'prepare_re_potential.py' and saves results for "Landkreise" and total values for Brandenburg in
`output_scalars` for energy system model and in `output_tables` for results documentation.

Saves the following data for "Landkreise" and aggregated values for Brandenburg `output_tables`:
    - power potential in GW for wind and pv in columns 'Leistung Wind [GW]' and 'Leistung PV [GW]'
    - area potential in km² for wind and pv in columns 'Fläche Wind [km2]' and 'Fläche PV [km2]'

"""

import pandas as pd
import sys

if __name__ == "__main__":
    filename_wind = sys.argv[1]
    filename_pv = sys.argv[2]
    filename_scalar_template = sys.argv[3]
    output_scalars = sys.argv[4]
    output_tables = sys.argv[5]

    ############################################
    # prepare potentials for scalar _resources #
    ############################################

    # prepare wind and pv potential
    potentials = pd.DataFrame()
    for type in ["pv", "wind"]:
        data = pd.read_csv(filename_wind, sep=";").set_index("NUTS")
        df = data[["region", "power_potential_agreed"]]
        if type == "pv":
            df["carrier"] = "solar"
            df["tech"] = "pv"
            df["comment"] = (
                "filenames: 2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv "
                "2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv"
            )
        else:
            df["carrier"] = "wind"
            df["tech"] = "onshore"
            df["comment"] = "filename: 2021-05-18_wind_brandenburg_kreise_epsg32633.csv"

        potentials = pd.concat([potentials, df], axis=0)
        potentials.index = range(0, len(potentials))

    # prepare scalars according to template
    scalar_df = pd.read_csv(filename_scalar_template, delimiter=";")
    scalar_df["id_scal"] = potentials.index
    scalar_df["scenario"] = ""
    scalar_df["name"] = "None"
    scalar_df["var_name"] = "capacity"
    scalar_df["carrier"] = potentials["carrier"]
    scalar_df["region"] = potentials["region"]
    scalar_df["tech"] = potentials["tech"]
    scalar_df["type"] = "volatile"
    scalar_df["var_value"] = potentials["power_potential_agreed"]
    scalar_df["var_unit"] = "MW"
    scalar_df[
        "reference"
    ] = "area potentials - https://sandbox.zenodo.org/record/746695/"
    scalar_df["comment"] = potentials["comment"]
    # set index
    scalar_df.set_index("id_scal", inplace=True)

    scalar_df.to_csv(output_scalars, sep=";")

    ##################################
    # prepare potentials for _tables #
    ##################################

    # prepare wind pot
    wind_pot = pd.read_csv(filename_wind, sep=";").set_index("NUTS")
    wind_pot["power_potential"] = wind_pot["power_potential"] / 1000
    wind_pot["area"] = wind_pot["area"] / 1e6
    wind_pot_prepared = wind_pot[["region", "area", "power_potential"]].rename(
        columns={
            "area": "Fläche Wind [km2]",
            "power_potential": "Leistung Wind [GW]",
            "region": "Kreis",
        }
    )

    # prepare pv pot
    pv_pot = pd.read_csv(filename_pv, sep=";").set_index("NUTS")
    pv_pot["power_potential"] = pv_pot["power_potential"] / 1000
    pv_pot["area"] = pv_pot["area"] / 1e6
    pv_pot_prepared = pv_pot[["area", "power_potential"]].rename(
        columns={
            "area": "Fläche PV [km2]",
            "power_potential": "Leistung PV [GW]",
            "region": "Kreis",
        }
    )

    potentials = pd.concat([wind_pot_prepared, pv_pot_prepared], axis=1)
    potentials = potentials.round(1)

    # sum up area and power potential of Brandenburg
    potential_bb = (
        pd.DataFrame(potentials.sum(axis=0)).transpose().rename({0: "Brandenburg"})
    )
    potential_bb["Kreis"] = "Summe Brandenburg"
    potentials = pd.concat([potentials, potential_bb], axis=0)

    potentials.to_csv(output_tables, sep=";")
