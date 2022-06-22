from snakemake.remote.HTTP import RemoteProvider as HTTPRemoteProvider
from oemoflex.tools.helpers import load_yaml

HTTP = HTTPRemoteProvider()


scenario_groups = {
    "examples": ["example_base", "example_more_re", "example_more_re_less_fossil"],
    "all-scenarios": [os.path.splitext(scenario)[0] for scenario in os.listdir("scenarios")],
    "all-optimized": [
        scenario for scenario in os.listdir("results")
        if (
                os.path.exists(os.path.join("results", scenario, "optimized", "es_dump.oemof"))
                and not "example_" in scenario
        )
    ]
}

resource_plots = ['scal_conv_pp-capacity_net_el']


# Target rules
rule plot_all_resources:
    input:
        expand("results/_resources/plots/{resource_plot}.png", resource_plot=resource_plots)

rule plot_all_examples:
    input:
        expand(
            "results/{scenario}/plotted/{plot_type}",
            scenario=scenario_groups["examples"],
            plot_type=["scalars", "dispatch"],
        )

ALL_SCENARIOS = scenario_groups["all-scenarios"]
PLOT_TYPE = ["scalars", "dispatch"]
rule process_all_scenarios:
    input:
        plots=expand(
            "results/{scenario}/plotted/{plot_type}",
            scenario=ALL_SCENARIOS,
            plot_type=PLOT_TYPE,
        ),
        tables=expand(
            "results/{scenario}/tables",
            scenario=ALL_SCENARIOS,
        )

rule plot_grouped_scenarios:
    input:
        expand("results/joined_scenarios/{scenario_group}/joined_plotted/", scenario_group="all-scenarios")


rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """

# Rules for intermediate steps

rule create_input_data_overview:
    input:
        "raw/scalars/costs_efficiencies.csv"
    output:
        "results/_tables/technical_and_cost_assumptions_{scenario_key}.csv"
    params:
        logfile="logs/{scenario_key}.log"
    shell:
        "python scripts/create_input_data_overview.py {input} {wildcards.scenario_key} {output} {params.logfile}"

rule prepare_example:
    input:
        "examples/{scenario}/preprocessed/"
    output:
        directory("results/{scenario}/preprocessed")
    wildcard_constraints:
        # necessary to distinguish from those scenarios that are not pre-fabricated
        scenario="|".join(scenario_groups["examples"])
    run:
        import shutil
        shutil.copytree(src=input[0], dst=output[0])

rule prepare_conv_pp:
    input:
        opsd="raw/conventional_power_plants_DE.csv",
        gpkg="raw/boundaries_germany_nuts3.gpkg",
        b3_regions="raw/b3_regions.yaml",
    output:
        "results/_resources/scal_conv_pp.csv"
    shell:
        "python scripts/prepare_conv_pp.py {input.opsd} {input.gpkg} {input.b3_regions} {output}"

rule prepare_feedin:
    input:
        wind_feedin="raw/time_series/ninja_wind_country_DE_current_merra-2_nuts-2_corrected.csv",
        pv_feedin="raw/time_series/ninja_pv_country_DE_merra-2_nuts-2_corrected.csv",
        ror_feedin="raw/time_series/DIW_Hydro_availability.csv",
    output:
        "results/_resources/ts_feedin.csv"
    shell:
        "python scripts/prepare_feedin.py {input.wind_feedin} {input.pv_feedin} {input.ror_feedin} {output}"

rule prepare_electricity_demand:
    input:
        opsd_url=HTTP.remote("https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv",
                            keep_local=True),
    output:
        "results/_resources/ts_load_electricity.csv"
    shell:
        "python scripts/prepare_electricity_demand.py {input.opsd_url} {output}"

rule prepare_vehicle_charging_demand:
    input:
        input_dir="raw/time_series/vehicle_charging",
        scalars="raw/scalars/demands.csv",
    output:
        "results/_resources/ts_load_electricity_vehicles.csv"
    params:
        logfile="logs/prepare_vehicle_charging_demand.log"
    shell:
        "python scripts/prepare_vehicle_charging_demand.py {input.input_dir} {input.scalars} {output} {params.logfile}"

rule prepare_scalars:
    input:
        raw_scalars="raw/scalars/costs_efficiencies.csv",
    output:
        "results/_resources/scal_costs_efficiencies.csv"
    shell:
        "python scripts/prepare_scalars.py {input.raw_scalars} {output}"

rule prepare_cop_timeseries:
    input:
        scalars="raw/scalars/demands.csv",
        weather="raw/weatherdata"
    output:
        ts_efficiency_small="results/_resources/ts_efficiency_heatpump_small.csv",
    params:
        logfile="logs/prepare_cop_timeseries.log"
    shell:
         "python scripts/prepare_cop_timeseries.py {input.scalars} {input.weather} {output.ts_efficiency_small} {params.logfile}"

rule prepare_heat_demand:
    input:
        weather="raw/weatherdata",
        distribution_hh="raw/distribution_households.csv",
        holidays="raw/holidays.csv",
        building_class="raw/building_class.csv",
        scalars="raw/scalars/demands.csv",
    output:
        scalars="results/_resources/scal_load_heat.csv",
        timeseries="results/_resources/ts_load_heat.csv",
    params:
        logfile="logs/prepare_heat_demand.log"
    shell:
        "python scripts/prepare_heat_demand.py {input.weather} {input.distribution_hh} {input.holidays} {input.building_class} {input.scalars} {output.scalars} {output.timeseries} {params.logfile}"

rule prepare_re_potential:
    input:
        pv_agriculture="raw/area_potential/2021-05-18_pv_agriculture_brandenburg_kreise_epsg32633.csv",
        pv_road_railway="raw/area_potential/2021-05-18_pv_road_railway_brandenburg_kreise_epsg32633.csv",
        wind="raw/area_potential/2021-05-18_wind_brandenburg_kreise_epsg32633.csv",
        kreise="raw/lookup_table_brandenburg_kreise.csv",
        assumptions="raw/scalars/potentials.csv",
    output:
        directory("results/_resources/RE_potential/")
    shell:
        "python scripts/prepare_re_potential.py {input.pv_agriculture} {input.pv_road_railway} {input.wind} {input.kreise} {input.assumptions} {output}"

rule process_re_potential:
    input:
        input_dir="results/_resources/RE_potential/",
    output:
        scalars="results/_resources/scal_power_potential_wind_pv.csv",
        table="results/_tables/potential_wind_pv_kreise.csv",
    shell:
        "python scripts/process_re_potential.py {input.input_dir} {output.scalars} {output.table}"

def get_paths_scenario_input(wildcards):
    scenario_specs = load_yaml(f"scenarios/{wildcards.scenario}.yml")
    paths_scenario_inputs = list()
    for key in ["paths_scalars", "paths_timeseries"]:
        paths = scenario_specs[key]
        if isinstance(paths, list):
            paths_scenario_inputs.extend(paths)
        elif isinstance(paths, str):
            paths_scenario_inputs.append(paths)
    return paths_scenario_inputs

rule build_datapackage:
    input:
        get_paths_scenario_input,
        scenario="scenarios/{scenario}.yml"
    output:
        directory("results/{scenario}/preprocessed")
    params:
        logfile="logs/{scenario}.log"
    shell:
        "python scripts/build_datapackage.py {input.scenario} {output} {params.logfile}"

# rule optimize:
#     input:
#         "results/{scenario}/preprocessed"
#     output:
#         directory("results/{scenario}/optimized/")
#     params:
#         logfile="logs/{scenario}.log"
#     shell:
#         "python scripts/optimize.py {input} {output} {params.logfile}"

rule postprocess:
    input:
        "results/{scenario}/optimized"
    output:
        directory("results/{scenario}/postprocessed/")
    params:
        logfile="logs/{scenario}.log"
    shell:
        "python scripts/postprocess.py {input} {wildcards.scenario} {output} {params.logfile}"

rule create_results_table:
    input:
        "results/{scenario}/postprocessed/"
    output:
        directory("results/{scenario}/tables/")
    params:
        logfile="logs/{scenario}.log"
    shell:
        "python scripts/create_results_table.py {input} {output} {params.logfile}"

rule create_joined_results_table:
    input:
        "results/joined_scenarios/{scenario_group}/joined/"
    output:
        directory("results/joined_scenarios/{scenario_group}/joined_tables/")
    params:
        logfile="logs/{scenario_group}.log"
    shell:
        "python scripts/create_results_table.py {input} {output} {params.logfile}"

rule plot_dispatch:
    input:
        "results/{scenario}/postprocessed/"
    output:
        directory("results/{scenario}/plotted/dispatch")
    params:
        logfile="logs/{scenario}.log"
    shell:
        "python scripts/plot_dispatch.py {input} {output} {params.logfile}"

rule plot_conv_pp_scalars:
    input:
        data="results/_resources/{resource}.csv",
    output:
        "results/_resources/plots/{resource}-{var_name}.png"
    shell:
        "python scripts/plot_conv_pp_scalars.py {input.data} {wildcards.var_name} {output}"

rule plot_scalar_results:
    input:
        "results/{scenario}/postprocessed/"
    output:
        directory("results/{scenario}/plotted/scalars/")
    params:
        logfile="logs/{scenario}.log"
    shell:
        "python scripts/plot_scalar_results.py {input} {output} {params.logfile}"

rule plot_joined_scalars:
    input:
        "results/joined_scenarios/{scenario_group}/joined/"
    output:
        directory("results/joined_scenarios/{scenario_group}/joined_plotted/")
    params:
        logfile="logs/{scenario_group}.log"
    shell:
        "python scripts/plot_scalar_results.py {input} {output} {params.logfile}"

rule report:
    input:
        template="report/report.md",
        template_interactive="report/report_interactive.md",
        plots_scalars="results/{scenario}/plotted/scalars",
        plots_dispatch="results/{scenario}/plotted/dispatch",
    output:
        directory("results/{scenario}/report/")
    params:
        logfile="logs/{scenario}.log",
        all_plots="results/{scenario}/plotted/",
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
        --lua-filter report/pandoc_filter.lua \
        --resource-path={params.all_plots} \
        --metadata title="Results for scenario {wildcards.scenario}" \
        {output}/report.md -o {output}/report.pdf
        """
        )
        # static html report
        shell(
        """
        pandoc --resource-path={params.all_plots} \
        --lua-filter report/pandoc_filter.lua \
        --metadata title="Results for scenario {wildcards.scenario}" \
        --self-contained -s --include-in-header=report/report.css \
        {output}/report.md -o {output}/report.html
        """
        )
        # interactive html report
        shell(
        """
        pandoc --resource-path={params.all_plots} \
        --lua-filter report/pandoc_filter.lua \
        --metadata title="Results for scenario {wildcards.scenario}" \
        --self-contained -s --include-in-header=report/report.css \
        {output}/report_interactive.md -o {output}/report_interactive.html
        """
        )
        os.remove(os.path.join(output[0], "report.md"))
        os.remove(os.path.join(output[0], "report_interactive.md"))


def get_scenarios_in_group(wildcards):
    return [os.path.join("results", scenario, "postprocessed") for scenario in scenario_groups[wildcards.scenario_group]]


# rule join_scenario_results:
#     input:
#         get_scenarios_in_group
#     output:
#         directory("results/joined_scenarios/{scenario_group}/joined/")
#     shell:
#         "python scripts/join_scenarios.py {input} {output}"
