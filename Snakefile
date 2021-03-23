rule setup_model_structure:
    input:
        "scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed/data")
    shell:
        "python scripts/setup_model_structure.py scenarios/{wildcards.scenario}.yml results/{wildcards.scenario}/preprocessed/data"


rule infer:
    input:
        "scenarios/{scenario}.yml"
    output:
        "results/{scenario}/preprocessed/datapackage.json"
    shell:
        "python scripts/infer.py scenarios/{wildcards.scenario}.yml results/{wildcards.scenario}/preprocessed"


rule prepare_example:
    input:
        directory("examples/{scenario}")
    output:
        directory("results/{scenario}/preprocessed")
    shell:
        "cp -r examples/{wildcards.scenario}/preprocessed results/{wildcards.scenario}/preprocessed"

rule prepare_conv_pp:
    input:
        opsd="raw/conventional_power_plants_DE.csv",
	    gpkg="raw/boundaries_germany_nuts3.gpkg",
	    script="scripts/prepare_conv_pp.py"
    output:
        "results/prepared_conv_pp.csv"
    shell:
        "python scripts/prepare_conv_pp.py {input.opsd} {input.gpkg} {output}"
		
rule optimize:
    input:
        directory("results/{scenario}/preprocessed/")
    output:
        directory("results/{scenario}/optimized/")
    shell:
        "python scripts/optimize.py results/{wildcards.scenario}/preprocessed results/{wildcards.scenario}/optimized"


rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """
