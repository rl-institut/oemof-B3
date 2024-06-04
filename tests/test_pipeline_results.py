"""

"""
import os
from oemof_b3.tools.testing_pipeline import (
    get_repo_path,
    get_abs_path_list,
    rename_path,
    file_name_extension,
    clean_file,
    rule_test,
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
        [
            "results/" + scenario + "/preprocessed",
            "results/" + scenario + "/optimized",
            "results/" + scenario + "/postprocessed",
            "results/" + scenario + "/b3_results/data",
            "results/" + scenario + "/tables",
            "results/" + scenario + "/plotted/dispatch",
            "results/" + scenario + "/plotted/storage_level",
            "results/" + scenario + "/plotted/scalars",
        ]
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


def test_pipeline_folders(delete_switch, scenarios):
    # Get output rule set from scenario
    for scenario in scenarios:
        output_rule_list = output_rule_set(scenario)

        for sublist in output_rule_list:
            absolute_path_list = get_abs_path_list(sublist)

        renamed_file_path = []
        for raw_dir_path in absolute_path_list:
            try:
                # Check if file already exists in directory
                if os.path.isfile(raw_dir_path):
                    # Rename file with extension original
                    renamed_file = file_name_extension(raw_dir_path)
                    renamed_path.append(renamed_file)
                # Check if file already exists in directory
                if os.path.isdir(raw_dir_path):
                    # Rename file with extension original
                    renamed_file = rename_path(raw_dir_path, "", "")
                    renamed_file_path.append(renamed_file)
                else:
                    # Check for the file with the _original suffix
                    dir_file = raw_dir_path + "_original"

                    if os.path.exists(dir_file):
                        raise FileExistsError(
                            f"File {dir_file} already exists."
                            f"Please rename the file {raw_dir_path} first."
                        )

            except FileNotFoundError as e:
                print(e)
                continue

        try:
            # Run the snakemake rule
            rule_test(sublist)

            # Check if the output file was created
            for raw_dir_path in absolute_path_list:
                assert os.path.exists(raw_dir_path)

            # Revert file changes
            clean_file(sublist, delete_switch, renamed_file_path)

        except BaseException:
            # Revert file changes
            clean_file(sublist, delete_switch, renamed_file_path)

            raise AssertionError(
                f"The workflow {raw_dir_path} could not be executed correctly. "
                f"Changes were reverted."
                "\n"
                f"{absolute_path_list}"
                "\n"
                f"{sublist}"
            )


def test_pipeline_results():
    test_pipeline_folders(delete_switch, scenarios)
