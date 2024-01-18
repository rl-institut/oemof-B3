import os
import snakemake
import shutil

# Navigate up one directory because of snakemake pipeline structure
os.chdir("..")

# Choose whether you want to delete test filst or not
delete_switch = True

# List of rules in snakemake pipeline of oemof-B3, which are tested
# Todo: Put entries also in lists, we need to loop over renaming cf. empty_ts
output_rule_list = [
    "raw/scalars/empty_scalars.csv",
    "results/_resources/scal_conv_pp.csv",
    "results/_resources/ts_feedin.csv",
    "results/_resources/ts_load_electricity.csv",
    "results/_resources/ts_load_electricity_vehicles.csv",
    "results/_resources/scal_costs_efficiencies.csv",
    "results/_resources/ts_efficiency_heatpump_small.csv",
    "results/_tables/technical_and_cost_assumptions_2050-base.csv",
    "results/_resources/plots/scal_conv_pp-capacity_net_el.png",
    "results/2050-100-el_eff/preprocessed",
    "results/2050-100-el_eff/optimized",
    "results/2050-100-el_eff/postprocessed",
    # "results/joined_scenarios/{scenario_group}/joined",
    "results/2050-100-el_eff/b3_results/data",
    "results/2050-100-el_eff/tables",
    # "results/joined_scenarios/{scenario_group}/joined_tables",
    "results/2050-100-el_eff/plotted/dispatch",
    "results/2050-100-el_eff/plotted/storage_level",
    "results/2050-100-el_eff/plotted/scalars",
    # "results/joined_scenarios/{scenario_group}/joined_plotted",
    "results/2050-100-el_eff/report",
]
zip_rule_list = [
    "raw/oemof-B3-raw-data.zip",
]
multiple_rule_list = [
    [
        "raw/time_series/empty_ts_load.csv",
        "raw/time_series/empty_ts_feedin.csv",
        "raw/time_series/empty_ts_efficiencies.csv",
    ],
    ["results/_resources/scal_load_heat.csv", "results/_resources/ts_load_heat.csv"],
    [
        "results/_resources/scal_power_potential_wind_pv.csv",
        "results/_tables/potential_wind_pv_kreise.csv",
    ],
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

# Todo: Implement check if geopandas and other needed packages installed


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
    if delete_switch:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def test_pipeline():
    # Loop over each rule which is tested in the snakemake pipeline
    for output_rule in output_rule_list:
        # Get absolute path
        output_path = os.path.join(os.getcwd(), output_rule)

        # Introduce a variable which indicates if data already calculated by user exists
        rename = False
        if os.path.exists(output_path):
            rename = True

        if os.path.isfile(output_path):
            # Get file extension
            file_extension = output_path[output_path.rfind(".") + 1 :]
            # Rename existing user data
            renamed_path = rename_path(
                output_path, "." + file_extension, "_original." + file_extension
            )

        elif os.path.isdir(output_path):
            renamed_path = output_path + "_original"
            shutil.move(output_path, renamed_path)

        try:
            # Run the snakemake rule in this loop
            output = snakemake.snakemake(
                targets=[output_rule],
                snakefile="Snakefile",
            )

            # Check if snakemake rule exited without error (true)
            assert output

            # Check if the output file was created
            assert os.path.exists(output_path)

            # Remove the file created for this test
            remove_test_data(output_path)

            # If file had to be renamed revert the changes
            if rename:
                if os.path.isfile(renamed_path):
                    rename_path(
                        renamed_path,
                        "_original." + file_extension,
                        "." + file_extension,
                    )
                elif os.path.isdir(renamed_path):
                    shutil.move(renamed_path, output_path)

        except BaseException:
            # Revert changes
            if os.path.exists(output_path):
                remove_test_data(output_path)

            if rename:
                if os.path.isfile(renamed_path):
                    rename_path(
                        renamed_path,
                        "_original." + file_extension,
                        "." + file_extension,
                    )
                elif os.path.isdir(renamed_path):
                    shutil.move(renamed_path, output_path)

            raise AssertionError(
                f"The workflow {output_rule} could not be executed correctly. "
                f"Changes were reverted."
            )
