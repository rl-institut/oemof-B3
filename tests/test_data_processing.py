import os
import numpy as np
import pandas as pd
import pytest
import unittest
from unittest.mock import patch

from oemof_b3.tools.data_processing import (
    HEADER_B3_SCAL,
    HEADER_B3_TS,
    stack_timeseries,
    unstack_timeseries,
    stack_var_name,
    unstack_var_name,
    load_b3_scalars,
    load_b3_timeseries,
    load_tabular_results_ts,
    save_df,
    filter_df,
    update_filtered_df,
    aggregate_scalars,
    aggregate_timeseries,
    check_consistency_timeindex,
    merge_a_into_b,
    oemof_results_ts_to_oemof_b3,
)

# Paths
this_path = os.path.abspath(os.path.dirname(__file__))


def full_path(filename):
    return os.path.join(this_path, "_files", filename)


path_file_sc = full_path("oemof_b3_resources_scalars.csv")
path_file_sc_scenarios = full_path("oemof_b3_resources_scalars_scenarios.csv")
path_file_sc_update_scenarios_expected = full_path(
    "oemof_b3_resources_scalars_update_scenarios_expected.csv"
)
path_file_sc_mixed_types = full_path("oemof_b3_resources_scalars_mixed_types.csv")
path_file_ts_stacked = full_path("oemof_b3_resources_timeseries_stacked.csv")
path_file_ts_stacked_comments = full_path(
    "oemof_b3_resources_timeseries_stacked_comments.csv"
)
path_oemof_results_flows = full_path("oemof_results_flows.csv")
path_oemof_b3_results_timeseries_flows = full_path(
    "oemof_b3_results_timeseries_flows.csv"
)
path_oemof_results_storage_content = full_path("oemof_results_storage_content.csv")
path_oemof_b3_results_timeseries_storage_content = full_path(
    "oemof_b3_results_timeseries_storage_content.csv"
)

# Headers
sc_cols_list = list(HEADER_B3_SCAL)

ts_cols_list = list(HEADER_B3_TS)

ts_row_wise_cols = [
    "var_name",
    "timeindex_start",
    "timeindex_stop",
    "timeindex_resolution",
    "series",
]

# DataFrames
ts_column_wise = pd.DataFrame(
    np.random.randint(0, 10, size=(25, 3)),
    columns=list("ABC"),
    index=pd.date_range("2021-01-01", "2021-01-02", freq="H"),
)

ts_column_wise_different = pd.DataFrame(
    np.random.randint(0, 5, size=(25, 3)),
    columns=list("ABC"),
    index=pd.date_range("2021-01-01", "2021-01-02", freq="H"),
)


def test_load_b3_scalars():
    """
    This test checks whether the DataFrame from read data contains all default columns
    """

    df = load_b3_scalars(path_file_sc)
    df_cols = list(df.columns)

    for col in sc_cols_list:
        assert col in df_cols


def test_load_b3_scalars_mixed_types():
    """
    This test checks whether the entries in "var_value" have the correct types.
    """

    df = load_b3_scalars(path_file_sc_mixed_types)

    types = [type(value) for value in df["var_value"]]

    # could more strictly assert that types are [int, float, bool, str, dict] as soon as this is
    # needed.

    assert types == [float, float, str, str, str], f"Types are {types}"


def test_load_b3_timeseries():
    """
    This test checks whether the DataFrame read by load_b3_timeseries function from data which is a
    c. stacked timeseries
    contains all default columns
    """
    df = load_b3_timeseries(path_file_ts_stacked)
    df_cols = list(df.columns)

    assert df_cols == ts_cols_list


def test_load_b3_timeseries_interpret_series():
    df = load_b3_timeseries(path_file_ts_stacked)

    for _, row in df.iterrows():
        assert isinstance(row["series"], list)


def test_save_df_sc():
    """
    This test checks for scalars whether the DataFrame remain unchanged after
    saving

    For this purpose, the data is read in again after saving and compared with the data
    originally read
    """
    # Scalars

    path_file_saved = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_scalars_saved.csv",
    )

    # Read scalars
    df = load_b3_scalars(path_file_sc)

    # Save read scalars
    save_df(df, path_file_saved)

    # Load the saved scalars
    df_saved = load_b3_scalars(path_file_saved)

    # Test DataFrames are same
    pd.testing.assert_frame_equal(df, df_saved)

    # Remove saved scalars which were saved for this test
    os.remove(path_file_saved)


