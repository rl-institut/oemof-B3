"""
This script checks the snakemake pipeline for target rules creating the scenario results.
"""
import os
from oemof_b3.tools.testing_pipeline import (
    get_repo_path,
    pipeline_output_test,
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


def make_scenario_outputs(scenario):
    _scenario_output_rule_list = [
        "results/" + scenario + "/preprocessed",
        "results/" + scenario + "/optimized",
        "results/" + scenario + "/postprocessed",
        "results/" + scenario + "/b3_results/data",
        "results/" + scenario + "/tables",
        "results/" + scenario + "/plotted/dispatch",
        "results/" + scenario + "/plotted/storage_level",
        "results/" + scenario + "/plotted/scalars",
        "results/" + scenario + "/plotted/es_graph",
        # "results/" + scenario + "/report",
    ]

    return _scenario_output_rule_list


def make_joined_outputs(_group):
    _joined_output_rule_list = [
        "results/joined_scenarios/" + _group + "/joined",
        "results/joined_scenarios/" + _group + "/joined_tables",
        "results/joined_scenarios/" + _group + "/joined_plotted",
    ]

    return _joined_output_rule_list


# 1. Per-scenario results
scenario_output_rule_list = [make_scenario_outputs(scenario) for scenario in scenarios]

# 2. Joined-scenario results
joined_output_rule_list = [make_joined_outputs(group) for group in scenario_groups]

# 3. Special single outputs (snakemake -j1 prepare_re_potential)
special_output_rule_list = ["results/_resources/RE_potential"]

# Combine all lists into one big list of lists
output_rule_list = (
    scenario_output_rule_list + joined_output_rule_list + special_output_rule_list
)


def test_pipeline_results():
    pipeline_output_test(delete_switch, scenario_output_rule_list)
