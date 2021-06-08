examples = [
    'simple_model',
    'simple_model_2',
    'simple_model_3'
]

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

rule optimize:
    input:
        "results/{scenario}/preprocessed"
    output:
        directory("results/{scenario}/optimized/")
    shell:
        "python scripts/optimize.py {input} {output}"

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
        shell("pandoc -V geometry:a4paper,margin=2.5cm --resource-path={output}/../plotted --metadata title='Results for scenario {wildcards.scenario}' {output}/report.md -o {output}/report.pdf")
        shell("pandoc --resource-path={output}/../plotted {output}/report.md --metadata title='Results for scenario {wildcards.scenario}' --self-contained -s --include-in-header=report/report.css -o {output}/report.html")
        os.remove(os.path.join(output[0], "report.md"))

rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """
