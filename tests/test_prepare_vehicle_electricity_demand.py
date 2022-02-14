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
temp_filename = os.path.join(
    test_dir,
    "_files",
    "temp.csv",
)


def _save_and_reload_ts(df):
    save_df(df, temp_filename)
    df = load_b3_timeseries(temp_filename)
    return df


def test_prepare_vehicle_charging_demand():
    df = prepare_vehicle_charging_demand(
        input_dir=vehicle_files_test_dir, balanced=True
    )

    # sort df to prevent failing in CI
    df.sort_values("region", inplace=True)

    # temporarily save df and load again for correct dtypes
    df = _save_and_reload_ts(df)

    # read expected results
    df_exp = load_b3_timeseries(filename_results)
    df_exp.sort_values("region", inplace=True)

    assert_frame_equal(df, df_exp)
    assert_series_equal(df["series"], df_exp["series"])


def test_prepare_vehicle_charging_demand_smoothing():
    df = prepare_vehicle_charging_demand(
        input_dir=vehicle_files_test_dir, balanced=True
    )

    # temporarily save df and load again for correct dtypes
    df = _save_and_reload_ts(df)

    assert sum(df["series"].iloc[0]) == float(1)


def teardown_function():
    os.remove(temp_filename)
