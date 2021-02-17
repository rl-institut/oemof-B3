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
        "results/{scenario}/preprocessed/datapackage.json"
    shell:
        "python scripts/infer.py {input} {output}"


rule prepare_example:
    input:
        directory("examples/{scenario}/preprocessed")
    output:
        directory("results/{scenario}/preprocessed")
    shell:
        "cp -r {input} {output}"


rule optimize:
    input:
        directory("results/{scenario}/preprocessed/")
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
