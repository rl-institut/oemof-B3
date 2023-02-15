rule download_raw_data:
    # target rule for download of raw input data
    input: "raw/oemof-B3-raw-data.zip"

rule download_zenodo:
    params:
        url="https://sandbox.zenodo.org/record/1164716/files/oemof-B3-raw-data-v0.0.2.zip",
        raw="raw"
    output: "raw/oemof-B3-raw-data.zip"
    shell: "python scripts/download_raw.py {params.url} {output}"

rule prepare_conv_pp:
    input:
        opsd="raw/conventional_power_plants_DE.csv",
        gpkg="raw/boundaries_germany_nuts3.gpkg",
        b3_regions="raw/b3_regions.yaml",
    output: "results/_resources/scal_conv_pp.csv"
    shell: "python scripts/prepare_conv_pp.py {input.opsd} {input.gpkg} {input.b3_regions} {output}"

rule prepare_feedin:
    input:
        wind_feedin="raw/time_series/ninja_wind_country_DE_current_merra-2_nuts-2_corrected.csv",
        pv_feedin="raw/time_series/ninja_pv_country_DE_merra-2_nuts-2_corrected.csv",
        ror_feedin="raw/time_series/DIW_Hydro_availability.csv",
    output: "results/_resources/ts_feedin.csv"
    shell: "python scripts/prepare_feedin.py {input.wind_feedin} {input.pv_feedin} {input.ror_feedin} {output}"

rule prepare_electricity_demand:
    input:
        opsd_url=HTTP.remote("https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv",
                            keep_local=True),
    output: "results/_resources/ts_load_electricity.csv"
    shell: "python scripts/prepare_electricity_demand.py {input.opsd_url} {output}"

rule prepare_vehicle_charging_demand:
    input:
        input_dir="raw/time_series/vehicle_charging",
        scalars="raw/scalars/demands.csv",
    output: "results/_resources/ts_load_electricity_vehicles.csv"
    params:
        logfile="results/_resources/ts_load_electricity_vehicles.log"
    shell: "python scripts/prepare_vehicle_charging_demand.py {input.input_dir} {input.scalars} {output} {params.logfile}"

rule prepare_scalars:
    input:
        raw_scalars="raw/scalars/costs_efficiencies.csv",
    output: "results/_resources/scal_costs_efficiencies.csv"
    shell: "python scripts/prepare_scalars.py {input.raw_scalars} {output}"

rule prepare_cop_timeseries:
    input:
        scalars="raw/scalars/demands.csv",
        weather="raw/weatherdata"
    output:
        ts_efficiency_small="results/_resources/ts_efficiency_heatpump_small.csv",
    params:
        logfile="results/_resources/ts_efficiency_heatpump_small.log"
    shell: "python scripts/prepare_cop_timeseries.py {input.scalars} {input.weather} {output.ts_efficiency_small} {params.logfile}"

rule prepare_heat_demand:
    input:
        weather="raw/weatherdata",
        distribution_hh="raw/distribution_households.csv",
        holidays="raw/holidays.csv",
        building_class="raw/building_class.csv",
        scalars="raw/scalars/demands.csv",
    output:
        scalars="results/_resources/scal_load_heat.csv",
        timeseries="results/_resources/ts_load_heat.csv",
    params:
        logfile="results/_resources/load_heat.log"
    shell: "python scripts/prepare_heat_demand.py {input.weather} {input.distribution_hh} {input.holidays} {input.building_class} {input.scalars} {output.scalars} {output.timeseries} {params.logfile}"

rule prepare_re_potential:
    input:
        pv_agriculture="raw/area_potential/2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv",
        pv_road_railway="raw/area_potential/2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv",
        wind="raw/area_potential/2021-05-18_wind_brandenburg_kreise_epsg32633.csv",
        kreise="raw/lookup_table_brandenburg_kreise.csv",
        assumptions="raw/scalars/potentials.csv",
    output: directory("results/_resources/RE_potential/")
    shell: "python scripts/prepare_re_potential.py {input.pv_agriculture} {input.pv_road_railway} {input.wind} {input.kreise} {input.assumptions} {output}"

rule process_re_potential:
    input:
        input_dir="results/_resources/RE_potential/",
    output:
        scalars="results/_resources/scal_power_potential_wind_pv.csv",
        table="results/_tables/potential_wind_pv_kreise.csv",
    shell: "python scripts/process_re_potential.py {input.input_dir} {output.scalars} {output.table}"
