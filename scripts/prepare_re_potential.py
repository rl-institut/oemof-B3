# coding: utf-8
r"""
Inputs
-------
type : str
    Type of area potential to be calculated: "pv" or "wind"
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
    - area potential before processing in column 'area'
    - area potential after processing and reducing by degree of agreement in column 'area_agreed'
    - percentage of overleaps between the areas in columns 'overleap_pv_agriculture_percent',
      'overleap_pv_road_railway_percent', only for pv: 'overleap_wind_percent'
    - only for wind: amount of wind turbines per area in column 'amount_of_wind_turbines'

Additonally saves the following data in "../results/RE_potential":
    - joined pv area potential of single areas in column 'area_raw' in
      "area_potential_single_areas_pv_raw.csv"
    - area potential of single areas after processing in column 'area_agreed' in
      f"area_potential_single_areas_{type}.csv" for `type`

"""
import os
import sys
import numpy as np
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
    filename_agriculture, filename_road_railway, output_file, out_dir_intermediate=None
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
      "area_potential_single_areas_pv_raw.csv" in `out_dir_intermediate`
    - pv area potential of single areas after processing with :py:func:`~.calculate_area_potential`
      in column 'area_agreed' in "area_potential_single_areas_pv.csv" in `out_dir_intermediate`
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
    out_dir_intermediate: str
        Directory where intermediate outputs are saved. If None, is set to "../results/RE_potential"
        Default: None.

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
    if not os.path.exists(out_dir_intermediate):
        os.mkdir(out_dir_intermediate)
    filename = os.path.join(
        out_dir_intermediate, "area_potential_single_areas_pv_raw.csv"
    )
    areas_pv.to_csv(filename)

    # read parameters for calculatons like minimum required area and degree of agreement from
    # 'xyz.csv' todo
    minimum_area, degree_of_agreement, required_specific_area = (
        1e4,
        0.1,
        0.8e4,
    )  # minimum area pv 1ha = 10000 m², required specific area 0.8 ha per MW

    # calculate area potential
    filename_single_areas = calculate_area_potential(
        area_data=areas_pv,
        type="pv",
        minimum_area=minimum_area,
        degree_of_agreement=degree_of_agreement,
        out_dir_intermediate=out_dir_intermediate,
    )

    # calcualte power potential
    calculate_power_potential(
        type="pv",
        input_file=filename_single_areas,
        required_specific_area=required_specific_area,
        output_file=output_file,
        nominal_power=None,
    )


def calculate_potential_wind(filename_wind, output_file, out_dir_intermediate=None):
    r"""
    Calculates the area and power potential of wind energy.

    - Calculates wind area potential for each area and Landkreis, methods see
      :py:func:`~.calculate_area_potential`
    - Calculates wind power potential for each area and Landkreis, methods see
      :py:func:`~.calculate_power_potential`

    The following data is saved:
    - wind area potential of single areas in column 'area_agreed' in
      "area_potential_single_areas_wind.csv" in `out_dir_intermediate`
    - wind power [MW] and area [m²] potential of "Landkreise" in columns 'area_agreed' and
      'power_potential' in `output_file`

    Parameters
    ----------
    filename_wind: str
        Path including file name to raw area potentials for wind energy
    output_file: str
        File name including path to output of power potential of wind for "Landkreise"
    out_dir_intermediate: str
        Directory where intermediate outputs are saved. If None, is set to "../results/RE_potential"
        Default: None.

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
    if not os.path.exists(out_dir_intermediate):
        os.mkdir(out_dir_intermediate)

    # read parameters for calculatons like minimum required area and degree of agreement from
    # 'xyz.csv' todo
    (
        minimum_area,
        degree_of_agreement,
        required_specific_area,
        nominal_power,
        reduction_by_wind_overleap,
    ) = (
        485,
        0.5,
        20e4,  # required_specific_area 20ha = 20*e⁴ m² per turbine
        4.2,  # nominal power in MW
        0.1,
    )

    # calculate area potential
    filename_single_areas = calculate_area_potential(
        area_data=areas,
        type="wind",
        minimum_area=minimum_area,
        degree_of_agreement=degree_of_agreement,
        out_dir_intermediate=out_dir_intermediate,
        reduction_by_wind_overleap=reduction_by_wind_overleap,
    )

    # calcualte power potential
    calculate_power_potential(
        type="wind",
        input_file=filename_single_areas,
        required_specific_area=required_specific_area,
        output_file=output_file,
        nominal_power=nominal_power,
    )


def calculate_area_potential(
    area_data,
    type,
    minimum_area,
    out_dir_intermediate,
    degree_of_agreement=None,
    reduction_by_wind_overleap=None,
):
    r"""
    Calculates area potential for wind or pv for single areas and "Landkreise" and saves results to
    csvs.

    Potential areas in `area_data` are processed in the following way:
    - areas smaller than `minimum_area` are excluded
    - areas are reduced by `degree_of_agreement`
    - if `type` is "pv", area is further reduced by a certain percentage
      (`reduction_by_wind_overleap`) in case there is overleapping with wind potential area in sum.

    The following data is saved in `out_dir_intermediate`:
    - Area potential of single areas for `degree_of_agreement` in column 'area_agreed' in
      f"area_potential_single_areas_{type}_agreement_{degree_of_agreement}.csv"

    Parameters
    ----------
    area_data: `pandas.DataFrame<frame>`
        Contains area potentials for energy carrier `type`.
    type: str
        Type of area potential "pv" or "wind"
    minimum_area: float
        Minimum required area for considering area as potential for installing plants of `type`
    out_dir_intermediate: str
        Directory where intermediate outputs are saved
        Default: None.
    degree_of_agreement: float or None
        The degree of agreement (ger: Einigungsgrad) is a factor and represents the
        ratio between the area potential that is assumed to be agreed on between
        different parties and the calculated available area potential.
        If None, `degree_of_agreement` is set to 1
        Default: None.
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

    # resize areas by degree of agreement (Einigungsgrad)
    if degree_of_agreement is None:
        degree_of_agreement = 1
    areas["area_agreed"] = areas["area"] * degree_of_agreement

    # take pv area potential overleap with wind area potential into account; not necessary for wind
    # as wind has priority
    if type == "pv":
        # by degree of agreement reduced area potential < area potential - overleap area with wind
        # potential areas  --> no action necessary
        if (
            areas["area_agreed"].sum()
            > areas["area"].sum() - areas["overleap_wind_area"].sum()
        ):
            # otherwise: reduce areas by a small percentage: adapt in "area_agreed" and save old
            # value in extra column
            areas["area_agreed_before_reduction_by_overleap"] = areas["area_agreed"]
            areas["area_agreed"] = areas["area_agreed"] * (
                1 - reduction_by_wind_overleap
            )
    elif type == "wind":
        pass
    else:
        raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")

    # save area potential of single areas in m² (needed for further calculations of wind potential)
    add_on = str(degree_of_agreement).replace('.', '_')
    filename_single_areas = os.path.join(
        out_dir_intermediate,
        f"area_potential_single_areas_{type}_agreement_{add_on}.csv",
    )
    areas.to_csv(filename_single_areas)

    return filename_single_areas


