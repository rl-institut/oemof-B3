import os
import snakemake
import shutil
from oemof_b3.tools.testing_pipeline import get_repo_path, pipeline_file_output_test


# Delete data from test run of pipeline if True otherwise False
delete_switch = True

# Get current path
current_path = os.path.abspath(os.getcwd())
target_path = get_repo_path(current_path)

# Set the current path to the target path
os.chdir(target_path)

raw_dir_rule = "raw/oemof-B3-raw-data.zip"
raw_dir = "raw"

output_rule_list = [
    ["raw/scalars/empty_scalars.csv"],
    [
        "raw/time_series/empty_ts_load.csv",
        "raw/time_series/empty_ts_feedin.csv",
        "raw/time_series/empty_ts_efficiencies.csv",
    ],
]


def test_raw_dir():
    absolute_path = os.path.join(os.getcwd(), raw_dir)

    # Check if raw dir already exists
    if os.path.isdir(absolute_path):
        renamed_path = absolute_path + "_original"
        shutil.move(absolute_path, renamed_path)
    else:
        renamed_path = None

    try:
        # Run the snakemake rule in this loop
        output = snakemake.snakemake(
            targets=[raw_dir_rule],
            snakefile="Snakefile",
        )

        # Check if snakemake rule exited without error (true)
        assert output
        assert os.path.exists(absolute_path)

        if delete_switch or renamed_path:
            if os.path.isdir(absolute_path):
                shutil.rmtree(absolute_path)

        if renamed_path:
            if os.path.isdir(renamed_path):
                shutil.move(renamed_path, absolute_path)

    except BaseException as e:
        if os.path.isdir(absolute_path):
            shutil.rmtree(absolute_path)

        if renamed_path:
            if os.path.isdir(renamed_path):
                shutil.move(renamed_path, absolute_path)

        raise Exception(f"The test of {raw_dir_rule} failed.") from e


def test_pipeline_raw():
    pipeline_file_output_test(delete_switch, output_rule_list)
