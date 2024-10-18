"""
This script checks the snakemake pipeline for target rules in directory '_resources'
and '_tables' located in the directory 'results'.
"""
import os
from oemof_b3.tools.testing_pipeline import (
    get_repo_path,
    install_with_extra,
    pipeline_file_output_test,
)

# Delete data from test run of pipeline if True otherwise False
delete_switch = True


# Install poetry -E preprocessing
extra_env = "preprocessing"
install_with_extra(extra_env)

# Get current path
current_path = os.path.abspath(os.getcwd())
target_path = get_repo_path(current_path)

# Set the current path to the target path
os.chdir(target_path)

output_rule_list = [
    ["results/_resources/scal_conv_pp.csv"],
    ["results/_resources/ts_feedin.csv"],
    ["results/_resources/ts_load_electricity.csv"],
    ["results/_resources/ts_load_electricity_vehicles.csv"],
    ["results/_resources/scal_costs_efficiencies.csv"],
    ["results/_resources/ts_efficiency_heatpump_small.csv"],
    # snakemake -j1 plot_conv_pp_scalars
    ["results/_resources/plots/scal_conv_pp-capacity_net_el.png"],
    ["results/_tables/technical_and_cost_assumptions_2050-base.csv"],
    ["results/_resources/scal_load_heat.csv", "results/_resources/ts_load_heat.csv"],
    # snakemake -j1 process_re_potential
    [
        "results/_resources/scal_power_potential_wind_pv.csv",
        "results/_tables/potential_wind_pv_kreise.csv",
    ],
    # snakemake -j1 download_resources
    [
        "results/_resources/ts_feedin.csv",
        "results/_resources/ts_load_electricity.csv",
        "results/_resources/ts_load_electricity_vehicles.csv",
        "results/_resources/scal_costs_efficiencies.csv",
        "results/_resources/ts_efficiency_heatpump_small.csv",
        "results/_resources/scal_load_heat.csv",
        "results/_resources/ts_load_heat.csv",
    ],
]


def test_pipeline_resources_tables():
    pipeline_file_output_test(delete_switch, output_rule_list)
