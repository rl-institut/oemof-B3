examples = [
    'base',
    'more_renewables',
    'more_renewables_less_fossil'
]

scenarios = ["toy-scenario", "toy-scenario-2"]

# Target rules

rule plot_all_scenarios:
    input:
        expand("results/{scenario}/plotted/", scenario=scenarios)

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
        scalar_template="oemof_b3/schema/scalars.csv",
        script="scripts/prepare_conv_pp.py"
    output:
        "results/_resources/conv_pp_scalar.csv"
    shell:
        "python scripts/prepare_conv_pp.py {input.opsd} {input.gpkg} {input.b3_regions} {input.scalar_template} {output}"

rule prepare_feedin:
    input:
        wind_feedin="raw/time_series/ninja_wind_country_DE_current_merra-2_nuts-2_corrected.csv",
        pv_feedin="raw/time_series/ninja_pv_country_DE_merra-2_nuts-2_corrected.csv",
        time_series_template="oemof_b3/schema/timeseries.csv",
        script="scripts/prepare_feedin.py"
    output:
        "results/_resources/feedin_time_series.csv"
    shell:
        "python {input.script} {input.wind_feedin} {input.pv_feedin} {input.time_series_template} {output}"

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
	template_interactive="report/report_interactive.md",
        plots="results/{scenario}/plotted"
    output:
        directory("results/{scenario}/report/")
    run:
        import os
        import shutil
        os.makedirs(output[0])
        shutil.copy(src=input[0], dst=output[0])
        shutil.copy(src=input[1], dst=output[0])
        # static pdf report
        shell(
        """
        pandoc -V geometry:a4paper,margin=2.5cm \
        --resource-path={output}/../plotted \
        --metadata title="Results for scenario {wildcards.scenario}" \
        {output}/report.md -o {output}/report.pdf
        """
        )
        # static html report
        shell(
        """
        pandoc --resource-path={output}/../plotted \
        --metadata title="Results for scenario {wildcards.scenario}" \
        --self-contained -s --include-in-header=report/report.css \
        {output}/report.md -o {output}/report.html
        """
        )
        # interactive html report
        shell(
        """
        pandoc --resource-path={output}/../plotted \
        --metadata title="Results for scenario {wildcards.scenario}" \
        --self-contained -s --include-in-header=report/report.css \
        {output}/report_interactive.md -o {output}/report_interactive.html
        """
        )
        os.remove(os.path.join(output[0], "report.md"))
        os.remove(os.path.join(output[0], "report_interactive.md"))

rule join_scenario_results:
    input:
        "scenario_groups/{scenario_list}.yml"
    output:
        "results/joined_scenarios/{scenario_list}/postprocessed/scalars.csv"
    shell:
        "python scripts/join_scenarios.py {input} {output}"

