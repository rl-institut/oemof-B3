import os
import numpy as np
import pandas as pd
import pytest

from oemof_b3.tools.data_processing import (
    stack_timeseries,
    unstack_timeseries,
    load_b3_scalars,
    load_b3_timeseries,
    save_df,
    filter_df,
    update_filtered_df,
    aggregate_scalars,
    aggregate_timeseries,
    check_consistency_timeindex,
    merge_a_into_b,
)

# Paths
this_path = os.path.realpath(__file__)

path_file_sc = os.path.join(
    os.path.abspath(os.path.join(this_path, os.pardir)),
    "_files",
    "oemof_b3_resources_scalars.csv",
)

path_file_sc_scenarios = os.path.join(
    os.path.abspath(os.path.join(this_path, os.pardir)),
    "_files",
    "oemof_b3_resources_scalars_scenarios.csv",
)

path_file_sc_update_scenarios_expected = os.path.join(
    os.path.abspath(os.path.join(this_path, os.pardir)),
    "_files",
    "oemof_b3_resources_scalars_update_scenarios_expected.csv",
)

path_file_sc_mixed_types = os.path.join(
    os.path.abspath(os.path.join(this_path, os.pardir)),
    "_files",
    "oemof_b3_resources_scalars_mixed_types.csv",
)

path_file_ts_stacked = os.path.join(
    os.path.abspath(os.path.join(this_path, os.pardir)),
    "_files",
    "oemof_b3_resources_timeseries_stacked.csv",
)

# Headers
sc_cols_list = [
    "scenario_key",
    "name",
    "var_name",
    "carrier",
    "region",
    "tech",
    "type",
    "var_value",
    "var_unit",
    "source",
    "comment",
]

ts_cols_list = [
    "scenario_key",
    "region",
    "var_name",
    "timeindex_start",
    "timeindex_stop",
    "timeindex_resolution",
    "series",
    "var_unit",
    "source",
    "comment",
]

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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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
        os.path.abspath(os.path.join(this_path, os.pardir)),
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


def test_stack_unstack_on_example_data():
    """
    This test checks if a DataFrame with a test sequence remains unchanged through stacking
    and unstacking
    """

    file_path = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "oemof_tabular_sequence.csv",
    )

    df = pd.read_csv(file_path, index_col=0, sep=";")
    df.index = pd.to_datetime(df.index)
    df = df.asfreq("H")

    df_stacked = stack_timeseries(df)
    df_unstacked = unstack_timeseries(df_stacked)
    assert pd.testing.assert_frame_equal(df, df_unstacked) is None


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