def test_save_df_ts():
    """
    This test checks for time series whether the DataFrame remain unchanged after
    saving

    For this purpose, the data is read in again after saving and compared with the data
    originally read
    """

    path_file_stacked_saved = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_timeseries_stacked_saved.csv",
    )

    # Read time series
    df = load_b3_timeseries(path_file_ts_stacked)

    # Save read time series
    save_df(df, path_file_stacked_saved)

    # Load the saved time series
    df_saved = load_b3_timeseries(path_file_stacked_saved)

    # Test DataFrames are same
    pd.testing.assert_series_equal(df["series"], df_saved["series"])
    pd.testing.assert_frame_equal(df, df_saved)

    # Remove saved time series which was saved for this test
    os.remove(path_file_stacked_saved)


def test_filter_df_sc_region_BE():
    """
    This test checks whether scalars are filtered correctly by key "region" and value "BE"
    """

    # Read scalars
    df = load_b3_scalars(path_file_sc)

    # Filter scalar by region "BE"
    df_BE = filter_df(df, "region", ["BE"])

    # Load expected filtered scalars
    path_file_filtered_sc = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_scalars_filtered_BE.csv",
    )
    df_filtered_sc_expected = load_b3_scalars(path_file_filtered_sc)

    # Test if expected and filtered DataFrame are same
    pd.testing.assert_frame_equal(df_filtered_sc_expected, df_BE)


def test_filter_df_sc_region_BE_BB():
    """
    This test checks whether scalars are filtered correctly by key "region" and value "BE_BB"
    """

    # Read scalars
    df = load_b3_scalars(path_file_sc)

    df_BE_BB = filter_df(df, "region", ["BE_BB"])

    assert df_BE_BB.empty


def test_filter_df_sc_type_conversion():
    """
    This test checks whether scalars are filtered correctly by key "type" and value "conversion"
    """

    # Read scalars
    df = load_b3_scalars(path_file_sc)

    # Filter scalar by type "conversion"
    df_conversion = filter_df(df, "type", ["conversion"])

    # Load expected filtered scalars
    path_file_filtered_sc = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_scalars_filtered_conversion.csv",
    )
    df_filtered_sc_expected = load_b3_scalars(path_file_filtered_sc)

    # Test if expected and filtered DataFrame are same
    pd.testing.assert_frame_equal(df_filtered_sc_expected, df_conversion)


def test_filter_df_sc_raises_error():
    """
    This test checks whether scalars are filtered correctly by key "region" and value "BE_BB"
    """
    # Read scalars
    df = load_b3_scalars(path_file_sc)

    with pytest.raises(KeyError):
        filter_df(df, "something", ["conversion"])


def test_update_filtered_df():

    df = load_b3_scalars(path_file_sc_scenarios)
    df_filtered_expected = load_b3_scalars(path_file_sc_update_scenarios_expected)

    filters = {
        1: {"scenario_key": "2050-base", "var_name": ["capacity_cost", "efficiency"]},
        2: {"scenario_key": "2050-eff", "var_name": ["capacity_cost", "efficiency"]},
    }

    df_filtered = update_filtered_df(df, filters)

    pd.testing.assert_frame_equal(df_filtered_expected, df_filtered, check_dtype=False)


def test_filter_df_ts():
    """
    This test checks whether time series is filtered by a key "region" and value "BE_BB"
    """

    # Read stacked time series
    df = load_b3_timeseries(path_file_ts_stacked)

    df_BE_BB = filter_df(df, "region", ["BE"])

    # Load expected filtered stacked time series
    path_file_filtered_ts = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_timeseries_stacked_filtered_BE.csv",
    )
    df_filtered_ts_expected = load_b3_timeseries(path_file_filtered_ts)

    # Test if expected and filtered DataFrame are same
    # ToDo: dtypes aren't same after filtering. To be changed in data_processing.py
    pd.testing.assert_frame_equal(df_filtered_ts_expected, df_BE_BB, check_dtype=False)


