examples = [
    'simple_model',
    'simple_model_2',
    'simple_model_3'
]

rule run_all_examples:
    input:
        expand("results/{scenario}/postprocessed", scenario=examples)

rule prepare_example:
    input:
        "examples/{scenario}/preprocessed/{scenario}"
    output:
        directory("results/{scenario}/preprocessed")
    wildcard_constraints:
        # necessary to distinguish from those scenarios that are not pre-fabricated
        scenario="|".join(examples)
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

rule build_datapackage:
    input:
        "scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed")
    shell:
        "python scripts/build_datapackage.py {input} {output}"

rule optimize:
    input:
        "results/{scenario}/preprocessed"
    output:
        directory("results/{scenario}/optimized/")
    shell:
        "python scripts/optimize.py {input} {output}"

rule postprocess:
    input:
        "results/{scenario}/optimized"
    output:
        directory("results/{scenario}/postprocessed/")
    shell:
        "python scripts/postprocess.py {input} {wildcards.scenario} {output}"

rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """
