# coding: utf-8
r"""
Inputs
-------
filename_agriculture : str
    Path incl. file name to area potential agriculture pv csv
filename_road_railway : str
    Path incl. file name to area potential roads and railway pv csv
filename_wind : str
    Path incl. file name to area potential wind csv
filename_assumptions : str
    Path incl. file name to assumptions csv

Outputs
---------
output_file : str
    Path incl. file name to output: power potential wind/pv of "Landkreise"

Description
-------------
Calculates the area and power potential of photovoltaics or wind energy depending on
`type`. The area of single areas are retrieved from csv files and processed. The
resulting area and power potential is saved in `output_file`

Saves the following data for "Landkreise":
    - power potential in column 'power_potential'
    - power potential after reducing by degree of agreement in column 'power_potential_agreed'
    - area potential in column 'area'
    - percentage of overleap between the areas in columns 'overleap_pv_agriculture_percent',
      'overleap_pv_road_railway_percent', only for pv: 'overleap_wind_percent'
    - all values for Brandenburg in row 'Brandenburg'

Additonally saves the following data in "../results/RE_potential":
    - joined pv area potential of single areas in column 'area_raw' in
      "area_potential_single_areas_pv_raw.csv"
    - area potential of single areas in column 'area' in
      f"area_potential_single_areas_{type}.csv" for `type`
    - power potential of single areas in column 'power_potential' and reduced power potential (by
      degree of agreement) in column 'power_potential_agreed' in
      f"power_potential_single_areas_{type}.csv" for `type`

"""
import os
import sys
import pandas as pd

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


def calculate_potential_pv(
    filename_agriculture, filename_road_railway, output_file, secondary_output_dir
):
    r"""
    Calculates the area and power potential of photovoltaics.

    - Merges area potential of agricultural areas (file `filename_agriculture`) and areas along
      roads and railways (file `filename_road_railway`)
    - Overleaping areas are substracted from agricultural areas
    - Calculates pv area potential for each area and Landkreis, methods see
      :py:func:`~.calculate_area_potential`
    - Calculates pv power potential for each area and Landkreis, methods see
      :py:func:`~.calculate_power_potential`

    The following data is saved:
    - "raw" pv area potential of single areas in column 'area_raw' in
      "area_potential_single_areas_pv_raw.csv" in `secondary_output_dir`
    - pv area potential of single areas after processing with :py:func:`~.calculate_area_potential`
      in column 'area_agreed' in "area_potential_single_areas_pv.csv" in `secondary_output_dir`
    - pv power [MW] and area [m²] potential of "Landkreise" in columns 'area_agreed' and
      'power_potential' in `output_file`

    Parameters
    ----------
    filename_agriculture: str
        Path including file name to raw area potentials of pv on agricultural areas
    filename_road_railway: str
        Path including file name to raw area potentials of pv along roads and railways
    output_file: str
        File name including path to output of power potential of pv for "Landkreise"
    secondary_output_dir: str
        Directory where secondary outputs are saved.

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

    # substract overleaping areas from road_railway and merge data frames
    areas_agriculture["area"] = (
        areas_agriculture["area_pv_raw"]
        - areas_agriculture["overleap_pv_road_railway_area"]
    )
    areas_road_railway["area"] = areas_road_railway["area_pv_raw"]
    areas_pv = pd.merge(left=areas_road_railway, right=areas_agriculture, how="outer")

    # save total pv area potential
    if not os.path.exists(secondary_output_dir):
        os.mkdir(secondary_output_dir)
    filename = os.path.join(
        secondary_output_dir, "area_potential_single_areas_pv_raw.csv"
    )
    areas_pv.to_csv(filename)

    # read parameters for calculatons like minimum required area and degree of agreement from
    # 'xyz.csv' todo
    (
        minimum_area,
        degree_of_agreement,
        required_specific_area,
        reduction_by_wind_overleap,
    ) = (
        1e4,  # 1 ha --> 1e4 m²
        1.0,
        125 / 1e6,  # 125 MW/km² --> 125/1e6 MW/m²
        0.1,
    )
    # todo required_specific_area / 1e6
    # calculate area potential
    filename_single_areas = calculate_area_potential(
        area_data=areas_pv,
        type="pv",
        minimum_area=minimum_area,
        secondary_output_dir=secondary_output_dir,
        reduction_by_wind_overleap=reduction_by_wind_overleap,
    )

    # calcualte power potential
    calculate_power_potential(
        type="pv",
        input_file=filename_single_areas,
        required_specific_area=required_specific_area,
        degree_of_agreement=degree_of_agreement,
        output_file=output_file,
        secondary_output_dir=secondary_output_dir,
    )


def calculate_potential_wind(filename_wind, output_file, secondary_output_dir=None):
    r"""
    Calculates the area and power potential of wind energy.

    - Calculates wind area potential for each area and Landkreis, methods see
      :py:func:`~.calculate_area_potential`
    - Calculates wind power potential for each area and Landkreis, methods see
      :py:func:`~.calculate_power_potential`

    The following data is saved:
    - wind area potential of single areas in [m²] incolumn 'area' in
      "area_potential_single_areas_wind.csv" in `secondary_output_dir`
    - wind power [MW] and area [m²] potential of "Landkreise" in columns 'area' and
      'power_potential' in `output_file`

    Parameters
    ----------
    filename_wind: str
        Path including file name to raw area potentials for wind energy
    output_file: str
        File name including path to output of power potential of wind for "Landkreise"
    secondary_output_dir: str
        Directory where secondary outputs are saved.

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
    if not os.path.exists(secondary_output_dir):
        os.mkdir(secondary_output_dir)

    # read parameters for calculatons like minimum required area and degree of agreement from
    # 'xyz.csv' todo
    (minimum_area, degree_of_agreement, required_specific_area,) = (
        485,  # m²
        1.0,
        21 / 1e6,  # 21 MW/km² --> 21/1e6 MW/m²
    )
    # todo required_specific_area / 1e6
    # calculate area potential
    filename_single_areas = calculate_area_potential(
        area_data=areas,
        type="wind",
        minimum_area=minimum_area,
        secondary_output_dir=secondary_output_dir,
    )

    # calcualte power potential
    calculate_power_potential(
        type="wind",
        input_file=filename_single_areas,
        required_specific_area=required_specific_area,
        output_file=output_file,
        degree_of_agreement=degree_of_agreement,
        secondary_output_dir=secondary_output_dir,
    )


