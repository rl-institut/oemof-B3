rule setup_model_structure:
    input:
        "scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed/data")
    shell:
        "python scripts/setup_model_structure.py {input} {output}"


rule infer:
    input:
        "scenarios/{scenario}.yml"
    output:
        # Actually, the target is datapackage.json, but setting the general directory
        # as output allows optimization to pick up the outputs of this rule.
        directory("results/{scenario}/preprocessed")
    shell:
        "python scripts/infer.py {input} {output}"


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
