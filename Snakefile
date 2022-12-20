import os

from snakemake.remote.HTTP import RemoteProvider as HTTPRemoteProvider
import oemof_b3.config.config as config

HTTP = HTTPRemoteProvider()

# The following lines define groups of scenarios/examples
# To get a desired order in the plots, define a list of scenarios here.
scenario_groups = {
    "examples": [
        "example_base",
        "example_more_re",
        "example_more_re_less_fossil"
    ],
    "all-scenarios": [
        os.path.splitext(scenario)[0] for scenario in os.listdir("scenarios")
    ],
    "all-custom-order": [
        "2050-80-el_eff",
        "2050-95-el_eff",
        "2050-100-el_eff",
        "2050-80-gas_moreCH4",
        "2050-95-gas_moreCH4",
        "2050-100-gas_moreCH4",
    ],
    "all-optimized": [
        scenario for scenario in os.listdir("results")
        if (
            os.path.exists(os.path.join("results", scenario, "optimized", "es_dump.oemof"))
            and not "example_" in scenario
        )
    ]
}

plot_type = ["scalars", "dispatch"]

resource_plots = ['scal_conv_pp-capacity_net_el']


# Target rules
rule plot_all_resources:
    input:
        expand(
        "results/_resources/plots/{resource_plot}.png",
        resource_plot=resource_plots
    )

rule run_all_examples:
    input:
        expand(
            "results/{scenario}/plotted/{plot_type}",
            scenario=scenario_groups["examples"],
            plot_type=plot_type,
        )

rule run_all_scenarios:
    input:
        plots=expand(
            "results/{scenario}/plotted/{plot_type}",
            scenario=scenario_groups["all-scenarios"],
            plot_type=plot_type,
        ),
        tables=expand(
            "results/{scenario}/tables",
            scenario=scenario_groups["all-scenarios"],
        )

rule plot_grouped_scenarios:
    input:
        expand(
        "results/joined_scenarios/{scenario_group}/joined_plotted/",
        scenario_group="all-scenarios"
    )

rule clean:
    shell:
        """
        rm -r ./results/*
        echo "Removed all results."
        """

# Include rules for intermediate steps
include: "snakemake_rules/build_datapackage.smk"
include: "snakemake_rules/optimization.smk"
include: "snakemake_rules/postprocessing.smk"
include: "snakemake_rules/visualization.smk"
include: "snakemake_rules/oep_upload.smk"

# prepare settings locally or download it from OEP (not implemented yet)
if config.settings.general.prepare_resources_locally:
    include: "snakemake_rules/prepare_resource.smk"
else:
    include: "snakemake_rules/oep_download.smk"
