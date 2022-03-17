# coding: utf-8
r"""
Inputs
-------
filename_pv_agriculture : str
    ``raw/area_potential/2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv``: Path incl.
    file name of area potential of agriculture pv
filename_pv_road_railway : str
    ``raw/area_potential/2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv``: Path incl.
    file name of area potential of roads and railway pv
filename_wind : str
    ``raw/area_potential/2021-05-18_wind_brandenburg_kreise_epsg32633.csv``: Path incl. file name
    of area potential wind
filename_kreise : str
    ``raw/lookup_table_brandenburg_kreise.csv``: Path incl. file name of lookup table Kreise and
    NUTS of Brandenburg
filename_assumptions : str
    ``raw/scalars_base_2050.csv``: Path incl. file name of assumptions
output_dir : str
    ``results/_resources/RE_potential/``: Path of output directory where power and area potential of
    single areas and of "Landkreise" is saved

Outputs
---------
pd.DataFrame
    Multiple data frames with power and area potential for single areas and aggregated to
    "Landkreise". For details see 'Description' below.


Description
-------------
Please note that this script is not integrated into the pipeline, yet.

Calculates the area and power potential of photovoltaics and wind energy. The area of single areas
are retrieved from csv files and processed. The resulting area and power potential for "Landkreise"
is saved in `output_dir/power_potential_wind_kreise.csv` for wind and in
`output_dir/power_potential_pv_kreise.csv` for pv:
    - power potential in column 'power_potential'
    - power potential after reducing by degree of agreement in column 'power_potential_agreed'
    - area potential in column 'area'
    - overlapping area in columns 'overlap_pv_agriculture_area', 'overlap_pv_road_railway_area',
      only for pv: 'overlap_wind_area'

Additionally, saves the following data in `output_dir`:
    - joined pv area potential from `filename_pv_agriculture` and `filename_pv_road_railway` of
      single areas in column 'area_raw' in "area_potential_single_areas_pv_raw.csv"
    - area potential of single areas in column 'area' in
      f"area_potential_single_areas_{type}.csv" for type in ['wind', 'pv']
    - power potential of single areas in column 'power_potential' and reduced power potential (by
      degree of agreement) in column 'power_potential_agreed' in
      f"power_potential_single_areas_{type}.csv" for type in ['wind', 'pv']
"""

import os
import sys
import pandas as pd

from oemof_b3.tools import data_processing as dp

# global variables
DROP_COLS = [
    "ADE",
    "GF",
    "BSG",
    "ARS",
    "AGS",
    "SDV_ARS",
    "IBZ",
    "BEM",
    "NBD",
    "SN_L",
    "SN_R",
    "SN_K",
    "SN_V1",
    "SN_G",
    "FK_S3",
    "ARS_0",
    "AGS_0",
    "DEBKG_ID",
    "RS",
    "SDV_RS",
    "RS_0",
]


def add_names_of_kreise(df, filename_kreise):
    r"""
    Merges names of Kreise of Brandenburg to `df` according to 'NUTS'.

    Parameters
    ----------
    df: pandas.DataFrame
        Contains at least a column 'NUTS' with NUTS of Kreise of Brandenburg
    filename_kreise: str
        File name including path to csv containing lookup table for Kreise and NUTS in Brandenburg

    Returns
    -------
    df_with_names: pandas.DataFrame
        `df` with added Kreise according to NUTS in column 'Kreis'

    """
    kreise = pd.read_csv(filename_kreise)
    df.index.name = "NUTS"
    df_with_names = pd.merge(left=df, right=kreise, on="NUTS")
    df_with_names.set_index("NUTS", inplace=True)
    return df_with_names


def calculate_potential_pv(
    filename_agriculture,
    filename_road_railway,
    output_dir,
    filename_kreise,
    filename_assumptions,
):
    r"""
    Calculates the area and power potential of photovoltaics.

    - Merges area potential of agricultural areas (file `filename_agriculture`) and areas along
      roads and railways (file `filename_road_railway`)
    - Overlapping areas are subtracted from agricultural areas
    - Calculates pv area potential for each area and Landkreis, methods see
      :py:func:`~.calculate_area_potential`
    - Calculates pv power potential for each area and Landkreis, methods see
      :py:func:`~.calculate_power_potential`

    The following data is saved:
    - "raw" pv area potential of single areas in column 'area_raw' in
      "area_potential_single_areas_pv_raw.csv" in `output_dir`
    - pv area potential of single areas after processing with :py:func:`~.calculate_area_potential`
      in column 'area_agreed' in "area_potential_single_areas_pv.csv" in `output_dir`
    - pv power [MW] and area [m²] potential of "Landkreise" in columns 'area_agreed' and
      'power_potential' in `output_dir/power_potential_pv_kreise.csv`

    Parameters
    ----------
    filename_agriculture: str
        Path including file name to raw area potentials of pv on agricultural areas
    filename_road_railway: str
        Path including file name to raw area potentials of pv along roads and railways
    output_dir: str
        Directory where outputs are saved.
    filename_kreise: str
        File name including path to csv containing lookup table for Kreise and NUTS in Brandenburg
    filename_assumptions: str
        File name including path to csv containing assumptions (scalars) for wind and pv potential.

    Returns
    -------
    None


    """
    # read total ground-mounted pv area potential from csvs (agricultural + roads and railways)
    areas_agriculture = (
        pd.read_csv(filename_agriculture, header=0)
        .set_index("fid")
        .drop(DROP_COLS, axis=1)
        .rename(columns={"area": "area_pv_raw"})
    )
    areas_road_railway = (
        pd.read_csv(filename_road_railway, header=0)
        .set_index("fid")
        .drop(DROP_COLS, axis=1)
        .rename(columns={"area": "area_pv_raw"})
    )

    # subtract overlapping areas from road_railway and merge data frames
    areas_agriculture["area"] = (
        areas_agriculture["area_pv_raw"]
        - areas_agriculture["overlap_pv_road_railway_area"]
    )
    areas_road_railway["area"] = areas_road_railway["area_pv_raw"]
    areas_pv = pd.concat([areas_road_railway, areas_agriculture], axis=0, sort=True)

    # save total pv area potential
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    filename = os.path.join(output_dir, "area_potential_single_areas_pv_raw.csv")
    areas_pv.to_csv(filename, sep=";")

    # read parameters for calculations like minimum required area and degree of agreement from
    # `filename_assumptions`
    df = dp.load_b3_scalars(filename_assumptions)
    pv_assumptions = df.loc[df["carrier"] == "solar"].set_index("var_name")
    # get parameters
    minimum_area = pv_assumptions.at["minimum_area", "var_value"]
    degree_of_agreement = pv_assumptions.at["degree_of_agreement", "var_value"]
    required_specific_area = (
        pv_assumptions.at["required_specific_area", "var_value"] / 1e6
    )
    reduction_by_wind_overlap = pv_assumptions.at[
        "reduction_by_wind_overlap", "var_value"
    ]

    # calculate area potential
    filename_single_areas = calculate_area_potential(
        area_data=areas_pv,
        type="pv",
        minimum_area=minimum_area,
        output_dir=output_dir,
        reduction_by_wind_overlap=reduction_by_wind_overlap,
    )

    # calculate power potential
    calculate_power_potential(
        type="pv",
        input_file=filename_single_areas,
        required_specific_area=required_specific_area,
        degree_of_agreement=degree_of_agreement,
        output_dir=output_dir,
        filename_kreise=filename_kreise,
    )


