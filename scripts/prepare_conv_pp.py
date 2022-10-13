# coding: utf-8
r"""
Inputs
-------
in_path1 : str
    ``raw/conventional_power_plants_DE.csv``: path incl. file name of input file with raw OPSD data
in_path2 : str
    ``raw/boundaries_germany_nuts3.gpkg``: path incl. file name of input file with geodata of
    regions in Germany
in_path3 : str
    ``raw/b3_regions.yaml``: path incl. file name of input file with names of regions in Berlin and
    Brandenburg
out_path : str
    ``results/_resources/scal_conv_pp.csv``: path incl. file name of output file with prepared data

Outputs
---------
pandas.DataFrame
    Contains grouped and aggregated data of conventional power plants in Berlin and Brandenburg.
    Data is grouped by region, energy source, technology and chp capability and contains
    net capacity and efficiency.

Description
-------------
The script filters the OPSD conventional power plant package for power plants in the regions Berlin
and Brandenburg. The retrieved data is stored in a new dataframe, aggregated and saved as a csv file
in the format of the scalar data template. Only operating power plants are considered.
"""

import sys

import pandas as pd

import oemof_b3.tools.data_processing as dp
import oemof_b3.tools.geo as geo
from oemof_b3.config import config
from oemof_b3.config.config import load_yaml


if __name__ == "__main__":
    in_path1 = sys.argv[1]  # path to OPSD data
    in_path2 = sys.argv[2]  # path to geopackage of german regions
    in_path3 = sys.argv[3]  # path to b3_regions.yaml
    out_path = sys.argv[4]

    pp_opsd_de = pd.read_csv(in_path1)
    pp_opsd_b3 = pp_opsd_de[pp_opsd_de.state.isin(["Brandenburg", "Berlin"])]
    pp_opsd_b3 = pp_opsd_b3.copy()
    pp_opsd_b3.reset_index(inplace=True, drop=True)

    regions_nuts3_de = geo.load_regions_file(in_path2)

    b3_regions_list = load_yaml(in_path3)

    b3_regions_geo = geo.filter_regions_file(regions_nuts3_de, b3_regions_list)
    pp_opsd_b3 = geo.add_region_to_register(pp_opsd_b3, b3_regions_geo)

    # clean up table columns
    pp_opsd_b3.drop(
        pp_opsd_b3.loc[pp_opsd_b3["status"] == "shutdown"].index, inplace=True
    )
    pp_opsd_b3.drop(
        pp_opsd_b3.loc[pp_opsd_b3["status"] == "shutdown_temporary"].index, inplace=True
    )
    pp_opsd_b3.drop(
        pp_opsd_b3.loc[pp_opsd_b3["status"] == "reserve"].index, inplace=True
    )
    pp_opsd_b3.drop(
        columns=pp_opsd_b3.columns.difference(
            [
                "capacity_net_bnetza",
                "energy_source",
                "technology",
                "chp",
                "chp_capacity_uba",
                "efficiency_estimate",
                "name",
            ]
        ),
        inplace=True,
    )
    pp_opsd_b3.rename(
        columns={"name": "region", "capacity_net_bnetza": "capacity_net_el"},
        inplace=True,
    )
    # treat Waste as Other fuels
    pp_opsd_b3.replace({"Waste": "Other fuels"}, inplace=True)

    # group data by region, energy source, technology and chp capability and
    # aggregate capacity and efficiency
    b3_agg_Series = pp_opsd_b3.groupby(
        ["region", "energy_source", "technology", "chp"]
    ).agg({"capacity_net_el": "sum", "efficiency_estimate": "mean"})
    b3_agg = pd.DataFrame(b3_agg_Series)

    # Estimate efficiency for energy source 'Other fuels'
    b3_agg.loc[
        ("Oder-Spree", "Other fuels", "Steam turbine", "yes"), "efficiency_estimate"
    ] = b3_agg.loc[
        b3_agg.index.get_level_values("energy_source") == "Other fuels",
        "efficiency_estimate",
    ].mean()

    b3_agg.reset_index(
        level=["region", "energy_source", "technology", "chp"], inplace=True
    )

    # rename technologies to oemoflex conventions
    b3_agg.loc[b3_agg["chp"] == "yes", "technology"] = "bpchp"
    b3_agg.loc[b3_agg["technology"] == "Steam turbine", "technology"] = "st"
    b3_agg.loc[b3_agg["technology"] == "Gas turbine", "technology"] = "ocgt"
    b3_agg.loc[b3_agg["technology"] == "Combined cycle", "technology"] = "ccgt"

    b3_agg.drop(columns=["chp"], inplace=True)

    # change data format to oemof-B3 _scalar_template format
    conv_scalars = b3_agg.melt(id_vars=["region", "energy_source", "technology"])
    conv_scalars.rename(
        columns={
            "technology": "tech",
            "variable": "var_name",
            "value": "var_value",
            "energy_source": "carrier",
        },
        inplace=True,
    )
    conv_scalars_prepared = dp.format_header(
        df=conv_scalars,
        header=dp.HEADER_B3_SCAL,
        index_name=config.settings.general.scal_index_name,
    )

    # add additional information as required by template
    conv_scalars_prepared.loc[:, "source"] = "OPSD_conv_pp_DE"
    conv_scalars_prepared.loc[
        :, "comment"
    ] = "filename: conventional_power_plants_DE.csv, aggregated based on NUTS3 region"
    conv_scalars_prepared.loc[:, "scenario_key"] = "Status quo"
    conv_scalars_prepared.loc[:, "type"] = "None"

    # Set units
    unit_dict = {"capacity_net_el": "MW", "efficiency_estimate": "None"}

    def set_unit(df, unit_dict):
        for key, value in unit_dict.items():
            df.loc[df["var_name"] == key, "var_unit"] = value

    set_unit(conv_scalars_prepared, unit_dict)

    # Rename carriers
    carrier_dict = {
        "Biomass and biogas": "biomass",
        "Hard coal": "hard coal",
        "Natural gas": "ch4",
        "Oil": "oil",
        "Lignite": "lignite",
        "Other fuels": "other",
    }
    conv_scalars_prepared.replace(carrier_dict, inplace=True)

    # export prepared conventional power plant data
    dp.save_df(conv_scalars_prepared, out_path)
