import os
import ast
import pandas as pd
import numpy as np


here = os.path.dirname(__file__)

template_dir = os.path.join(here, "..", "schema")

HEADER_B3_SCAL = pd.read_csv(
    os.path.join(template_dir, "scalars.csv"), index_col=0, delimiter=";"
).columns

HEADER_B3_TS = pd.read_csv(
    os.path.join(template_dir, "timeseries.csv"), index_col=0, delimiter=";"
).columns


def get_list_diff(list_a, list_b):
    r"""
    Returns all items of list_a that are not in list_b.

    Parameters
    ----------
    list_a : list
        First list
    list_b : list
        Second list
    Returns
    -------
    list_a_diff_b : list
        List of all items in list_a that are not in list_b.
    """
    return list(set(list_a).difference(set(list_b)))


def format_header(df, header, index_name):
    r"""
    Formats columns of a DataFrame according to a specified header and index name.
    Fills missing columns with NaN. In case there are columns that are not in header,
    an error is raised.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to format
    header : list
        List of columns
    index_name : str
        Name of the index

    Returns
    -------
    df_formatted : pd.DataFrame
    """
    _df = df.copy()

    extra_colums = get_list_diff(_df.columns, header)

    if index_name in extra_colums:
        _df = _df.set_index(index_name, drop=True)
        extra_colums = get_list_diff(_df.columns, header)
    else:
        _df.index.name = index_name

    if extra_colums:
        raise ValueError(f"There are extra columns {extra_colums}")

    missing_columns = get_list_diff(header, _df.columns)

    for col in missing_columns:
        _df.loc[:, col] = np.nan

    try:
        df_formatted = _df[header]

    except KeyError:
        raise KeyError("Failed to format data according to specified header.")

    return df_formatted


def load_b3_scalars(path, sep=","):
    """
    This function loads scalars from a csv file.

    Parameters
    ----------
    path : str
        path of input file of csv format
    sep : str
        column separator

    Returns
    -------
    df : pd.DataFrame
        DataFrame with loaded scalars
    """
    # Read data
    df = pd.read_csv(path, sep=sep)

    df["var_value"] = pd.to_numeric(df["var_value"], errors="coerce").fillna(
        df["var_value"]
    )

    df = format_header(df, HEADER_B3_SCAL, "id_scal")

    df.loc[:, "var_value"] = df.loc[:, "var_value"].apply(
        lambda x: ast.literal_eval(x), 1
    )

    return df


def load_b3_timeseries(path, sep=","):
    """
    This function loads a stacked time series from a csv file.

    Parameters
    ----------
    path : str
        path of input file of csv format
    sep : str
        column separator

    Returns
    -------
    df : pd.DataFrame
        DataFrame with loaded time series
    """
    # Read data
    df = pd.read_csv(path, sep=sep)

    df = format_header(df, HEADER_B3_TS, "id_ts")

    df.loc[:, "series"] = df.loc[:, "series"].apply(lambda x: ast.literal_eval(x), 1)

    return df


def save_df(df, path):
    """
    This function saves data to a csv file.

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


def filter_df(df, column_name, values, inverse=False):
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
    inverse : Boolean
        If True, the entries for `column_name` and `values` are dropped
        and the rest of the DataFrame be retained.

    Returns
    -------
    df_filtered : pd.DataFrame
        Filtered data.
    """
    _df = df.copy()

    if isinstance(values, list):
        where = _df[column_name].isin(values)

    else:
        where = _df[column_name] == values

    if inverse:
        where = ~where

    df_filtered = _df.loc[where]

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
    df_aggregated = _df.groupby(groupby, sort=False).agg(agg_method)

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
    for all time steps.

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
    This function stacks a Dataframe in a form where one series resides in one row.

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
    This function unstacks a Dataframe so that there is a row for each value.

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


def unstack_var_name(df):
    r"""
    Given a DataFrame in oemof_b3 scalars format, this function will unstack
    the variables. The returned DataFrame will have one column for each var_name.

    Parameters
    ----------
    df : pd.DataFrame
        Stacked scalar data.
    Returns
    -------
    unstacked : pd.DataFrame
        Unstacked scalar data.
    """
    _df = df.copy()

    _df = format_header(_df, HEADER_B3_SCAL, "id_scal")

    _df = _df.set_index(
        ["scenario", "name", "region", "carrier", "tech", "type", "var_name"]
    )

    unstacked = _df.unstack("var_name")

    return unstacked


def stack_var_name(df):
    r"""
    Given a DataFrame, this function will stack the variables.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with one column per variable

    Returns
    -------
    stacked : pd.DataFrame
        DataFrame with a column "var_name" and "var_value"
    """
    assert isinstance(df, pd.DataFrame)

    _df = df.copy()

    _df.columns.name = "var_name"

    stacked = _df.stack("var_name")

    stacked.name = "var_value"

    stacked = pd.DataFrame(stacked).reset_index()

    return stacked


class ScalarProcessor:
    r"""
    This class allows to filter and unstack scalar data in a way that makes processing simpler.
    """

    def __init__(self, scalars):
        self.scalars = scalars

    def get_unstacked_var(self, var_name):
        r"""
        Filters the scalars for the given var_name and returns the data in unstacked form.

        Parameters
        ----------
        var_name : str
            Name of the variable

        Returns
        -------
        result : pd.DataFrame
            Data in unstacked form.
        """
        _df = filter_df(self.scalars, "var_name", var_name)

        if _df.empty:
            raise ValueError(f"No entries for {var_name} in df.")

        _df = unstack_var_name(_df)

        result = _df.loc[:, "var_value"]

        return result

    def drop(self, var_name):

        self.scalars = filter_df(self.scalars, "var_name", var_name, inverse=True)

    def append(self, var_name, data):
        r"""
        Accepts a Series or DataFrame in unstacked form and appends it to the scalars.

        Parameters
        ----------
        var_name : str
            Name of the data to append
        data : pd.Series or pd.DataFrame
            Data to append

        Returns
        -------
        None
        """
        _df = data.copy()

        if isinstance(_df, pd.Series):
            _df.name = var_name

            _df = pd.DataFrame(_df)

        _df = stack_var_name(_df)

        _df = format_header(_df, HEADER_B3_SCAL, "id_scal")

        self.scalars = self.scalars.append(_df)
