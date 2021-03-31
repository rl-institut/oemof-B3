rule setup_model_structure:
    input:
        "scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed/{scenario}/data")
    shell:
        "python scripts/setup_model_structure.py {input} {output}"


rule infer:
    input:
        "scenarios/{scenario}.yml"
    output:
        "results/{scenario}/preprocessed/{scenario}/datapackage.json"
    shell:
        "python scripts/infer.py {input} {output}"


rule prepare_example:
    input:
        "examples/{example}/preprocessed"
    output:
        directory("results/{example}/preprocessed")
    wildcard_constraints:
        example="((simple_model)|(simple_model_2)|(simple_model_3))"
    shell:
        "cp -r {input} {output}"


rule optimize:
    input:
        "results/{scenario}/preprocessed/{scenario}"
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
