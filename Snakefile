from snakemake.remote.HTTP import RemoteProvider as HTTPRemoteProvider
HTTP = HTTPRemoteProvider()

examples = [
    'base',
    'more_renewables',
    'more_renewables_less_fossil'
]

scenario_list_example = ['examples']

resources = ['scal_conv_pp']

scenarios = ["toy-scenario", "toy-scenario-2"]

# Target rules
rule plot_grouped_scenarios:
    input:
        expand("results/joined_scenarios/{scenario_list}/joined_plotted/", scenario_list=scenario_list_example)

rule plot_all_scenarios:
    input:
        expand("results/{scenario}/plotted/", scenario=examples)

rule run_all_examples:
    input:
        expand("results/{scenario}/postprocessed", scenario=examples)

rule plot_all_examples:
    input:
        expand("results/{scenario}/plotted/", scenario=examples)

rule report_all_examples:
    input:
        expand("results/{scenario}/report/", scenario=examples)

rule plot_all_resources:
    input:
        expand("results/_resources/plots/{resource}.png", resource=resources)

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
        "results/_resources/scal_conv_pp.csv"
    shell:
        "python scripts/prepare_conv_pp.py {input.opsd} {input.gpkg} {input.b3_regions} {output}"

rule prepare_feedin:
    input:
        wind_feedin="raw/time_series/ninja_wind_country_DE_current_merra-2_nuts-2_corrected.csv",
        pv_feedin="raw/time_series/ninja_pv_country_DE_merra-2_nuts-2_corrected.csv",
        ror_feedin="raw/time_series/DIW_Hydro_availability.csv",
        script="scripts/prepare_feedin.py"
    output:
        "results/_resources/ts_feedin.csv"
    shell:
        "python {input.script} {input.wind_feedin} {input.pv_feedin} {input.ror_feedin} {output}"

rule prepare_electricity_demand:
    input:
        opsd_url=HTTP.remote("https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv",
                            keep_local=True),
        script="scripts/prepare_electricity_demand.py"
    output:
        "results/_resources/ts_load_electricity.csv"
    shell:
        "python {input.script} {input.opsd_url} {output}"

rule prepare_scalars:
    input:
        raw_scalars="raw/base-scenario.csv",
        script="scripts/prepare_scalars.py",
    output:
        "results/_resources/scal_base-scenario.csv"
    shell:
        "python {input.script} {input.raw_scalars} {output}"

rule prepare_re_potential:
    input:
        pv_agriculture="raw/area_potential/2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv",
        pv_road_railway="raw/area_potential/2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv",
        wind="raw/area_potential/2021-05-18_wind_brandenburg_kreise_epsg32633.csv",
        kreise="raw/lookup_table_brandenburg_kreise.csv",
        assumptions="raw/scalars.csv",
        script="scripts/prepare_re_potential.py"
    output:
        directory("results/_resources/RE_potential/")
    shell:
        "python {input.script} {input.pv_agriculture} {input.pv_road_railway} {input.wind} {input.kreise} {input.assumptions} {output}"

rule process_re_potential:
    input:
        input_dir=directory("results/_resources/RE_potential/"),
        script="scripts/process_re_potential.py"
    output:
        scalars="results/_resources/scal_power_potential_wind_pv.csv",
        table="results/_tables/potential_wind_pv_kreise.csv",
    shell:
        "python {input.script} {input.input_dir} {output.scalars} {output.table}"

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

rule plot_conv_pp_scalars:
    input:
        data="results/_resources/{resource}.csv",
        script="scripts/plot_conv_pp_scalars.py"
    output:
        "results/_resources/plots/{resource}_var_{var_name}.png"
    shell:
        "python {input.script} {input.data} {wildcards.var_name} {output}"

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
        "results/joined_scenarios/{scenario_list}/joined/scalars.csv"
    shell:
        "python scripts/join_scenarios.py {input} {output}"

rule plot_joined_scalars:
    input:
        "results/joined_scenarios/{scenario_list}/joined/scalars.csv"
    output:
        directory("results/joined_scenarios/{scenario_list}/joined_plotted/")
    shell:
        "python scripts/plot_joined_scalars.py {input} {output}"
