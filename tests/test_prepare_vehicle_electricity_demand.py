import os
from pandas.util.testing import assert_frame_equal, assert_series_equal

from scripts.prepare_vehicle_charging_demand import prepare_vehicle_charging_demand
from oemof_b3.tools.data_processing import load_b3_timeseries, save_df

# Paths
test_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))
vehicle_files_test_dir = os.path.join(test_dir, "_files", "test_vehicle_ts")
filename_results = os.path.join(
    test_dir, "_files", "oemof_b3_resources_timeseries_elec_vehicle_demand.csv"
)


def test_prepare_vehicle_time_series():
    df = prepare_vehicle_charging_demand(input_dir=vehicle_files_test_dir)

    # temporarily save df and load again for correct dtypes
    temp_filename = os.path.join(
        test_dir,
        "_files",
        "temp.csv",
    )
    save_df(df, temp_filename)
    df = load_b3_timeseries(temp_filename)

    # read expected results
    df_exp = load_b3_timeseries(filename_results)

    assert_frame_equal(df, df_exp)
    assert_series_equal(df["series"], df_exp["series"])

    # delete temporary file
    os.remove(temp_filename)
