import os
import subprocess
import snakemake
import logging


def install_with_extra(extra):
    """
    This function installs extra packages stored in tool.poetry.extras.

    Inputs
    -------
    extra : str
        Name of extra packages in a list

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
    This function sets the current path to the target directory.

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
    This function renames existing files in directories by appending
    the suffix "_original" to their filenames.

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

    # Add suffix "_original" before the file extension
    new_filename = filename.replace(before, after)

    # Join the directory and new filename to get the new path
    new_file_path = os.path.join(directory, new_filename)

    # Check if file with new suffix already exists
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


def remove_test_data(path):
    if os.path.isfile(path):
        os.remove(path)


def get_abs_path_list(output_rule_list):
    """
    This function finds the absolut file path for each rule
    in the output_rule_list.

    Inputs
    -------
    output_rule_list : str
        File path of rule

    Outputs
    -------
    None

    """
    # Get absolute path of rule
    return [os.path.abspath(entry) for entry in output_rule_list]


def file_name_extension(raw_file_path):
    """
     This function rearranges the current absolute file path
     with the new extension suffix '_original'.

     Inputs
     -------
     raw_file_path : str
         Absolute path of rule

     Outputs
     -------
     renamed_path : str

    """
    renamed_path = []

    # Get file extension
    file_extension = raw_file_path[raw_file_path.rfind(".") + 1:]
    # Rename existing user data
    renamed_file = rename_path(
        raw_file_path, "." + file_extension, "_original." + file_extension
    )
    renamed_path.append(renamed_file)

    return renamed_path


def rule_test(sublist):
    """
     This function runs the rule from the output rule sublist.

     Inputs
     -------
     sublist : str
         Path of rule

     Outputs
     -------
     None

    """
    # Run the snakemake rule in this loop
    output = snakemake.snakemake(
        targets=sublist,
        snakefile="Snakefile",
    )

    # Check if snakemake rule exited without error (true)
    assert output, f"Snakemake rule failed for targets: {sublist}"

    # Log the success
    logging.info(f"Snakemake rule executed successfully for targets: {sublist}")


def clean_file(sublist, delete_switch, renamed_path):
    """
     This function removes test data files and reverts renamed files.

     Inputs
     -------
    sublist : list of str
        List of target paths of rules
    delete_switch : bool
        If True, delete the data created during the test run.
        If False, do not delete the data.
    renamed_path : list of str
        List of renamed target paths

     Outputs
     -------
     None

    """
    # Remove the file created for this test
    for raw_file_path in sublist:
        if os.path.exists(raw_file_path):
            if delete_switch or renamed_path:
                remove_test_data(raw_file_path)

        # If file had to be renamed revert the changes
    for renamed_file in renamed_path:
        if os.path.isfile(renamed_file):
            file_extension = renamed_file[renamed_file.rfind(".") + 1:]
            rename_path(
                renamed_file,
                "_original." + file_extension,
                "." + file_extension,
            )


def pipeline_file_output_test(delete_switch, output_rule_list):
    """
    This function tests the Snakemake pipeline for a list of output rules
    and reverts all changes made in the target directory.

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
    # Loop over each rule which is tested in the snakemake pipeline
    for sublist in output_rule_list:
        # Get absolute path of sublist
        absolute_path_list = get_abs_path_list(sublist)

        for raw_file_path in absolute_path_list:
            # Check if file already exists in directory
            if os.path.isfile(raw_file_path):
                # Rename file with extension original
                renamed_path = file_name_extension(raw_file_path)

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
