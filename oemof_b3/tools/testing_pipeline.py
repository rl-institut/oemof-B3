"""
This script contains functions to test the files and directories created
through the snakemake pipeline.
"""
import os
import subprocess
import snakemake
import shutil
import logging
import sys


def install_with_extra(extra):
    """
    This function installs extra packages stored in tool.poetry.extras.

    Inputs
    -------
    extra : str
        Name of the list with the extra packages to be installed
        from pyproject.toml as string

    Outputs
    -------
    None

    """
    try:
        subprocess.run(["poetry", "install", "-E", extra], check=True)
        print(
            f"Successfully installed packages with extra environment {extra} using Poetry!"
        )
    except subprocess.CalledProcessError as e:
        print(
            f"Error installing packages with extra environment {extra} using Poetry: {e}"
        )


def get_repo_path(current_path):
    """
    This function sets the current path to oemof-B3 as target directory.

    Inputs
    -------
    current_path : str
        Path to the current directory

    Outputs
    -------
    target_path : str
        Absolut path to target directory

    """
    target_path = current_path  # as the starting point

    # Define the target directory name
    target_directory = "oemof-B3"

    # Loop until the target path is found
    while os.path.basename(target_path) != target_directory:
        target_path = os.path.dirname(target_path)
        if target_path == os.path.expanduser("~"):
            raise ValueError(
                f"Target directory '{target_directory}' not found in the path hierarchy."
            )

    return target_path


def get_raw_path():
    """
    This function returns the absolute path to raw directory.

    Inputs
    -------

    Outputs
    -------
    raw_dir_path : str
        Absolute file path to directory raw

    """
    this_path = os.path.abspath(os.getcwd())
    repo_path = get_repo_path(this_path)
    raw_dir_path = os.path.join(repo_path, "raw")

    return raw_dir_path


def check_raw_data_exists():
    """
    This function checks if raw data already exists in repo. If not the corresponding rule is
    triggered. If the rule fails an exception is raised and user gets notified.

    Inputs
    -------

    Outputs
    -------
    bool
        True if raw data exists and False if it does not
    """
    raw_dir_path = get_raw_path()

    raw_dir_rule = ["raw/oemof-B3-raw-data.zip"]

    if not os.path.isdir(raw_dir_path):
        output = snakemake.snakemake(
            targets=raw_dir_rule,
            snakefile="Snakefile",
        )

        if not output:
            raise FileExistsError(
                f"The output corresponding to rule {raw_dir_rule[0]} could not be created. \n"
                f"Hence this tests are failing."
            )

        return False
    else:
        return True


def remove_raw_data_created():
    """
    This function removes the 'raw' directory that has been created for the test to run.

    Inputs
    -------

    Outputs
    -------
    None

    """
    raw_dir_path = get_raw_path()

    if os.path.isdir(raw_dir_path):
        shutil.rmtree(raw_dir_path)
    else:
        raise FileNotFoundError(
            f"Something went wrong. {raw_dir_path} has been created but could not be found."
        )


def remove_test_results():
    """
    This function removes files in 'results' directory.

    Inputs
    -------

    Outputs
    -------
    None

    """

    # Determine the OS
    if sys.platform.startswith("win"):
        clean_target = ["clean_on_win_sys"]
    else:
        clean_target = ["clean"]

    # Revert all file changes -> clean all results
    snakemake.snakemake(
        targets=clean_target,
        snakefile="Snakefile",
    )


def get_abs_path_list(output_rule_list):
    """
    This function returns the absolut file path for each rule in the output_rule_list.

    Inputs
    -------
    output_rule_list : str
        File path of rule

    Outputs
    -------
    absolute_path_list : list
        Absolute file path in list

    """
    # Get absolute path of rule
    absolute_path_list = [os.path.abspath(entry) for entry in output_rule_list]

    return absolute_path_list


def rule_test(rule_path):
    """
    This function runs a specific rule with snakemake and asserts a successful run with True.

    Inputs
    -------
    rule_path : str
        Path of rule

    Outputs
    -------
    None

    """
    # Run the snakemake rule in this loop
    output = snakemake.snakemake(
        targets=rule_path,
        snakefile="Snakefile",
    )

    # Check if snakemake rule exited without error (true)
    assert output

    # Log the success
    logging.info(f"Snakemake rule executed successfully for targets: {rule_path}")


def pipeline_output_test(delete_switch, output_rule_list):
    """
    ...

    Inputs
    -------
    delete_switch : bool
        If True, delete the data created during the test run.
        If False, do not delete the data.
    output_rule_list : list of str
        Nested list with sublist containing paths to target files
        associated with a specific rule.

    Outputs
    -------
    None

    """
    # Raw data is needed for some rules and therefore is created if missing
    raw_data_exists = check_raw_data_exists()

    # TODO @ Alaadin17: Implement here: If results_path (= dir "results") not empty, raise:
    #         raise FileExistsError(
    #             f"The directory {results_path} is not empty. \n"
    #             f"The test can not be executed. Please delete all files in {results_path} first
    #             and then execute again."
    #         )

    for sublist in output_rule_list:
        absolute_path_list = get_abs_path_list(sublist)

        try:
            # Run the snakemake rule
            rule_test(sublist)

            # Check if the output file was created
            for raw_dir_path in absolute_path_list:
                assert os.path.exists(raw_dir_path)

        except BaseException:
            remove_test_results()

            raise AssertionError(
                f"The workflow {absolute_path_list[0]} could not be executed correctly. "
                f"Changes were reverted."
            )

    # Remove all files in results
    if delete_switch:
        remove_test_results()

    # Remove raw data if it has been created. It is needed as input data for the tests
    if raw_data_exists:
        remove_raw_data_created()
