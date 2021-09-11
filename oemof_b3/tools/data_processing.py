import os
import ast
import pandas as pd
import numpy as np


here = os.path.dirname(__file__)

template_dir = os.path.join(here, "..", "..", "results", "_resources")

HEADER_B3_SCAL = pd.read_csv(
    os.path.join(template_dir, "_scalar_template.csv"), delimiter=";"
).columns

HEADER_B3_TS = pd.read_csv(
    os.path.join(template_dir, "_timeseries_template.csv"), delimiter=";"
).columns


def get_list_diff(list_a, list_b):
    return list(set(list_a).difference(set(list_b)))


def format_header(df, header, index_name):

    extra_colums = get_list_diff(df.columns, header)

    if extra_colums:
        raise ValueError(f"There are extra columns {extra_colums}")

    missing_columns = get_list_diff(header, df.columns)

    for col in missing_columns:
        df[col] = np.nan

    try:
        df_formatted = df[header]

    except KeyError:
        print("Failed to format data according to specified header.")

    df_formatted.set_index(index_name, inplace=True)

    if index_name in missing_columns:
        df_formatted.reset_index(inplace=True, drop=True)
        df_formatted.index.name = index_name

    return df_formatted


def load_b3_scalars(path):
    """
    This function loads scalars from a csv file

    Parameters
    ----------
    path : str
        path of input file of csv format
    Returns
    -------
    df : pd.DataFrame
        DataFrame with loaded scalars

    """
    # Read data
    df = pd.read_csv(path)

    df = format_header(df, HEADER_B3_SCAL, "id_scal")

    return df


def load_b3_timeseries(path):
    """
    This function loads a stacked time series from a csv file

    Parameters
    ----------
    path : str
        path of input file of csv format

    Returns
    -------
    df : pd.DataFrame
        DataFrame with loaded time series

    """
    # Read data
    df = pd.read_csv(path)

    df = format_header(df, HEADER_B3_TS, "id_ts")

    return df


def save_df(df, path):
    """
    This function saves data to a csv file

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to be saved

    path : str
        Path to save the csv file

    """
    # Save scalars to csv file
    df.to_csv(path, index=True)

    # Print user info
    print(f"User info: The DataFrame has been saved to: {path}.")


def filter_df(df, column_name, values):
    """
    This function filters a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame
    column_name : string
        The column's name to filter.
    values : str/numeric/list
        String, number or list of strings or numbers to filter by.

    Returns
    -------
    df_filtered : pd.DataFrame
        Filtered data.
    """
    _df = df.copy()

    if isinstance(values, list):
        df_filtered = _df.loc[df[column_name].isin(values)]

    else:
        df_filtered = _df.loc[df[column_name] == values]

    return df_filtered


def isnull_any(df):
    return df.isna().any().any()


def aggregate_units(units):
    r"""
    This function checks if units that should be aggregated are unique.
    If they are not, it raises an error. If they are, it returns the unique unit.

    Parameters
    ----------
    units:
        pd.Series of units

    Returns
    -------
    unique_unit : str
        Unique unit
    """
    unique_units = units.unique()

    if len(unique_units) > 1:
        raise ValueError("Units are not consistent!")
    else:
        return unique_units[0]


def aggregate_scalars(df, columns_to_aggregate, agg_method=None):
    r"""
    This functions aggregates scalar data in oemof-B3-resources format and sums up
    by region, carrier, tech or type.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame in oemof-B3-resources format.
    columns_to_aggregate : string or list
        The columns to sum together ('region', 'carrier', 'tech' or 'type).
    agg_method : dict
        Dictionary to specify aggregation method.

    Returns
    -------
    df_aggregated : pd.DataFrame
        Aggregated data.
    """
    _df = df.copy()
    df_columns = _df.columns
    if not isinstance(columns_to_aggregate, list):
        columns_to_aggregate = [columns_to_aggregate]

    # Define the columns that are split and thus not aggregated
    groupby = ["scenario", "carrier", "region", "tech", "type", "var_name"]

    groupby = list(set(groupby).difference(set(columns_to_aggregate)))

    # Define how to aggregate if
    if not agg_method:
        agg_method = {
            "var_value": sum,
            "name": lambda x: "None",
            "var_unit": aggregate_units,
        }

    # When any of the groupby columns has empty entries, print a warning
    _df_groupby = _df[groupby]
    if isnull_any(_df_groupby):
        columns_with_nan = _df_groupby.columns[_df_groupby.isna().any()].to_list()
        print(f"Some of the groupby columns contain NaN: {columns_with_nan}.")

        for item in columns_with_nan:
            groupby.remove(item)
        _df.drop(columns_with_nan, axis=1)

        print("Removed the columns containing NaN from the DataFrame.")

    # Groupby and aggregate
    df_aggregated = _df.groupby(groupby, sort=True).agg(agg_method)

    # Assign "ALL" to the columns that where aggregated.
    for col in columns_to_aggregate:
        df_aggregated[col] = "All"

    # Reset the index
    df_aggregated.reset_index(inplace=True)

    df_aggregated = format_header(df_aggregated, HEADER_B3_SCAL, "id_scal")

    return df_aggregated


