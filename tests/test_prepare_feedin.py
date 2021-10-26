import os
from pandas.util.testing import assert_frame_equal, assert_series_equal

from scripts.prepare_feedin import prepare_time_series
from oemof_b3.tools.data_processing import load_b3_timeseries, save_df

# Paths
test_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))

filename_wind = os.path.join(
    test_dir,
    "_files",
    "ninja_wind_country_DE_current_merra-2_nuts-2_corrected_test_data.csv",
)
filename_pv = os.path.join(
    test_dir, "_files", "ninja_pv_country_DE_merra-2_nuts-2_corrected_test_data.csv"
)
filename_results = os.path.join(
    test_dir, "_files", "oemof_b3_resources_timeseries_feedin.csv"
)


def test_prepare_time_series_wind():
    df = prepare_time_series(
        filename_ts=filename_wind,
        year=2012,  # in the test files only years 2010, 2012 and 2013 are included
        type="wind",
    )
    # temporarily save df and load again for correct dtypes
    temp_filename = os.path.join(
        test_dir,
        "_files",
        "temp.csv",
    )
    save_df(df, temp_filename)
    df = load_b3_timeseries(temp_filename)

    # read expected results
    df_results = load_b3_timeseries(filename_results)
    df_exp = df_results.loc[df_results["var_name"] == "wind-profile"]

    assert_frame_equal(df, df_exp)
    assert_series_equal(df["series"], df_exp["series"])

    # delete temporary file
    os.remove(temp_filename)


def test_prepare_time_series_pv():
    df = prepare_time_series(
        filename_ts=filename_pv,
        year=2012,  # in the test files only years 2010, 2012 and 2013 are included
        type="pv",
    )
    # temporarily save df and load again for correct dtypes
    temp_filename = os.path.join(
        test_dir,
        "_files",
        "temp.csv",
    )
    save_df(df, temp_filename)
    df = load_b3_timeseries(temp_filename)

    # read expected results
    df_results = load_b3_timeseries(filename_results)
    df_exp = df_results.loc[df_results["var_name"] == "pv-profile"]

    assert_frame_equal(df, df_exp)
    assert_series_equal(df["series"], df_exp["series"])

    # delete temporary file
    os.remove(temp_filename)