def calculate_potential_wind(
    filename_wind,
    output_dir,
    filename_kreise,
    filename_assumptions,
):
    r"""
    Calculates the area and power potential of wind energy.

    - Calculates wind area potential for each area and Landkreis, methods see
      :py:func:`~.calculate_area_potential`
    - Calculates wind power potential for each area and Landkreis, methods see
      :py:func:`~.calculate_power_potential`

    The following data is saved:
    - wind area potential of single areas in [m²] in column 'area' in
      "area_potential_single_areas_wind.csv" in `output_dir`
    - wind power [MW] and area [m²] potential of "Landkreise" in columns 'area' and
      'power_potential' in `output_dir/power_potential_wind_kreise.csv`

    Parameters
    ----------
    filename_wind: str
        Path including file name to raw area potentials for wind energy
    output_dir: str
        Directory where outputs are saved.
    filename_kreise: str
        File name including path to csv containing lookup table for Kreise and NUTS in Brandenburg
    filename_assumptions: str
        File name including path to csv containing assumptions (scalars) for wind and pv potential.

    Returns
    -------
    None

    """
    # read area potential wind
    areas = (
        pd.read_csv(filename_wind, header=0).set_index("fid").drop(DROP_COLS, axis=1)
    )

    # create directory for intermediate results if not existent
    # save total wind area potential
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # read parameters for calculations like minimum required area and degree of agreement from
    # `filename_assumptions`
    df = dp.load_b3_scalars(filename_assumptions)
    wind_assumptions = df.loc[df["carrier"] == "wind"].set_index("var_name")
    # get parameters
    minimum_area = wind_assumptions.at["minimum_area", "var_value"]
    degree_of_agreement = wind_assumptions.at["degree_of_agreement", "var_value"]
    required_specific_area = (
        wind_assumptions.at["required_specific_area", "var_value"] / 1e6
    )

    # calculate area potential
    filename_single_areas = calculate_area_potential(
        area_data=areas,
        type="wind",
        minimum_area=minimum_area,
        output_dir=output_dir,
    )

    # calculate power potential
    calculate_power_potential(
        type="wind",
        input_file=filename_single_areas,
        required_specific_area=required_specific_area,
        degree_of_agreement=degree_of_agreement,
        output_dir=output_dir,
        filename_kreise=filename_kreise,
    )


def calculate_area_potential(
    area_data,
    type,
    minimum_area,
    output_dir,
    reduction_by_wind_overlap=None,
):
    r"""
    Calculates area potential for wind or pv for areas in `area_data` and saves results to csvs.

    Potential areas in `area_data` are processed in the following way:
    - areas smaller than `minimum_area` are excluded
    - if `type` is "pv", area is reduced by a certain percentage
      (`reduction_by_wind_overlap`) in case there is overlapping with wind potential area in sum.

    The following data is saved in `output_dir`:
    - Area potential of single areas in column 'area' in
      f"output_dir/area_potential_single_areas_{type}.csv"

    Parameters
    ----------
    area_data: `pandas.DataFrame<frame>`
        Contains area potentials for energy carrier `type`.
    type: str
        Type of area potential "pv" or "wind".
    minimum_area: float
        Minimum required area for considering area as potential for installing plants of `type`.
    output_dir: str
        Directory where outputs are saved.
    reduction_by_wind_overlap: float or None
        Reduction of area if `type` is "pv" in case there is overlapping with wind
        potential area in sum.
        Default: None.

    Returns
    -------
    filename_single_areas: str
        Path including file name where the area potential of the single areas is saved

    """
    # remove areas smaller minimum required area
    areas = area_data.copy()
    areas = areas.loc[area_data["area"] >= minimum_area]

    # take pv area potential overlap with wind area potential into account; not necessary for wind
    # as wind has priority
    if type == "pv":
        # reduce areas by a small percentage: adapt in "area_agreed" and save old value in extra
        # column
        areas["area_before_reduction_by_overlap"] = areas["area"]
        areas["area"] = areas["area"] - (
            areas["overlap_wind_area"] * reduction_by_wind_overlap
        )
    elif type == "wind":
        pass
    else:
        raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")

    # save area potential of single areas in m²
    filename_single_areas = os.path.join(
        output_dir,
        f"area_potential_single_areas_{type}.csv",
    )
    areas.to_csv(filename_single_areas, sep=";")

    return filename_single_areas


