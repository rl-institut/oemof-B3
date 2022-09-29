# coding: utf-8
r"""
Inputs
-------
input_dir : str
    ``results/_resources/RE_potential/``: Path to input directory of renewable potential
output_scalars : str
    ``results/_resources/scal_power_potential_wind_pv.csv``: Path incl. file name of scalar output,
     which is input to energy system model
output_tables : str
    ``results/_tables/potential_wind_pv_kreise.csv``: Path incl. file name of output for results
    documentation

Outputs
---------
pd.DataFrame
    Power potential for "Landkreise" and total values for Brandenburg in `output_scalars` in format
    as required by scalars template
pd.DataFrame
    Power and area potential for "Landkreise" and aggregated values for Brandenburg in
    `output_tables` for results documentation:
    - power potential in GW for wind and pv in columns 'Leistung Wind [GW]' and 'Leistung PV [GW]'
    - area potential in km² for wind and pv in columns 'Fläche Wind [km2]' and 'Fläche PV [km2]'

Description
-------------
Processes the area and power potential of pv and wind energy resulting from script
'prepare_re_potential.py'. Formats the power potential of pv and wind energy as input for the
energy system model and joins results of both pv and wind.
"""

import pandas as pd
import sys
import os

from oemof_b3.tools import data_processing as dp
from oemof_b3.config import config

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_scalars = sys.argv[2]
    output_tables = sys.argv[3]

    ###########################################
    # prepare potentials for scalar_resources #
    ###########################################

    # prepare wind and pv potential
    potentials = pd.DataFrame()
    for type in ["pv", "wind"]:
        filename = os.path.join(input_dir, f"power_potential_{type}_kreise.csv")
        if type == "pv":
            data = pd.read_csv(filename, sep=";").set_index("NUTS")
            data["carrier"] = "solar"
            data["tech"] = "pv"
            data["comment"] = (
                "filenames: 2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv "
                "2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv"
            )
        else:
            data = pd.read_csv(filename, sep=";").set_index("NUTS")
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
        df=potentials,
        header=dp.HEADER_B3_SCAL,
        index_name=config.settings.general.scal_index_name,
    )

    # add additional information as required by template
    scalar_df.loc[:, "scenario_key"] = config.settings.process_re_potential.scenario_key
    scalar_df.loc[:, "name"] = config.settings.process_re_potential.name
    scalar_df.loc[:, "var_name"] = config.settings.process_re_potential.var_name
    scalar_df.loc[:, "type"] = "volatile"
    scalar_df.loc[:, "var_unit"] = config.settings.process_re_potential.var_unit
    scalar_df.loc[:, "source"] = config.settings.process_re_potential.source

    dp.save_df(df=scalar_df, path=output_scalars)

    ##################################
    # prepare potentials for _tables #
    ##################################
    potentials_table = pd.DataFrame()
    for type in ["pv", "wind"]:
        filename = os.path.join(input_dir, f"power_potential_{type}_kreise.csv")
        df = pd.read_csv(filename, sep=";").set_index("NUTS")
        df["power_potential"] = df["power_potential"] / 1000
        df["area"] = df["area"] / 1e6
        df_prepared = df[["region", "area", "power_potential"]].rename(
            columns={
                "area": f"Fläche {type.title()} [km2]",
                "power_potential": f"Leistung {type.title()} [GW]",
                "region": "Kreis",
            }
        )
        if type == "wind":
            df_prepared.drop("Kreis", axis=1, inplace=True)
        potentials_table = pd.concat([potentials_table, df_prepared], axis=1)

    potentials_table = potentials_table.round(1)

    # sum up area and power potential of Brandenburg
    potential_bb = (
        pd.DataFrame(potentials_table.sum(axis=0))
        .transpose()
        .rename({0: "Brandenburg"})
    )
    potential_bb["Kreis"] = "Summe Brandenburg"
    potentials_table = pd.concat([potentials_table, potential_bb], axis=0)

    dp.save_df(df=potentials_table, path=output_tables)
