"""
This script checks the snakemake pipeline for target rules creating the scenario results.
"""
import os
from oemof_b3.tools.testing_pipeline import (
    get_repo_path,
    pipeline_folder_output_test,
)

# Delete data from test run of pipeline if True otherwise False
delete_switch = True


# Get current path
current_path = os.path.abspath(os.getcwd())
target_path = get_repo_path(current_path)

# Set the current path to the target path
os.chdir(target_path)


scenarios = [
    "2050-100-el_eff",
    "2050-95-el_eff",
    "2050-80-el_eff",
    "2050-100-gas_moreCH4",
    "2050-95-gas_moreCH4",
    "2050-80-gas_moreCH4",
]

scenario_groups = [
    "examples",
    "all-scenarios",
    "all-custom-order",
    "all-optimized",
]


def output_rule_set(scenario):
    output_rule_list = [
        "results/" + scenario + "/preprocessed",
        "results/" + scenario + "/optimized",
        "results/" + scenario + "/postprocessed",
        "results/" + scenario + "/b3_results/data",
        "results/" + scenario + "/tables",
        "results/" + scenario + "/plotted/dispatch",
        "results/" + scenario + "/plotted/storage_level",
        "results/" + scenario + "/plotted/scalars",
        # "results/" + scenario + "/report",
    ]

    return output_rule_list


for scenario_group in scenario_groups:
    output_rule_list = [
        "results/joined_scenarios/" + scenario_group + "/joined",
        "results/joined_scenarios/" + scenario_group + "/joined_tables",
        "results/joined_scenarios/" + scenario_group + "/joined_plotted",
    ]

# snakemake -j1 prepare_re_potential
output_rule_list = ["results/_resources/RE_potential"]

scenario_output_rule_list = [output_rule_set(scenario) for scenario in scenarios]


def test_pipeline_results():
    pipeline_folder_output_test(delete_switch, scenario_output_rule_list)
