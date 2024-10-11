"""
This script contains functions to test the files and folders created
through the snakemake pipeline.
"""
import os
import subprocess
import snakemake
import shutil
import logging


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


def rename_path(file_path, before, after):
    """
    This function renames an existing file in a directory or the directory itself (if passed with
    file_path) by appending the extension "_original" to its name.

    Inputs
    -------
    file_path : str
        Absolute path to a directory
    before : str
        Original extension
    after : str
        Renamed extension

    Outputs
    -------
    new_file_path : str
        Renamed absolute file path

    """
    # Split the path and file name
    directory, filename = os.path.split(file_path)

    # Determine new name based on whether it's a file or directory
    if os.path.isfile(file_path):
        # Add "_original" before the file extension
        new_filename = filename.replace(before, after)
    else:
        # Todo: Make more robust by asking elif it is an directory
        # Add extension "_original" to the directory name
        new_filename = filename + "_original"

    # Join the directory and new filename to get the new path
    new_file_path = os.path.join(directory, new_filename)

    # Check if file with new extension already exists
    if os.path.exists(new_file_path):
        raise FileExistsError(
            f"File {new_file_path} already exists and therefore we can not rename your file"
            f" {filename}.\n"
            f"Please rename the file {new_filename} first."
        )

    # Rename the file
    os.rename(file_path, new_file_path)
    print(f"File '{filename}' has been renamed.")

    return new_file_path


def get_raw_path():
    """
    This function returns the absolute path to raw directory

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


def remove_raw_data_created(exists):
    """
    This function

    Inputs
    -------
    exists : bool
        True if raw data exists and False if not

    Outputs
    -------

    """
    raw_dir_path = get_raw_path()

    if not exists:
        if os.path.isdir(raw_dir_path):
            shutil.rmtree(raw_dir_path)
        else:
            raise FileNotFoundError(
                f"Something went wrong. {raw_dir_path} has been created but could not be found."
            )


def remove_test_data(path):
    """
    This function removes files or directories of the given path.

    Inputs
    -------
    path : str
        Absolute path to a file or directory

    Outputs
    -------
    None

    """
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


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


def file_name_extension(file_path):
    """
    This function rearranges the current absolute file path with the new extension '_original'.

    Inputs
    -------
    file_path : str
        Absolute path

    Outputs
    -------
    renamed_file_path : str

    """
    # Get file extension
    file_extension = file_path[file_path.rfind(".") + 1 :]
    # Rename existing user data
    renamed_file_path = rename_path(
        file_path, "." + file_extension, "_original." + file_extension
    )

    return renamed_file_path


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


def remove_extension(before, after):
    """
        This function

        Inputs
        -------
        before : list of str
            List of file path
        after :
            If True, delete the data created during the test run.
            If False, do not delete the data.
        renamed_file_path_list : list of str
            List with renamed absolute file path

        Outputs
        -------
        None

        """
    shutil.move(before, after)


def clean_file(file_path_list, delete_switch, renamed_file_path_list):
    """
    This function removes files and directories of the file path.
    If renamed, the function removes the file or directory extensions.

    Inputs
    -------
    file_path_list : list of str
        List of file path
    delete_switch : bool
        If True, delete the data created during the test run.
        If False, do not delete the data.
    renamed_file_path_list : list of str
        List with renamed absolute file path

    Outputs
    -------
    None

    """
    # Remove the file created for this test
    for file_path in file_path_list:
        if os.path.exists(file_path):
            if delete_switch or renamed_file_path_list:
                remove_test_data(file_path)

    # If file had to be renamed revert the changes
    for renamed_file in renamed_file_path_list:
        if os.path.isfile(renamed_file):
            file_extension = renamed_file[renamed_file.rfind(".") + 1 :]
            rename_path(
                renamed_file,
                "_original." + file_extension,
                "." + file_extension,
            )
        else:
            # If directory had to be renamed revert changes
            original_path = renamed_file.partition("_original")[0]
            remove_extension(renamed_file, original_path)


def pipeline_file_output_test(delete_switch, output_rule_list):
    """
    This function tests the Snakemake pipeline for a list of output rule
    files and reverts all changes made in the target directory.

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

    # Loop over each rule which is tested in the snakemake pipeline
    for sublist in output_rule_list:
        # Get absolute path of sublist
        absolute_path_list = get_abs_path_list(sublist)

        renamed_path = []
        for raw_file_path in absolute_path_list:
            # Check if file already exists in directory
            if os.path.isfile(raw_file_path):
                # Rename file with extension original
                renamed_file = file_name_extension(raw_file_path)
                renamed_path.append(renamed_file)

        try:
            # Run the snakemake rule
            rule_test(sublist)

            # Check if the output file was created
            for raw_file_path in absolute_path_list:
                assert os.path.exists(raw_file_path)

            # Revert file changes
            clean_file(sublist, delete_switch, renamed_path)

        except BaseException:
            # Revert file changes
            clean_file(sublist, delete_switch, renamed_path)

            raise AssertionError(
                f"The workflow {raw_file_path} could not be executed correctly. "
                f"Changes were reverted."
                "\n"
                f"{absolute_path_list}"
                "\n"
                f"{sublist}"
            )

    # Remove raw data if it has been created. It is needed as input data for the tests
    remove_raw_data_created(raw_data_exists)


def pipeline_folder_output_test(delete_switch, output_rule_list):
    # Raw data is needed for some rules and therefore is created if missing
    raw_data_exists = check_raw_data_exists()

    for sublist in output_rule_list:
        absolute_path_list = get_abs_path_list(sublist)

        renamed_file_path = []
        for raw_dir_path in absolute_path_list:
            try:
                # Check if file already exists in directory
                if os.path.isfile(raw_dir_path):
                    # Rename file with extension original
                    renamed_file = file_name_extension(raw_dir_path)
                    renamed_file_path.append(renamed_file)
                # Check if file already exists in directory
                if os.path.isdir(raw_dir_path):
                    # Rename file with extension original
                    renamed_file = rename_path(raw_dir_path, "", "")
                    renamed_file_path.append(renamed_file)
                else:
                    # Check for the file with the _original extension
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

    # Remove raw data if it has been created. It is needed as input data for the tests
    remove_raw_data_created(raw_data_exists)
