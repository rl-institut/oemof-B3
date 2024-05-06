import os
import subprocess
import snakemake


def install_with_extra(extra):
    """
    This function installs extra packages stored in tool.poetry.extras

    Inputs
    -------
    extra : str
        Name of extra packages in a list.

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
    # Split the path and file name
    directory, filename = os.path.split(file_path)

    # Add "_original" before the file extension
    new_filename = filename.replace(before, after)

    # Join the directory and new filename to get the new path
    new_file_path = os.path.join(directory, new_filename)

    # Check if file with name after already exists
    if os.path.exists(new_file_path):
        raise FileExistsError(
            f"File {new_file_path} already exists and therefore we can not rename your file"
            f" {filename}.\n"
            f"Please rename the file {new_filename} first."
        )

    # Rename the file
    os.rename(file_path, new_file_path)
    print(f"File '{filename}' has been")

    return new_file_path


def remove_test_data(path):
    if os.path.isfile(path):
        os.remove(path)


def pipeline_file_output_test(delete_switch, output_rule_list):
    # Loop over each rule which is tested in the snakemake pipeline
    for sublist in output_rule_list:
        # Get absolute path
        absolute_path_list = [os.path.join(os.getcwd(), entry) for entry in sublist]

        renamed_path = []
        for raw_file_path in absolute_path_list:

            if os.path.isfile(raw_file_path):
                # Get file extension
                file_extension = raw_file_path[raw_file_path.rfind(".") + 1 :]
                # Rename existing user data
                renamed_file = rename_path(
                    raw_file_path, "." + file_extension, "_original." + file_extension
                )
                renamed_path.append(renamed_file)

        try:
            # Run the snakemake rule in this loop
            output = snakemake.snakemake(
                targets=sublist,
                snakefile="Snakefile",
            )

            # Check if snakemake rule exited without error (true)
            assert output

            # Check if the output file was created
            for raw_file_path in absolute_path_list:
                assert os.path.exists(raw_file_path)

            for raw_file_path in sublist:
                # Remove the file created for this test
                if os.path.exists(raw_file_path):
                    if delete_switch or renamed_path:
                        remove_test_data(raw_file_path)

            # If file had to be renamed revert the changes
            for renamed_file in renamed_path:
                if os.path.isfile(renamed_file):
                    rename_path(
                        renamed_file,
                        "_original." + file_extension,
                        "." + file_extension,
                    )

        except BaseException:
            # Revert changes
            for remove_raw_file_path in sublist:
                # Remove the file created for this test
                if os.path.exists(remove_raw_file_path):
                    remove_test_data(remove_raw_file_path)

            # If file had to be renamed revert the changes
            for renamed_file in renamed_path:
                if os.path.isfile(renamed_file):
                    rename_path(
                        renamed_file,
                        "_original." + file_extension,
                        "." + file_extension,
                    )

            raise AssertionError(
                f"The workflow {raw_file_path} could not be executed correctly. "
                f"Changes were reverted."
                "\n"
                f"{absolute_path_list}"
                "\n"
                f"{sublist}"
            )