def calculate_power_potential(
    type,
    input_file,
    required_specific_area,
    degree_of_agreement,
    output_dir,
    filename_kreise,
):
    r"""
    Calculates wind or pv power potential for each area and Landkreis and saves results to csv.

    Saves the following data for "Landkreise" in `output_dir/power_potential_{type}_kreise.csv`:
    - power potential in column 'power_potential'
    - power potential after reducing by degree of agreement in column 'power_potential_agreed'
    - area potential in column 'area'
    - percentage of overlap between the areas in columns 'overlap_pv_agriculture_percent',
      'overlap_pv_road_railway_percent', 'overlap_wind_percent'

    Parameters
    ----------
    type: str
        Type of area potential "pv" or "wind"
    input_file: str
        Filename including path to file containing area potential
    required_specific_area: float
        Specific area required per wind turbine or per installed capacity pv.
    degree_of_agreement: float or None
        The degree of agreement (ger: Einigungsgrad) is a factor and represents the
        ratio between the area potential that is assumed to be agreed on between
        different parties and the calculated available area potential.
        If None, `degree_of_agreement` is set to 1
        Default: None.
    output_dir: str
        Directory where outputs are saved.
    filename_kreise: str
        File name including path to csv containing lookup table for Kreise and NUTS in Brandenburg

    Returns
    -------
    None

    """
    # read area potential
    potentials = pd.read_csv(input_file, header=0, sep=";")

    # calculate power potential with required specific area
    potentials["power_potential"] = potentials["area"] * required_specific_area

    # resize power potentials by degree of agreement (Einigungsgrad)
    if degree_of_agreement is None:
        degree_of_agreement = 1
    potentials["power_potential_agreed"] = (
        potentials["power_potential"] * degree_of_agreement
    )

    if type == "wind":
        keep_cols = [
            "area",
            "overlap_pv_agriculture_area",
            "overlap_pv_road_railway_area",
            "power_potential",
            "power_potential_agreed",
        ]

    elif type == "pv":
        keep_cols = [
            "area",
            "overlap_pv_agriculture_area",
            "overlap_pv_road_railway_area",
            "overlap_wind_area",
            "power_potential",
            "power_potential_agreed",
        ]
    else:
        raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")

    # sum up area and power potential of "Landkreise"
    potentials_kreise = potentials.groupby("NUTS")[keep_cols].sum()

    # sum up area and power potential of Brandenburg
    potential_bb = (
        pd.DataFrame(potentials_kreise.sum(axis=0))
        .transpose()
        .rename({0: "Brandenburg"})
    )
    potentials_kreise = pd.concat([potentials_kreise, potential_bb], axis=0)

    # add names of Kreise in Brandenburg
    potentials_kreise = add_names_of_kreise(
        df=potentials_kreise, filename_kreise=filename_kreise
    )

    # save power potential in MW of NUTS3 (Landkreise)
    filename_nuts3 = os.path.join(
        output_dir,
        f"power_potential_{type}_kreise.csv",
    )
    potentials_kreise.to_csv(filename_nuts3, sep=";")

    # additionally save power potential of single areas in MW
    filename_single_areas = os.path.join(
        output_dir,
        f"power_potential_single_areas_{type}.csv",
    )
    potentials.to_csv(filename_single_areas, sep=";")


if __name__ == "__main__":
    filename_pv_agriculture = sys.argv[1]
    filename_pv_road_railway = sys.argv[2]
    filename_wind = sys.argv[3]
    filename_kreise = sys.argv[4]
    filename_assumptions = sys.argv[5]
    output_dir = sys.argv[6]

    # calculate pv potential
    calculate_potential_pv(
        filename_agriculture=filename_pv_agriculture,
        filename_road_railway=filename_pv_road_railway,
        output_dir=output_dir,
        filename_kreise=filename_kreise,
        filename_assumptions=filename_assumptions,
    )

    # calculate wind potential
    calculate_potential_wind(
        filename_wind=filename_wind,
        output_dir=output_dir,
        filename_kreise=filename_kreise,
        filename_assumptions=filename_assumptions,
    )