def check_consistency_timeindex(df, index):
    """
    This function assert that values of a column in a stacked DataFrame are same
    for all time steps

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame for which the time index is checked
    index : string
        Index of values to be checked in the DataFrame

    Returns
    -------
    value : string
        Single value of the series of duplicates

    """
    if index == "timeindex_start":
        name = "start date"
    elif index == "timeindex_stop":
        name = "end date"
    elif index == "timeindex_resolution":
        name = "frequency"

    if np.all(df[index].array == df[index].array[0]):
        value = df[index].array[0]
        if value is None:
            raise TypeError(
                f"Your provided data is missing a {name}."
                f"Please make sure you pass the {name} with {index}."
            )
        else:
            return value
    else:
        raise ValueError(
            f"The {name} of your provided data doesn't match for all entries. "
            f"Please make sure to pass the {name} with {index}."
        )


def stack_timeseries(df):
    """
    This function stacks a Dataframe in a form where one series resides in one row

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to be stacked

    Returns
    -------
    df_stacked : pandas.DataFrame
        Stacked DataFrame

    """
    _df = df.copy()

    # Assert that _df has a timeindex
    if not isinstance(_df.index, pd.DatetimeIndex):
        raise TypeError(
            "Your data should have a time series as an index of the format "
            "'%Y-%m-%d %H:%M:%S'."
        )

    # Assert that frequency match for all time steps
    if pd.infer_freq(_df.index) is None:
        raise TypeError(
            "No frequency of your provided data could be detected."
            "Please provide a DataFrame with a specific frequency (eg. 'H' or 'T')."
        )

    _df_freq = pd.infer_freq(_df.index)
    if _df.index.freqstr is None:
        print(
            f"User info: The frequency of your data is not specified in the DataFrame, "
            f"but is of the following frequency alias: {_df_freq}. "
            f"The frequency of your DataFrame is therefore automatically set to the "
            f"frequency with this alias."
        )
        _df = _df.asfreq(_df_freq)

    # Stack timeseries
    df_stacked_cols = [
        "var_name",
        "timeindex_start",
        "timeindex_stop",
        "timeindex_resolution",
        "series",
    ]

    df_stacked = pd.DataFrame(columns=df_stacked_cols)

    timeindex_start = _df.index.values[0]
    timeindex_stop = _df.index.values[-1]

    for column in df.columns:
        var_name = column
        timeindex_resolution = _df[column].index.freqstr
        series = [list(_df[column].values)]

        column_data = [
            var_name,
            timeindex_start,
            timeindex_stop,
            timeindex_resolution,
            series,
        ]

        dict_stacked_column = dict(zip(df_stacked_cols, column_data))
        df_stacked_column = pd.DataFrame(data=dict_stacked_column)
        df_stacked = df_stacked.append(df_stacked_column, ignore_index=True)

    # Save name of the index in the unstacked DataFrame as name of the index of "timeindex_start"
    # column of stacked DataFrame, so that it can be extracted from it when unstacked again.
    df_stacked["timeindex_start"].index.name = _df.index.name

    return df_stacked


def unstack_timeseries(df):
    """
    This function unstacks a Dataframe so that there is a row for each value

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to be unstacked

    Returns
    -------
    df_unstacked : pandas.DataFrame
        Unstacked DataFrame

    """
    _df = df.copy()

    # Assert that frequency match for all time steps
    frequency = check_consistency_timeindex(_df, "timeindex_resolution")
    timeindex_start = check_consistency_timeindex(_df, "timeindex_start")
    timeindex_stop = check_consistency_timeindex(_df, "timeindex_stop")

    # Warn user if "source" or "comment" in columns of stacked DataFrame
    # These two columns will be lost once unstacked
    lost_columns = ["source", "comment"]
    for col in lost_columns:
        if col in list(df.columns):
            print(
                f"User warning: Caution any remarks in column '{col}' are lost after "
                f"unstacking."
            )

    # Process values of series
    values_series = []
    for row in _df.iterrows():
        values_series.append(row[1]["series"])

    values_array = np.array(values_series).transpose()

    # Unstack timeseries
    df_unstacked = pd.DataFrame(
        values_array,
        columns=list(_df["var_name"]),
        index=pd.date_range(timeindex_start, timeindex_stop, freq=frequency),
    )

    # Get and set index name from and to index name of "timeindex_start".
    # If it existed in the origin DataFrame, which has been stacked, it will be set to that one.
    df_unstacked.index.name = _df["timeindex_start"].index.name

    return df_unstacked
