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
    save_scalars,
    save_timeseries,
    df_filtered,
    df_agg,
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


def test_stack():

    ts_row_wise = stack_timeseries(ts_column_wise)

    assert list(ts_row_wise.columns) == ts_row_wise_cols


def test_unstack():

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
    this_path = os.path.realpath(__file__)
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
