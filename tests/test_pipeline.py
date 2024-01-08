import os
import snakemake

# Navigate up one directory because of snakemake pipeline structure
os.chdir("..")

# List of rules in snakemake pipeline of oemof-B3, which are tested
output_rule_list = ["raw/scalars/empty_scalars.csv"]


def rename_file(file_path, before, after):
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


def test_pipeline():
    # Loop over each rule which is tested in the snakemake pipeline
    for output_rule in output_rule_list:
        # Get absolute path
        output_file_path = os.path.join(os.getcwd(), output_rule)

        # Introduce a variable which indicates if data already calculated by user exists
        rename = False
        if os.path.exists(output_file_path):
            # Set renaming indicator to true because user data exists
            rename = True
            # Rename existing user data
            renamed_file_path = rename_file(output_file_path, ".csv", "_original.csv")

        try:
            # Run the snakemake rule in this loop
            output = snakemake.snakemake(
                targets=[output_rule],
                snakefile="Snakefile",
            )

            # Check if snakemake rule exited without error (true)
            assert output

            # Check if the output file was created
            assert os.path.exists(output_file_path)

            # Remove the file created for this test
            os.remove(output_file_path)

            # If file had to be renamed revert the changes
            if rename:
                rename_file(renamed_file_path, "_original.csv", ".csv")

        except BaseException:
            print(
                f"The workflow {output_rule} could not be executed correctly. "
                f"Changes will be reverted."
            )

            # Revert changes
            if os.path.exists(output_file_path):
                os.remove(output_file_path)

            if rename:
                rename_file(renamed_file_path, "_original.csv", ".csv")
