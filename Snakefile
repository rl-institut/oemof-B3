examples = [
    'base',
    'more_renewables',
    'more_renewables_less_fossil'
]

# Target rules

rule run_all_examples:
    input:
        expand("results/{scenario}/postprocessed", scenario=examples)

rule plot_all_examples:
    input:
        expand("results/{scenario}/plotted/", scenario=examples)

rule report_all_examples:
    input:
        expand("results/{scenario}/report/", scenario=examples)

rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """

# Rules for intermediate steps

rule prepare_example:
    input:
        "examples/{scenario}/preprocessed/{scenario}"
    output:
        directory("results/{scenario}/preprocessed")
    wildcard_constraints:
        # necessary to distinguish from those scenarios that are not pre-fabricated
        scenario="|".join(examples)
    run:
        import shutil
        shutil.copytree(src=input[0], dst=output[0])

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

rule plot_dispatch:
    input:
        "results/{scenario}/postprocessed/"
    output:
        directory("results/{scenario}/plotted/")
    shell:
        "python scripts/plot_dispatch.py {input} {output}"

rule report:
    input:
        template="report/report.md",
        plots="results/{scenario}/plotted"
    output:
        directory("results/{scenario}/report/")
    run:
        import os
        import shutil
        os.makedirs(output[0])
        shutil.copy(src=input[0], dst=output[0])
        shell('pandoc -V geometry:a4paper,margin=2.5cm --resource-path={output}/../plotted --metadata title="Results for scenario {wildcards.scenario}" {output}/report.md -o {output}/report.pdf')
        shell('pandoc --resource-path={output}/../plotted {output}/report.md --metadata title="Results for scenario {wildcards.scenario}" --self-contained -s --include-in-header=report/report.css -o {output}/report.html')
        os.remove(os.path.join(output[0], "report.md"))

rule join_scenario_results:
    input:
        "scenario_groups/{scenario_list}.yml"
    output:
        "results/joined_scenarios/{scenario_list}/scalars.csv"
    shell:
        "python scripts/join_scenarios.py {input} {output}"

