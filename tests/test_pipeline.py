import os
import snakemake

# Navigate up one directory because of snakemake pipeline structure
os.chdir("..")

output_rule = "raw/scalars/empty_scalars.csv"
output_file_path = os.path.join(os.getcwd(), output_rule)


def check_if_output_exists(path):
    return os.path.exists(path)


def rename_file(before, after):
    # Split the path and file name
    directory, filename = os.path.split(output_file_path)

    # Add "_original" before the file extension
    new_filename = filename.replace(before, after)

    # Join the directory and new filename to get the new path
    new_file_path = os.path.join(directory, new_filename)

    # Check if file with name after already exists
    if check_if_output_exists(new_file_path):
        raise FileExistsError(
            f"File {new_file_path} already exists and therefore we can not rename your file"
            f" {filename}.\n"
            f"Please rename the file {new_filename} first."
        )

    # Rename the file
    os.rename(output_file_path, new_file_path)
    print(f"File '{filename}' has been")


def test_empty_scalars():
    if check_if_output_exists(output_file_path):
        rename_file(".csv", "_original.csv")

    try:
        # Run the snakemake rule: create_empty_scalars
        output = snakemake.snakemake(
            targets=[output_rule],
            snakefile="Snakefile",
        )

        assert output

        # Check if the output file was created
        assert os.path.exists(output_file_path)

        os.remove(output_file_path)

        rename_file("_original.csv", ".csv")

    except (BaseException):
        print(
            f"The workflow {output_rule} could not be executed correctly. "
            f"Changes will be reverted."
        )

        # Revert changes
        if check_if_output_exists():
            os.remove(output_file_path)

        rename_file("_original.csv", ".csv")
