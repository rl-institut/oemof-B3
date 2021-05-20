rule setup_model_structure:
    input:
        "scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed/data")
    shell:
        "python scripts/setup_model_structure.py scenarios/{wildcards.scenario}.yml results/{wildcards.scenario}/preprocessed"


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


rule optimize:
    input:
        directory("results/{scenario}/preprocessed/")
    output:
        directory("results/{scenario}/optimized/")
    shell:
        "python scripts/optimize.py results/{wildcards.scenario}/preprocessed results/{wildcards.scenario}/optimized"


rule scenario_report:
    input:
        "report/report.md"
        #rules.scenario_plot.outputs
    output:
         "report.{suffix}"
    wildcard_constraints:
        suffix = "{(html)|(pdf)}"
    shell:
        """
        pandoc -t report.md -o results/scenario_reports/{wildcards.scenario}
        """

rule report:
    input:
        "report/report.md"
    output:
        "report.pdf"
    shell:
        """
        cd report
        pandoc report.md -o report.pdf
        """

rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """
