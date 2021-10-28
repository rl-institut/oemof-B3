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
output_scalars : str
    Path incl. file name to scalar output as input to energy system model
output_tables : str
    Path incl. file name to output for results documentation

Description
-------------
Processes the area and power potential of pv and wind energy resulting from script
'prepare_re_potential.py'. Reformats the power potential of pv and wind energy as input for the
energy system model and joins results of both pv and wind.
Saves results for "Landkreise" and total values for Brandenburg in `output_scalars` (only power
potential) in format as required by template and in `output_tables` (power and
area potential) for results documentation.

Saves the following data for "Landkreise" and aggregated values for Brandenburg in `output_tables`:
    - power potential in GW for wind and pv in columns 'Leistung Wind [GW]' and 'Leistung PV [GW]'
    - area potential in km² for wind and pv in columns 'Fläche Wind [km2]' and 'Fläche PV [km2]'

"""

import pandas as pd
import sys

from oemof_b3.tools import data_processing as dp

if __name__ == "__main__":
    filename_wind = sys.argv[1]
    filename_pv = sys.argv[2]
    output_scalars = sys.argv[3]
    output_tables = sys.argv[4]

    ############################################
    # prepare potentials for scalar _resources #
    ############################################

    # prepare wind and pv potential
    potentials = pd.DataFrame()
    for type in ["pv", "wind"]:
        if type == "pv":
            data = pd.read_csv(filename_pv, sep=";").set_index("NUTS")
            data["carrier"] = "solar"
            data["tech"] = "pv"
            data["comment"] = (
                "filenames: 2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv "
                "2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv"
            )
        else:
            data = pd.read_csv(filename_wind, sep=";").set_index("NUTS")
            data["carrier"] = "wind"
            data["tech"] = "onshore"
            data[
                "comment"
            ] = "filename: 2021-05-18_wind_brandenburg_kreise_epsg32633.csv"

        # prepare df with certain columns
        df = data.loc[
            :, ["region", "power_potential_agreed", "carrier", "tech", "comment"]
        ]
        df.rename(columns={"power_potential_agreed": "var_value"}, inplace=True)
        potentials = pd.concat([potentials, df], axis=0)

    # format header of `potentials` according to template
    scalar_df = dp.format_header(
        df=potentials, header=dp.HEADER_B3_SCAL, index_name="id_scal"
    )

    # add additional information as required by template
    scalar_df.loc[:, "scenario"] = ""
    scalar_df.loc[:, "name"] = "None"
    scalar_df.loc[:, "var_name"] = "capacity"
    scalar_df.loc[:, "type"] = "volatile"
    scalar_df.loc[:, "var_unit"] = "MW"
    scalar_df.loc[
        :, "source"
    ] = "area potentials - https://sandbox.zenodo.org/record/746695/"

    dp.save_df(df=scalar_df, path=output_scalars)

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
