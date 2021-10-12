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

rule build_datapackage:
    input:
        "scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed")
    shell:
        "python scripts/build_datapackage.py {input} {output}"

rule prepare_pv_potential:
    input:
        filename_agriculture="raw/area_potential/2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv",
        filename_road_railway="raw/area_potential/2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv",
        filename_kreise="raw/lookup_table_brandenburg_kreise.csv",
        filename_assumptions="raw/scalars.csv",
        script="scripts/prepare_re_potential.py"
    output:
        filename_kreise="results/_resources/power_potential_pv_kreise.csv",
        secondary_output_dir=directory("results/_resources/RE_potential/")
    shell:
        "python {input.script} {input.filename_agriculture} {input.filename_road_railway} {input.filename_kreise} {input.filename_assumptions} {output.filename_kreise} {output.secondary_output_dir}"

rule prepare_wind_potential:
    input:
        filename_wind="raw/area_potential/2021-05-18_wind_brandenburg_kreise_epsg32633.csv",
        filename_kreise="raw/lookup_table_brandenburg_kreise.csv",
        filename_assumptions="raw/scalars.csv",
        script="scripts/prepare_re_potential.py"
    output:
        filename_kreise="results/_resources/power_potential_wind_kreise.csv",
        secondary_output_dir=directory("results/_resources/RE_potential/")
    shell:
        "python scripts/prepare_re_potential.py  {input.filename_wind} {input.filename_kreise} {input.filename_assumptions} {output.filename_kreise} {output.secondary_output_dir}"

rule process_re_potential:
    input:
        filename_wind="results/_resources/power_potential_wind_kreise.csv",
        filename_pv="results/_resources/power_potential_pv_kreise.csv",
        scalar_template="oemof_b3/schema/scalars.csv",
        script="scripts/process_re_potential.py"
    output:
        filename_scalars="results/_resources/wind_pv_scalar.csv",
        filename_table="results/_tables/potential_wind_pv_kreise.csv",
    shell:
        "python scripts/process_re_potential.py  {input.filename_wind} {input.filename_pv} {input.scalar_template} {output.filename_scalars} {output.filename_table}"

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