def test_df_agg_sc():
    """
    This test checks whether scalars are aggregated by a key
    """

    # 1. Test
    # Read scalars
    df = load_b3_scalars(path_file_sc)

    # Aggregate by region
    df_agg_by_region = aggregate_scalars(df, "region")

    # Load expected aggregated DataFrame
    path_file_agg_sc = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_scalars_agg_region.csv",
    )
    df_agg_region_expected = load_b3_scalars(path_file_agg_sc)

    # Check if results of aggregation equal the expected ones
    pd.testing.assert_frame_equal(
        df_agg_by_region, df_agg_region_expected, check_dtype=False
    )

    # Aggregate by carrier
    df_agg_by_carrier = aggregate_scalars(df, "carrier")

    # Load expected aggregated DataFrame
    path_file_agg_sc = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_scalars_agg_carrier.csv",
    )
    df_agg_carrier_expected = load_b3_scalars(path_file_agg_sc)

    # Check if results of aggregation equal the expected ones
    pd.testing.assert_frame_equal(
        df_agg_by_carrier, df_agg_carrier_expected, check_dtype=False
    )

    # Aggregate by tech
    df_agg_by_tech = aggregate_scalars(df, "tech")

    # Load expected aggregated DataFrame
    path_file_agg_sc = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_scalars_agg_tech.csv",
    )
    df_agg_tech_expected = load_b3_scalars(path_file_agg_sc)

    # Check if results of aggregation equal the expected ones
    pd.testing.assert_frame_equal(
        df_agg_by_tech, df_agg_tech_expected, check_dtype=False
    )


def test_df_agg_sc_with_nan():
    """
    This test checks whether scalars containing nan are aggregated by a key
    """

    df = load_b3_scalars(path_file_sc)
    df["carrier"].iloc[1] = np.nan
    df_agg_by_region = aggregate_scalars(df, "region")
    assert np.isnan(df_agg_by_region["carrier"].iloc[1])


def test_df_agg_ts():
    """
    This test checks whether a time series is aggregated by a key
    """
    # Read stacked time series
    df = load_b3_timeseries(path_file_ts_stacked)

    # Aggregate by region
    df_agg_by_region = aggregate_timeseries(df, "region")

    # Load expected filtered stacked time series
    path_file_agg_ts = os.path.join(
        this_path,
        "_files",
        "oemof_b3_resources_timeseries_stacked_agg_region.csv",
    )
    df_agg_expected = load_b3_timeseries(path_file_agg_ts)

    # Check if results of aggregation equal the expected ones
    pd.testing.assert_frame_equal(df_agg_by_region, df_agg_expected, check_dtype=False)


def test_check_consistency():
    """
    This test checks whether
    1. "timeindex_start",
    2. "timeindex_stop" and
    3. "timeindex_resolution"

    are same in each row. For this purpose, a correctly formatted Dataframe and a modified
    Dataframe containing a non-consistent entry are tested

    """
    df_stacked = stack_timeseries(ts_column_wise)

    frequency = check_consistency_timeindex(df_stacked, "timeindex_resolution")
    timeindex_start = check_consistency_timeindex(df_stacked, "timeindex_start")
    timeindex_stop = check_consistency_timeindex(df_stacked, "timeindex_stop")

    assert timeindex_start == pd.to_datetime("2021-01-01 00:00:00")
    assert timeindex_stop == pd.to_datetime("2021-01-02 00:00:00")
    assert frequency == "H"

    df_stacked_modified = df_stacked.copy()
    df_stacked_modified.at["timeindex_resolution", 1] = "M"
    df_stacked_modified.at["timeindex_start", 1] = pd.to_datetime("2021-01-01 00:00:10")
    df_stacked_modified.at["timeindex_stop", 1] = pd.to_datetime("2021-01-02 00:00:10")

    with pytest.raises(ValueError):
        check_consistency_timeindex(df_stacked_modified, "timeindex_resolution")
        check_consistency_timeindex(df_stacked_modified, "timeindex_start")
        check_consistency_timeindex(df_stacked_modified, "timeindex_stop")


def test_stack():
    """
    This test checks whether the stacked DataFrame "ts_row_wise"
    contains the after stacking expected columns "ts_row_wise_cols"
    """

    ts_row_wise = stack_timeseries(ts_column_wise)

    assert list(ts_row_wise.columns) == ts_row_wise_cols


def test_unstack():
    """
    This test checks if a dummy DataFrame remains unchanged through stacking
    and unstacking
    """

    ts_row_wise = stack_timeseries(ts_column_wise)
    ts_column_wise_again = unstack_timeseries(ts_row_wise)

    # Test will error out if the frames are not equal
    pd.testing.assert_frame_equal(ts_column_wise_again, ts_column_wise)

    # In case the test does not error out it is None. Hence a passed test results
    # to None
    assert pd.testing.assert_frame_equal(ts_column_wise_again, ts_column_wise) is None
    with pytest.raises(AssertionError):
        pd.testing.assert_frame_equal(ts_column_wise_again, ts_column_wise_different)


def test_stack_unstack_timeseries_on_example_data():
    """
    This test checks if a DataFrame with a test sequence remains unchanged through stacking
    and unstacking
    """

    file_path = os.path.join(
        this_path,
        "_files",
        "oemof_tabular_sequence.csv",
    )

    df = pd.read_csv(file_path, index_col=0, sep=";")
    df.index = pd.to_datetime(df.index)
    df = df.asfreq("H")

    df_stacked = stack_timeseries(df)
    df_unstacked = unstack_timeseries(df_stacked)
    assert pd.testing.assert_frame_equal(df, df_unstacked) is None


def test_unstack_stack_scalars_on_example_data():
    """
    This test checks oemof-B3 scalars remains unchanged through stacking
    and unstacking.

    ATTENTION: This only works if the input data is sorted in the standard
    order defined in data_processing.py.
    """
    df = load_b3_scalars(path_file_sc)

    df_unstacked = unstack_var_name(df)
    df_stacked = stack_var_name(df_unstacked)

    assert pd.testing.assert_frame_equal(df, df_stacked) is None


class test_unstack_warning_source_comment(unittest.TestCase):
    """
    This test verifies whether the caution message is appropriately raised
    when executing the function unstack_timeseries(). The caution message will
    be raised if source and comments are not empty.
    """

    def setUp(self):
        self.df_with_comments = load_b3_timeseries(path_file_ts_stacked_comments)
        self.df_wo_comments = load_b3_timeseries(path_file_ts_stacked)

    # Assert WARNING with unstack_timeseries(df_with_comments)
    def test_unstack_warning_source_comment(self):
        # Patch the logger.warning method to capture the warning calls
        with patch(
            "oemof_b3.tools.data_processing.logger.warning"
        ) as mock_logger_warning:
            # Call the function with df_with_comments, which should raise a warning
            unstacked_df = unstack_timeseries(self.df_with_comments)

        # Check if the logger.warning was called with the expected messages
        expected_warnings = [
            "Caution any remarks in column 'source' are lost after unstacking.",
            "Caution any remarks in column 'comment' are lost after unstacking.",
        ]

        # Check if any of the expected warning messages are contained in the captured warning messages
        self.assertTrue(
            any(
                warning_msg in str(warning[0])
                for warning in mock_logger_warning.call_args_list
                for warning_msg in expected_warnings
            )
        )

    # Assert that unstack_timeseries(df_wo_comments) does not give the warning:
    def test_unstack_no_warning(self):
        # Patch the logger.warning method to capture the warning calls
        with patch(
            "oemof_b3.tools.data_processing.logger.warning"
        ) as mock_logger_warning:
            # Call the function with df_wo_comments, which should not raise a warning
            unstacked_df = unstack_timeseries(self.df_wo_comments)

        # Check that logger.warning was not called in this case
        mock_logger_warning.assert_not_called()


if __name__ == "__main__":
    unittest.main()


def test_merge_a_into_b():
    r"""
    Tests merge function.
    """
    a = pd.DataFrame(
        {
            "A": ["a", "b", "x"],
            "B": [2, 2, 2],
            "C": [3, 3, 3],
        }
    )
    b = pd.DataFrame(
        {
            "A": ["a", "b", "c"],
            "B": [np.nan, np.nan, np.nan],
            "C": [1, np.nan, 1],
        }
    )
    a.index.name = "id_scal"
    b.index.name = "id_scal"

    expected_result = pd.DataFrame(
        {
            "A": ["a", "b", "c", "x"],
            "B": [2.0, 2.0, np.nan, 2.0],
            "C": [3.0, 3.0, 1.0, 3.0],
        }
    )

    c = merge_a_into_b(a, b, on=["A"], how="outer")

    assert c.equals(expected_result)


def test_oemof_results_flows_to_b3_ts():
    df = load_tabular_results_ts(path_oemof_results_flows)

    df_expected = load_b3_timeseries(path_oemof_b3_results_timeseries_flows)

    df = oemof_results_ts_to_oemof_b3(df)

    df[["timeindex_start", "timeindex_stop"]] = df[
        ["timeindex_start", "timeindex_stop"]
    ].astype(str)

    pd.testing.assert_frame_equal(df, df_expected)


def test_oemof_results_storage_content_to_b3_ts():
    df = load_tabular_results_ts(path_oemof_results_storage_content)

    df_expected = load_b3_timeseries(path_oemof_b3_results_timeseries_storage_content)

    df = oemof_results_ts_to_oemof_b3(df)

    df[["timeindex_start", "timeindex_stop"]] = df[
        ["timeindex_start", "timeindex_stop"]
    ].astype(str)

    pd.testing.assert_frame_equal(df, df_expected)
