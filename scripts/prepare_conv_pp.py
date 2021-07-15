# coding: utf-8
r"""
Inputs
-------
in_path1 : str
    path of input file with raw opsd data as .csv
in_path2 : str
    path of input file with geodata of regions in Germany as .gpgk
in_path3 : str
    path of input file with names of regions in Berlin and Brandenburg as .yaml
in_path4 : str
    path of template for scalar data as .csv
out_path : str
    path of output file with prepared data as .csv

Outputs
---------
pandas.DataFrame
    with grouped and aggregated data of conventional power plants in Berlin and Brandenburg.
    Data is grouped by region, energy source, technology and chp capability and contains
    net capacity and efficiency.

Description
-------------
The script filters the OPSD conventional power plant package for power plants
in Berlin and Brandenburg. The retrieved data is stored in a new dataframe, aggregated and
saved as a csv file in the format of the scalar data template.
Only operating power plants are considered.
"""
import sys

import pandas as pd
import yaml

import oemof_b3.tools.geo as geo

if __name__ == "__main__":
    in_path1 = sys.argv[1]  # path to OPSD data
    in_path2 = sys.argv[2]  # path to geopackage of german regions
    in_path3 = sys.argv[3]  # path to b3_regions.yaml
    in_path4 = sys.argv[4]  # path to _scalar_template.csv
    out_path = sys.argv[5]

    pp_opsd_de = pd.read_csv(in_path1)
    pp_opsd_b3 = pp_opsd_de[pp_opsd_de.state.isin(["Brandenburg", "Berlin"])]
    pp_opsd_b3 = pp_opsd_b3.copy()
    pp_opsd_b3.reset_index(inplace=True, drop=True)

    regions_nuts3_de = geo.load_regions_file(in_path2)

    b3_regions_yaml = open(in_path3, "r")
    b3_regions_content = yaml.load(b3_regions_yaml, Loader=yaml.FullLoader)
    for key, value in b3_regions_content.items():
        b3_regions_list = value

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
        b3_agg.index.get_level_values("energy_source") == "Waste", "efficiency_estimate"
    ].mean()

    b3_agg.reset_index(
        level=["region", "energy_source", "technology", "chp"], inplace=True
    )

    # change data format to _scalar_template
    conv_scalars = b3_agg.melt(id_vars=["region", "energy_source", "technology"])

    scalar_template = pd.read_csv(in_path4, delimiter=";")

    scalar_template["id_scal"] = conv_scalars.index
    scalar_template["scenario"] = "Status quo"
    scalar_template["var_name"] = conv_scalars["variable"]
    scalar_template["carrier"] = conv_scalars["energy_source"]
    scalar_template["region"] = conv_scalars["region"]
    scalar_template["tech"] = conv_scalars["technology"]
    scalar_template["var_value"] = conv_scalars["value"]
    scalar_template[
        "reference"
    ] = "https://doi.org/10.25832/conventional_power_plants/2020-10-01"
    scalar_template[
        "comment"
    ] = "filename: conventional_power_plants_DE.csv, aggregated based on NUTS3 region"

    unit_dict = {"chp": None, "capacity_net_el": "MW", "efficiency_estimate": None}

    def set_unit(df, unit_dict):
        for key, value in unit_dict.items():
            print(key, value)
            df.loc[df["var_name"] == key, "var_unit"] = value

    set_unit(scalar_template, unit_dict)

    # export prepared conventional power plant data
    scalar_template.to_csv(out_path, index=False)