def calculate_power_potential(
    type, input_file, output_file, required_specific_area, nominal_power=None
):
    r"""
    Calculates wind or pv power potential for each area and Landkreis and saves results to csv.

    Saves the following data for "Landkreise" in `output_file`.
    - power potential in column 'power_potential'
    - area potential before processing in column 'area'
    - area potential after processing and reducing by degree of agreement in column 'area_agreed'
    - percentage of overleaps between the areas in columns 'overleap_pv_agriculture_percent',
      'overleap_pv_road_railway_percent', 'overleap_wind_percent'
    - if `type` is "wind", amount of wind turbines per area in columns
      amount_of_wind_turbines_float' and 'amount_of_wind_turbines', amount of wind turbines is
      rounded down to integers, except if value < 1, then amount of wind turbines is 1 as a single
      wind turbine needs less space (no distancing to other wind turbines)

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
    nominal_power: float
        Nominal power of wind turbine type; not needed for pv.
        Default: None.

    Returns
    -------
    None

    """
    # read area potential
    potentials = pd.read_csv(input_file, header=0)

    # calculate power potential with required specific area per wind turbine / per installed
    # capacity pv
    if type == "wind":
        # calculate amount of wind turbines per area
        if nominal_power is None:
            raise ValueError(
                f"`nominal_power` is None, but needs to be set for type {type}."
            )
        # calculate amount of wind turbines per area
        potentials["amount_of_wind_turbines_float"] = (
            potentials["area_agreed"] / required_specific_area
        )
        # round amount of wind turbines to integer:
        # round to lower integer except if value < 1, then amount of wind turbines is 1 as
        # a single wind turbine needs less space (no distancing to other wind turbines).
        potentials["amount_of_wind_turbines"] = potentials[
            "amount_of_wind_turbines_float"
        ].apply(np.floor)
        indices = potentials.loc[potentials["amount_of_wind_turbines_float"] < 1].index
        potentials.loc[indices, "amount_of_wind_turbines"] = potentials.loc[
            indices, "amount_of_wind_turbines_float"
        ].apply(np.ceil)
        # calculate power potential per area
        potentials["power_potential"] = (
            potentials["amount_of_wind_turbines"] * nominal_power
        )
        # sum up area and power potential of "Landkreise"
        potentials_kreise = potentials.groupby("NUTS")[
            "area",
            "overleap_pv_agriculture_percent",
            "overleap_pv_road_railway_percent",
            "area_agreed",
            "amount_of_wind_turbines",
            "power_potential",
        ].sum()

    elif type == "pv":
        # calculate power potential
        potentials["power_potential"] = (
            potentials["area_agreed"] / required_specific_area
        )

        # sum up area and power potential of "Landkreise"
        potentials_kreise = potentials.groupby("NUTS")[
            "area",
            "overleap_pv_agriculture_percent",
            "overleap_pv_road_railway_percent",
            "overleap_wind_percent",
            "area_agreed",
            "power_potential",
        ].sum()
    else:
        raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")

    # save power potential in MW of NUTS3 (Landkreise) todo use SI units?
    potentials_kreise.to_csv(output_file)


if __name__ == "__main__":
    type = sys.argv[1]
    output_file = sys.argv[4]
    if type == "pv":
        filename_agriculture = sys.argv[2][0]
        filename_road_railway = sys.argv[2][1]
        filename_assumptions = sys.argv[3]
        calculate_potential_pv(
            filename_agriculture=filename_agriculture,
            filename_road_railway=filename_road_railway,
            output_file=output_file,
        )
    elif type == "wind":
        filename_wind = sys.argv[2][0]
        filename_assumptions = sys.argv[3]
        calculate_potential_wind(
            filename_wind=filename_wind,
            output_file=output_file,
        )
    else:
        raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")
