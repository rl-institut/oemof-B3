examples = [
    'simple_model',
    'simple_model_2',
    'simple_model_3'
]

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


rule scenario_report_old:
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

rule report_all_examples:
    input:
        expand("results/{scenario}/report/", scenario=examples)

rule report:
    input:
        "report/report.md"
    params:
        # TODO: Make this an input once the plot rule is defined
        "results/{scenario}/plotted"
    output:
        directory("results/{scenario}/report/")
    run:
        import os
        import shutil
        os.makedirs(output[0])
        shutil.copy(src=input[0], dst=output[0])
        shell("pandoc -V geometry:a4paper,margin=2.5cm --resource-path={output}/../plotted {output}/report.md -o {output}/report.pdf")
        os.remove(os.path.join(output[0], "report.md"))

rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """
