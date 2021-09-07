import os
import numpy as np
import pandas as pd
import pytest

from oemof_b3.tools.data_processing import (
    get_optional_required_header,
    stack_timeseries,
    unstack_timeseries,
    load_scalars,
    load_timeseries,
    save_df,
    filter_df,
    aggregate_scalars,
    check_consistency_timeindex,
)

this_path = os.path.realpath(__file__)

ts_row_wise_cols = [
    "var_name",
    "timeindex_start",
    "timeindex_stop",
    "timeindex_resolution",
    "series",
]

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


def test_get_optional_required_header():
    """
    This test checks whether header of
    1. scalars and
    2. time series
    are returned correctly

    In a third test it is checked whether a ValueError
    is raised if an invalid string is passed with
    data_type

    """
    # 1. Test
    scalars_header_expected = [
        "id_scal",
        "scenario",
        "name",
        "var_name",
        "carrier",
        "region",
        "tech",
        "type",
        "var_value",
        "var_unit",
        "reference",
        "comment",
    ]
    scalars_header_optional_expected = ["id_scal", "var_unit", "reference", "comment"]

    scalars_header_required_expected = [
        "scenario",
        "name",
        "var_name",
        "carrier",
        "region",
        "tech",
        "type",
        "var_value",
    ]

    scalars_header_results = get_optional_required_header("scalars")

    assert scalars_header_results[0] == scalars_header_expected
    assert scalars_header_results[1] == scalars_header_optional_expected
    assert scalars_header_results[2] == scalars_header_required_expected

    # 2. Test
    timeseries_header_expected = [
        "id_ts",
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
    timeseries_header_optional_expected = [
        "id_ts",
        # "region",
        "var_unit",
        "source",
        "comment",
    ]
    timeseries_header_required_expected = [
        "region",
        "var_name",
        "timeindex_start",
        "timeindex_stop",
        "timeindex_resolution",
        "series",
    ]

    timeseries_header_results = get_optional_required_header("timeseries")

    assert timeseries_header_results[0] == timeseries_header_expected
    assert timeseries_header_results[1] == timeseries_header_optional_expected
    assert timeseries_header_results[2] == timeseries_header_required_expected

    # 3. Test
    with pytest.raises(ValueError):
        get_optional_required_header("something_else")


def test_load_scalars():
    """
    This test checks whether
    1. the DataFrame from read data contains all default columns and
    2. load_scalars errors out if data is missing a required column

    """
    # 1. Test
    cols_list = [
        "scenario",
        "name",
        "var_name",
        "carrier",
        "region",
        "tech",
        "type",
        "var_value",
        "id_scal",
        "var_unit",
        "reference",
        "comment",
    ]

    path_file = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_scalars.csv",
    )

    df = load_scalars(path_file)
    df_cols = list(df.columns)

    for col in cols_list:
        assert col in df_cols

    # 2. Test
    path_file_missing_required = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_scalars_missing_required.csv",
    )
    with pytest.raises(KeyError):
        # Check whether reading a DataFrame missing required columns errors out
        load_scalars(path_file_missing_required)


def test_load_timeseries():
    """
    This test checks whether
    1.  the DataFrame read by load_timeseries function from data which is a
            a. time series with multiIndex
            b. sequence
            c. stacked time series / sequence
        contains all default columns and
    2.  load_timeseries errors out if data is missing a required column

    """
    # 1. Test
    cols_list = [
        "id_ts",
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

    # a. time series with multiIndex
    path_file_timeseries = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_timeseries.csv",
    )

    # b. sequence
    path_file_sequence = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_sequence.csv",
    )

    # c. stacked time series / sequence
    path_file_stacked = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_stacked.csv",
    )

    paths = [
        path_file_timeseries,
        path_file_sequence,
        path_file_stacked,
    ]

    # Run 1. Test for formats a., b. and c.
    for path_file in paths:
        df = load_timeseries(path_file)
        df_cols = list(df.columns)

        assert df_cols == cols_list

    # 2. Test
    path_file_stacked_missing_required = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_stacked_missing_required.csv",
    )

    with pytest.raises(KeyError):
        # Check whether reading a stacked DataFrame missing required columns errors out
        load_timeseries(path_file_stacked_missing_required)


def test_save_df():
    """
    This test checks for scalars and time series whether
    1. the path of the scalars stored in a csv file exists
    2. the DataFrame remain unchanged after saving. For this purpose, the data is read in again
    after saving and compared with the scalars originally read

    """
    # Scalars
    path_file_scalars = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_scalars.csv",
    )

    path_file_saved = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_scalars_saved.csv",
    )

    # Read scalars
    df = load_scalars(path_file_scalars)

    # Save read scalars
    save_df(df, path_file_saved)

    # Load the saved scalars
    df_saved = load_scalars(path_file_saved)

    # 1. Test
    assert os.path.exists(path_file_saved) == 1

    # 2. Test
    pd.testing.assert_frame_equal(df, df_saved)

    # Remove saved scalars which were saved for this test
    os.remove(path_file_saved)

    # Time series
    path_file_timeseries = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_timeseries.csv",
    )
    df = load_timeseries(path_file_timeseries)

    path_file_stacked = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_stacked_saved.csv",
    )

    save_df(df, path_file_stacked)
    assert os.path.exists(path_file_stacked) == 1

    df_saved = load_timeseries(path_file_stacked)

    pd.testing.assert_series_equal(df["series"], df_saved["series"])
    pd.testing.assert_frame_equal(df, df_saved)

    os.remove(path_file_stacked)


def test_filter_df():
    """
    This test checks whether
    1. scalars and
    2. time series
    are filtered by a key and value

    """
    # 1. Test
    path_file_scalars = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_scalars.csv",
    )

    # Read scalars
    df = load_scalars(path_file_scalars)

    df_BE = filter_df(df, "region", ["BE"])

    assert df_BE["region"].values[0] == "BE"
    assert len(df_BE["region"]) == 7

    df_BE_BB = filter_df(df, "region", ["BE_BB"])

    assert df_BE_BB.empty

    df_conversion = filter_df(df, "type", ["conversion"])
    assert len(df_conversion["type"]) == 10

    with pytest.raises(KeyError):
        filter_df(df, "something", ["conversion"])

    # 2. Test
    path_file_timeseries = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_stacked.csv",
    )

    # Read stacked time series
    df = load_timeseries(path_file_timeseries)

    df_BE_BB = filter_df(df, "region", ["BE_BB"])

    assert (
        df_BE_BB["region"].values[0] == "BE_BB"
        and df_BE_BB["region"].values[1] == "BE_BB"
    )
    assert len(df_BE_BB["region"]) == 2

    df_var_name = filter_df(
        df,
        "var_name",
        [
            "flow from BB-biomass-st to BB-electricity",
            "flow from BB-electricity-liion-battery to BB-electricity",
        ],
    )

    assert (
        df_var_name["var_name"].values[0] == "flow from BB-biomass-st to BB-electricity"
        and df_var_name["var_name"].values[1]
        == "flow from BB-electricity-liion-battery to BB-electricity"
    )


def test_aggregate_scalars():
    """
    This test checks whether
    1. scalars and
    2. time series
    are aggregated by a key

    """
    # 1. Test
    path_file_scalars = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_scalars.csv",
    )

    # Read scalars
    df = load_scalars(path_file_scalars)

    # Aggregate by region
    df_aggregated_by_region = aggregate_scalars(df, "region")

    # Add expected results of aggregation
    df_aggregated_expected = pd.DataFrame(
        data={
            "id_scal": [None] * 8,
            "scenario": ["base"] * 8,
            "name": ["Aggregated by region"] * 8,
            "var_name": [
                "capacity",
                "flow_biomass",
                "flow_electricity",
                "costs",
                "capacity",
                "flow_biomass",
                "flow_electricity",
                "costs",
            ],
            "carrier": ["All"] * 8,
            "region": ["BE", "BE", "BE", "BE", "BB", "BB", "BB", "BB"],
            "tech": ["All"] * 8,
            "type": ["All"] * 8,
            "var_value": [
                0,
                0,
                13470154039.4199,
                0,
                400000,
                2692790078.846871,
                25900023216.653,
                108971828.939188,
            ],
            "var_unit": ["-"] * 8,
            "reference": [None] * 8,
            "comment": [None] * 8,
        }
    )

    # Check if results of aggregation equal the expected ones
    pd.testing.assert_frame_equal(df_aggregated_by_region, df_aggregated_expected)

    # Aggregate by carrier
    df_aggregated_by_carrier = aggregate_scalars(df, "carrier")

    assert list(df_aggregated_by_carrier["var_value"].values) == [
        400000,
        2692790078.846871,
        -1023260209.6668,
        108971828.9391882,
        40393437465.7397,
    ]

    # Aggregate by tech
    df_aggregated_by_tech = aggregate_scalars(df, "tech")

    expected_results_series_tech = [
        400000.000,
        2692790078.847,
        -1023260209.667,
        108971828.939,
        6666117465.740,
        33727320000.000,
    ]

    for index, item in enumerate(list(df_aggregated_by_tech["var_value"].values)):
        assert round(item, 3) == expected_results_series_tech[index]

    # 2. Test
    path_file_timeseries = os.path.join(
        os.path.abspath(os.path.join(this_path, os.pardir)),
        "_files",
        "test_stacked.csv",
    )

    # Read stacked time series
    df = load_timeseries(path_file_timeseries)

    # Aggregate by region
    df_aggregated_by_region = aggregate_scalars(df, "region")

    # Add expected results of aggregation
    df_aggregated_expected = pd.DataFrame(
        data={
            "id_ts": [None] * 2,
            "region": ["BB", "BE_BB"],
            "var_name": ["Aggregated by region"] * 2,
            "timeindex_start": [df["timeindex_start"][0]] * 2,
            "timeindex_stop": [df["timeindex_stop"][0]] * 2,
            "timeindex_resolution": [df["timeindex_resolution"][0]] * 2,
            "series": [
                [3917414.00714099, 3865968.88012165, 3688842.50107082],
                [137824.4, 125071.28, 81162.145],
            ],
            "var_unit": ["-"] * 2,
            "source": [None] * 2,
            "comment": [None] * 2,
        }
    )

    # Check if results of aggregation equal the expected ones
    pd.testing.assert_frame_equal(df_aggregated_by_region, df_aggregated_expected)


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
        "test_sequence.csv",
    )

    df = pd.read_csv(file_path, index_col=0)
    df.index = pd.to_datetime(df.index)

    df_stacked = stack_timeseries(df)
    df_unstacked = unstack_timeseries(df_stacked)
    assert pd.testing.assert_frame_equal(df, df_unstacked) is None
