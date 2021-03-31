rule setup_model_structure:
    input:
        "scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed")
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
        "examples/{example}"
    output:
        directory("results/{example}/preprocessed")
    wildcard_constraints:
        example="((simple_model)|(simple_model_2)|(simple_model_3))"
    shell:
        "cp -r examples/{wildcards.example}/preprocessed results/{wildcards.example}/preprocessed"


rule optimize:
    input:
        "results/{scenario}/preprocessed/{scenario}"
    output:
        directory("results/{scenario}/optimized/")
    shell:
        "python scripts/optimize.py {input} results/{wildcards.scenario}/optimized"


rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """
