# coding: utf-8
r"""
Inputs
------- # todo adpt input description
in_path1 : str
    path of input file with raw opsd data as .csv

Outputs
---------
# todo

Description
-------------
# todo

"""
import os
import sys

import pandas as pd


def calculate_potential_pv(
    filename_agriculture, filename_road_railway, output_file, out_dir_intermediate=None
):
    r"""
    Calculates the area and power potential of photovoltaics.

    - Merges area potential of agricultural areas (file `filename_agriculture`) and areas along roads and railways (file `filename_road_railway`)
    - Overleaping areas are substracted from agricultural areas
    - Calculates PV area potential for each area and Landkreis, methods see :py:func:`~.calculate_area_potential`
    - Calculates PV power potential for each area and Landkreis, methods see :py:func:`~.calculate_power_potential`

    The following data is saved:
    - "raw" PV area potential of single areas in column 'area_raw' in "area_potential_single_areas_pv_raw.csv" in `out_dir_intermediate`
    - PV area potential of single areas after processing with :py:func:`~.calculate_area_potential` in column 'area_agreed' in "area_potential_single_areas_pv.csv" in `out_dir_intermediate`
    - PV power [MW] and area [m²] potential of "Landkreise" in columns 'area_agreed' and 'power_potential' in `output_file`

    Parameters
    ----------
    filename_agriculture: str
        Path including file name to raw area potentials of PV on agricultural areas
    filename_road_railway: str
        Path including file name to raw area potentials of PV along roads and railways
    output_file: str
        File name including path to output of power potential of PV for "Landkreise"
    out_dir_intermediate: str
        Directory where intermediate outputs are saved. If None, is set to "../results/RE_potential"
        Default: None.

    Returns
    -------
    None


    """
    # read total ground-mounted pv area potential from csvs (agricultural + roads and railways)
    drop_cols = [
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
    areas_agriculture = (
        pd.read_csv(filename_agriculture, header=0)
        .set_index("fid")
        .drop(drop_cols, axis=1)
        .rename(columns={"area": "area_pv_raw"})
    )
    areas_road_railway = (
        pd.read_csv(filename_road_railway, header=0)
        .set_index("fid")
        .drop(drop_cols, axis=1)
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

    # read parameters for calculatons like minimum required area and degree of agreement from 'xyz.csv' todo
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

    - Calculates wind area potential for each area and Landkreis, methods see :py:func:`~.calculate_area_potential`
    - Calculates wind power potential for each area and Landkreis, methods see :py:func:`~.calculate_power_potential`

    The following data is saved:
    - wind area potential of single areas in column 'area_agreed' in "area_potential_single_areas_pv.csv" in `out_dir_intermediate`
    - wind power [MW] and area [m²] potential of "Landkreise" in columns 'area_agreed' and 'power_potential' in `output_file`

    Parameters
    ----------
    filename_wind: str
        Path including file name to raw area potentials for wind energy
    output_file: str
        File name including path to output of power potential of PV for "Landkreise"
    out_dir_intermediate: str
        Directory where intermediate outputs are saved. If None, is set to "../results/RE_potential"
        Default: None.

    Returns
    -------
    None


    """
    # read area potential wind
    drop_cols = [
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
    areas = (
        pd.read_csv(filename_wind, header=0).set_index("fid").drop(drop_cols, axis=1)
    )

    # create directory for intermediate results if not existent
    # save total pv area potential
    if not os.path.exists(out_dir_intermediate):
        os.mkdir(out_dir_intermediate)

    # read parameters for calculatons like minimum required area and degree of agreement from 'xyz.csv' todo
    minimum_area, degree_of_agreement, required_specific_area, nominal_power = (
        485,
        0.1,
        20e4,
        4.2,
    )  # required_specific_area 20ha = 20*e⁴ m²

    # calculate area potential
    filename_single_areas = calculate_area_potential(
        area_data=areas,
        type="wind",
        minimum_area=minimum_area,
        degree_of_agreement=degree_of_agreement,
        out_dir_intermediate=out_dir_intermediate,
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
    area_data, type, minimum_area, out_dir_intermediate, degree_of_agreement=None
):
    r"""
    Calculates PV area potential for each area and Landkreis and saves results to csvs.

    Potential areas in `area_data` are processed:
    - areas smaller than `minimum_area` are excluded
    - areas are reduced by `degree_of_agreement`
    - if `type` is "pv", area is further reduced by 10 % in case there is overleapping with wind potential area in sum.

    The following data is saved in `out_dir_intermediate`:
    - Area potential of single areas in column 'area_agreed' in f"area_potential_single_areas_{type}.csv"

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

    Returns
    -------
    filename_single_areas: str
        Path including file name where the area potential of the single areas is saved

    """
    # remove areas smaller minimum required area
    areas = area_data.loc[area_data["area"] >= minimum_area]

    # resize areas by degree of agreement (Einigungsgrad)
    if degree_of_agreement == None:
        degree_of_agreement = 1
    areas["area_agreed"] = areas["area"] * degree_of_agreement

    # take pv area potential overleap with wind area potential into account; not necessary for wind as wind has priority
    if type == "pv":
        # by degree of agreement reduced area potential < area potential - overleap area with wind potential areas  --> no action necessary
        if (
            areas["area_agreed"].sum()
            > areas["area"].sum() - areas["overleap_wind_area"].sum()
        ):
            # otherwise: reduce areas by a small percentage: adapt in "area_agreed" and save in extra column
            areas["area_reduced_by_wind"] = areas["area_agreed"] * 0.9
            areas["area_agreed"] = areas["area_reduced_by_wind"]
    elif type == "wind":
        pass
    else:
        raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")

    # save area potential of single areas in m² (needed for further calculations of wind potential)
    filename_single_areas = os.path.join(
        out_dir_intermediate, f"area_potential_single_areas_{type}.csv"
    )
    areas.to_csv(filename_single_areas)

    # # sum up area potential of "Landkreise"
    # areas_kreise = areas.groupby("NUTS")[
    #     "area_pv_raw",
    #     "area",
    #     "overleap_pv_agriculture_percent",
    #     "overleap_pv_road_railway_percent",
    #     "overleap_wind_percent",
    #     "area_agreed",
    # ].sum()

    # # save area potential of NUTS3 (Landkreise)
    # filename_kreise = os.path.join(out_dir_intermediate, f"area_potential_kreise_{type}.csv")
    # areas_kreise.to_csv(filename_single_areas)

    return filename_single_areas


def calculate_power_potential(
    type, input_file, output_file, required_specific_area, nominal_power=None
):
    r"""
    Calculates PV power potential for each area and Landkreis and saves results to csv.

    Saves power potential of "Landkreise" in column 'power_potential' in `output_file`.

    Parameters
    ----------
    type: str
        Type of area potential "pv" or "wind"
    input_file: str
        Filename including path to file containing area potential
    output_file: str
        File name including path to output of power potential of PV for "Landkreise"
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

    # calculate power potential with required specific area per wind turbine / per installed capacity pv
    if type == "wind":
        # calculate amount of wind turbines per area, rounded down
        if nominal_power == None:
            raise ValueError(
                f"`nominal_power` is None, but needs to be set for type {type}."
            )
        # calculate power potential
        potentials["amount_of_wind_turbines"] = (
            potentials["area_agreed"] / required_specific_area
        )
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

    # todo save power potential of single areas?

    # save power potential in MW of NUTS3 (Landkreise) todo use SI units?
    potentials_kreise.to_csv(output_file)


if __name__ == "__main__":
    # type = sys.argv[1] # pv or wind
    # if type == "pv":
    #     filename_agriculture = sys.argv[2]  # path incl. file name to area potential agriculture pv csv
    #     filename_road_railway = sys.argv[3]  # path incl. file name to area roads and railway pv csv
    #     # filename_assumptions = sys.argv[X]  # path incl. file name to assumptions csv
    #     output_file = sys.argv[4]  # path incl. file name to output: power potential pv of Kreise
    #     calculate_potential_pv(filename_agriculture=filename_agriculture, filename_road_railway=filename_road_railway, output_file=output_file)
    # elif type== "wind":
    #     pass # todo
    # else:
    #     raise ValueError(f"Parameter `type` needs to be 'pv' or 'wind' but is {type}.")

    calculate_potential_pv(
        filename_agriculture="../raw/area_potential/2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv",
        filename_road_railway="../raw/area_potential/2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv",
        out_dir_intermediate="../results/RE_potential",
        output_file="../results/_resources/power_potential_pv_kreise.csv",
    )

    calculate_potential_wind(
        filename_wind="../raw/area_potential/2021-05-18_wind_brandenburg_kreise_epsg32633.csv",
        out_dir_intermediate="../results/RE_potential",
        output_file="../results/_resources/power_potential_wind_kreise.csv",
    )