def calculate_area_potential(
    area_data,
    type,
    minimum_area,
    secondary_output_dir,
    reduction_by_wind_overleap=None,
):
    r"""
    Calculates area potential for wind or pv for areas in `area_data` and saves results to csvs.

    Potential areas in `area_data` are processed in the following way:
    - areas smaller than `minimum_area` are excluded
    - if `type` is "pv", area is reduced by a certain percentage
      (`reduction_by_wind_overleap`) in case there is overleapping with wind potential area in sum.

    The following data is saved in `secondary_output_dir`:
    - Area potential of single areas in column 'area' in
      f"area_potential_single_areas_{type}.csv"

    Parameters
    ----------
    area_data: `pandas.DataFrame<frame>`
        Contains area potentials for energy carrier `type`.
    type: str
        Type of area potential "pv" or "wind".
    minimum_area: float
        Minimum required area for considering area as potential for installing plants of `type`.
    secondary_output_dir: str
        Directory where intermediate outputs are saved.
    reduction_by_wind_overleap: float or None
        Reduction of area if `type` is "pv" in case there is overleapping with wind
        potential area in sum.
        Default: None.

    Returns
    -------
    filename_single_areas: str
        Path including file name where the area potential of the single areas is saved

    """
    # remove areas smaller minimum required area
    areas = area_data.loc[area_data["area"] >= minimum_area]

    # take pv area potential overleap with wind area potential into account; not necessary for wind
    # as wind has priority
    if type == "pv":
        # reduce areas by a small percentage: adapt in "area_agreed" and save old value in extra
        # column
        areas["area_before_reduction_by_overleap"] = areas["area"]
        areas["area"] = areas["area"] * (1 - reduction_by_wind_overleap)
    elif type == "wind":
        pass
    else:
        raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")

    # save area potential of single areas in m² (needed for further calculations of wind potential)
    filename_single_areas = os.path.join(
        secondary_output_dir,
        f"area_potential_single_areas_{type}.csv",
    )
    areas.to_csv(filename_single_areas)

    return filename_single_areas


def calculate_power_potential(
    type,
    input_file,
    output_file,
    required_specific_area,
    degree_of_agreement,
    secondary_output_dir=None,
):
    r"""
    Calculates wind or pv power potential for each area and Landkreis and saves results to csv.

    Saves the following data for "Landkreise" in `output_file`.
    - power potential in column 'power_potential'
    - power potential after reducing by degree of agreement in column 'power_potential_agreed'
    - area potential in column 'area'
    - percentage of overleap between the areas in columns 'overleap_pv_agriculture_percent',
      'overleap_pv_road_railway_percent', 'overleap_wind_percent'
    - all values for Brandenburg in row 'Brandenburg'

    Parameters
    ----------
    type: str
        Type of area potential "pv" or "wind"
    input_file: str
        Filename including path to file containing area potential
    output_file: str
        File name including path to output of power potential of pv for "Landkreise"
    required_specific_area: float
        Specific area required per wind turbine or per installed capacity pv.
    degree_of_agreement: float or None
        The degree of agreement (ger: Einigungsgrad) is a factor and represents the
        ratio between the area potential that is assumed to be agreed on between
        different parties and the calculated available area potential.
        If None, `degree_of_agreement` is set to 1
        Default: None.
    secondary_output_dir: str
        Directory where secondary outputs are saved.

    Returns
    -------
    None

    """
    # read area potential
    potentials = pd.read_csv(input_file, header=0)

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
            "overleap_pv_agriculture_percent",
            "overleap_pv_road_railway_percent",
            "power_potential",
            "power_potential_agreed",
        ]

    elif type == "pv":
        keep_cols = [
            "area",
            "overleap_pv_agriculture_percent",
            "overleap_pv_road_railway_percent",
            "overleap_wind_percent",
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

    # save power potential in MW of NUTS3 (Landkreise) todo use SI units?
    potentials_kreise.to_csv(output_file)

    # additionally save power potential of single areas in MW
    filename_single_areas = os.path.join(
        secondary_output_dir,
        f"power_potential_single_areas_{type}.csv",
    )
    potentials.to_csv(filename_single_areas)


if __name__ == "__main__":
    try:
        output_file = sys.argv[3]
        type = output_file.split("_")[3]
        secondary_output_dir = sys.argv[4]
    except IndexError:
        output_file = sys.argv[4]
        type = output_file.split("_")[3]
        secondary_output_dir = sys.argv[5]
    if type == "pv":
        filename_agriculture = sys.argv[1]
        filename_road_railway = sys.argv[2]
        filename_assumptions = sys.argv[3]
        calculate_potential_pv(
            filename_agriculture=filename_agriculture,
            filename_road_railway=filename_road_railway,
            output_file=output_file,
            secondary_output_dir=secondary_output_dir,
        )
    elif type == "wind":
        filename_wind = sys.argv[1]
        filename_assumptions = sys.argv[2]
        calculate_potential_wind(
            filename_wind=filename_wind,
            output_file=output_file,
            secondary_output_dir=secondary_output_dir,
        )
    else:
        raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")
