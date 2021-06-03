rule build_datapackage:
    input:
        "scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed")
    shell:
        "python scripts/build_datapackage.py {input} {output}"

rule prepare_example:
    input:
        "examples/{scenario}/preprocessed/{scenario}"
    output:
        directory("results/{scenario}/preprocessed")
    wildcard_constraints:
        # necessary to distinguish from those scenarios that are not pre-fabricated
        scenario="simple_model*"
    shell:
        "cp -r {input} {output}"

rule prepare_conv_pp:
    input:
        opsd="raw/conventional_power_plants_DE.csv",
        gpkg="raw/boundaries_germany_nuts3.gpkg",
        b3_regions="raw/b3_regions.yaml",
        script="scripts/prepare_conv_pp.py"
    output:
        "results/_resources/conv_pp.csv"
    shell:
        "python scripts/prepare_conv_pp.py {input.opsd} {input.gpkg} {input.b3_regions} {output}"

rule prepare_pv_potential:
    input:
        type="pv",
        filenames=["raw/area_potential/2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv",
                   "raw/area_potential/2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv"],
        assumptions="xxxx.csv", # todo
        script="scripts/prepare_re_potential.py"
    output:
        "results/_resources/power_potential_pv_kreise.csv"
    shell:
        "python scripts/prepare_re_potential.py  {input.type} {input.filenames} {input.assumptions} {output}"

rule prepare_wind_potential:
    input:
        type="wind",
        filenames=["raw/area_potential/2021-05-18_wind_brandenburg_kreise_epsg32633.csv"],
        assumptions="xxxx.csv", # todo
        script="scripts/prepare_re_potential.py"
    output:
        "results/_resources/power_potential_wind_kreise.csv"
    shell:
        "python scripts/prepare_re_potential.py  {input.type} {input.filenames} {input.assumptions} {output}"

rule optimize:
    input:
        "results/{scenario}/preprocessed"
    output:
        directory("results/{scenario}/optimized/")
    shell:
        "python scripts/optimize.py {input} {output}"

rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """
