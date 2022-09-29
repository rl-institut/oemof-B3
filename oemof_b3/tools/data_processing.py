# coding: utf-8
r"""
Inputs
-------
HEADER_B3_SCAL : pandas.DataFrame
``oemof_b3/schema/scalars.csv``: Header of scalars template

HEADER_B3_TS : pandas.DataFrame
``oemof_b3/schema/timeseries.csv``: Header of timeseries template

Description
-------------
This script contains some helper functions for processing the data in oemof-B3, such as loading,
filtering, sorting, merging, aggregating and saving.

"""
import ast
import os
import warnings

import numpy as np
import oemof.tabular.facades
import pandas as pd

here = os.path.dirname(__file__)

template_dir = os.path.join(here, "..", "schema")

HEADER_B3_SCAL = pd.read_csv(
    os.path.join(template_dir, "scalars.csv"), index_col=0, delimiter=";"
).columns

HEADER_B3_TS = pd.read_csv(
    os.path.join(template_dir, "timeseries.csv"), index_col=0, delimiter=";"
).columns


def sort_values(df, reset_index=True):
    _df = df.copy()

    _df = _df.sort_values(by=["scenario_key", "carrier", "tech", "var_name", "region"])

    if reset_index:
        _df = _df.reset_index(drop=True)

        _df.index.name = "id_scal"

    return _df


def sum_series(series):
    """
    Enables ndarray summing into one list
    """
    summed_series = sum(series)
    if isinstance(summed_series, np.ndarray):
        return summed_series.tolist()
    else:
        return summed_series


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


def load_b3_scalars(path, sep=";"):
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

    return df


def load_b3_timeseries(path, sep=";"):
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


def _multi_load(paths, load_func):
    r"""
    Wraps a load_func to allow loading several dataframes at once.

    Parameters
    ----------
    paths : str or list of str
        Path or list of paths to data.
    load_func : func
        A function that is able to load data from a single path

    Returns
    -------
    result : pd.DataFrame
        DataFrame containing the concatenated results
    """
    if isinstance(paths, list):
        pass
    elif isinstance(paths, str):
        return load_func(paths)
    else:
        raise ValueError(f"{paths} has to be either list of paths or path.")

    dfs = []
    for path in paths:
        df = load_func(path)
        dfs.append(df)

    result = pd.concat(dfs)

    return result


def multi_load_b3_scalars(paths):
    r"""
    Loads scalars from several csv files.

    Parameters
    ----------
    paths : str or list of str
        Path or list of paths to data.

    Returns
    -------
    pd.DataFrame
    """
    return _multi_load(paths, load_b3_scalars)


def multi_load_b3_timeseries(paths):
    r"""
    Loads stacked timeseries from several csv files.

    Parameters
    ----------
    paths : str or list of str
        Path or list of paths to data.

    Returns
    -------
    pd.DataFrame
    """
    return _multi_load(paths, load_b3_timeseries)


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
    df.to_csv(path, index=True, sep=";")

    # Print user info
    print(f"User info: The DataFrame has been saved to: {path}.")


def load_tabular_results_scal(path):
    r"""
    Loads timeseries as given by oemof.tabular/oemoflex.

    Parameters
    ----------
    paths : str or list of str
        Path or list of paths to data.

    Returns
    -------
    pd.DataFrame
    """
    return pd.read_csv(path, header=[0])


def load_tabular_results_ts(path):
    r"""
    Loads timeseries as given by oemof.tabular/oemoflex.

    Parameters
    ----------
    paths : str or list of str
        Path or list of paths to data.

    Returns
    -------
    pd.DataFrame
    """
    return pd.read_csv(path, header=[0, 1, 2], parse_dates=[0], index_col=[0])


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


def multi_filter_df(df, **kwargs):
    r"""
    Applies several filters in a row to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Data in oemof_b3 format.
    kwargs : Additional keyword arguments
        Filters to apply

    Returns
    -------
    filtered_df : pd.DataFrame
        Filtered data
    """
    filtered_df = df.copy()
    for key, value in kwargs.items():
        filtered_df = filter_df(filtered_df, key, value)
    return filtered_df


def multi_filter_df_simultaneously(df, inverse=False, **kwargs):
    r"""
    Applies several filters simultaneously to a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Data in oemof_b3 format.
    inverse : bool
        If True, matching entries are dropped
        and the rest of the DataFrame kept.
    kwargs : Additional keyword arguments
        Filters to apply

    Returns
    -------
    filtered_df : pd.DataFrame
        Filtered data
    """
    _df = df.copy()

    all_wheres = []

    for key, value in kwargs.items():
        if isinstance(value, list):
            where = _df[key].isin(value)

        else:
            where = _df[key] == value

        all_wheres.append(where)

    all_wheres = pd.concat(all_wheres, 1).all(1)

    if inverse:
        all_wheres = ~all_wheres

    df_filtered = _df.loc[all_wheres]

    return df_filtered


def update_filtered_df(df, filters):
    r"""
    Accepts an oemof-b3 Dataframe, filters it, subsequently update
    the result with data filtered with other filters.

    Parameters
    ----------
    df : pd.DataFrame
        Scalar data in oemof-b3 format to filter
    filters : dict of dict
        Several filters to be applied subsequently

    Returns
    -------
    filtered : pd.DataFrame
    """
    assert isinstance(filters, dict)
    for value in filters.values():
        assert isinstance(value, dict)

    # Prepare empty dataframe to be updated with filtered data
    filtered_updated = pd.DataFrame(columns=HEADER_B3_SCAL)
    filtered_updated.index.name = "id_scal"

    for iteration, filter in filters.items():
        print(f"Applying set of filters no {iteration}.")

        # Apply set of filters
        filtered = multi_filter_df(df, **filter)

        # Update result with new filtered data
        filtered_updated = merge_a_into_b(
            filtered,
            filtered_updated,
            how="outer",
            on=["name", "region", "carrier", "tech", "var_name"],
            verbose=False,
        )

        # inform about filtering updating
        print(f"Updated data with data filtered by {filter}")

    return filtered_updated


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


def aggregate_data(df, groupby, agg_method=None):
    r"""
    This functions aggregates data in oemof-B3-resources format and sums up
    by region, carrier, tech or type.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame in oemof-B3-resources format.
    groupby : list
        The columns to group df by
    agg_method : dict
        Dictionary to specify aggregation method.

    Returns
    -------
    df_aggregated : pd.DataFrame
        Aggregated data.
    """
    # Groupby and aggregate
    return df.groupby(groupby, sort=False, dropna=False).agg(agg_method)


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

    _df = format_header(_df, HEADER_B3_SCAL, "id_scal")

    if not isinstance(columns_to_aggregate, list):
        columns_to_aggregate = [columns_to_aggregate]

    # Define the columns that are split and thus not aggregated
    groupby = ["scenario_key", "carrier", "region", "tech", "type", "var_name"]

    groupby = list(set(groupby).difference(set(columns_to_aggregate)))

    # Define how to aggregate if
    if not agg_method:
        agg_method = {
            "var_value": sum,
            "name": lambda x: "None",
            "var_unit": aggregate_units,
        }

    df_aggregated = aggregate_data(df, groupby, agg_method)

    # Assign "ALL" to the columns that where aggregated.
    for col in columns_to_aggregate:
        df_aggregated[col] = "All"

    # Reset the index
    df_aggregated.reset_index(inplace=True)

    df_aggregated = format_header(df_aggregated, HEADER_B3_SCAL, "id_scal")

    return df_aggregated


def aggregate_timeseries(df, columns_to_aggregate, agg_method=None):
    r"""
    This functions aggregates timeseries data in oemof-B3-resources format and sums up
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

    _df = format_header(_df, HEADER_B3_TS, "id_ts")
    _df.series = _df.series.apply(lambda x: np.array(x))

    if not isinstance(columns_to_aggregate, list):
        columns_to_aggregate = [columns_to_aggregate]

    # Define the columns that are split and thus not aggregated
    groupby = [
        "scenario_key",
        "region",
        "var_name",
        "timeindex_start",
        "timeindex_stop",
        "timeindex_resolution",
    ]

    groupby = list(set(groupby).difference(set(columns_to_aggregate)))

    # Define how to aggregate if
    if not agg_method:
        agg_method = {
            "series": sum_series,
            "var_unit": aggregate_units,
        }

    df_aggregated = aggregate_data(_df, groupby, agg_method)

    # Assign "ALL" to the columns that where aggregated.
    for col in columns_to_aggregate:
        df_aggregated[col] = "All"

    # Reset the index
    df_aggregated.reset_index(inplace=True)

    df_aggregated = format_header(df_aggregated, HEADER_B3_TS, "id_ts")

    return df_aggregated


def expand_regions(scalars, regions, where="ALL"):
    r"""
    Expects scalars in oemof_b3 format (defined in ''oemof_b3/schema/scalars.csv'') and regions.
    Returns scalars with new rows included for each region in those places where region equals
    `where`.

    Parameters
    ----------
    scalars : pd.DataFrame
        Data in oemof_b3 format to expand
    regions : list
        List of regions
    where : str
        Key that should be expanded
    Returns
    -------
    sc_with_region : pd.DataFrame
        Data with expanded regions in oemof_b3 format
    """
    _scalars = format_header(scalars, HEADER_B3_SCAL, "id_scal")

    sc_with_region = _scalars.loc[scalars["region"] != where, :].copy()

    sc_wo_region = _scalars.loc[scalars["region"] == where, :].copy()

    if sc_wo_region.empty:
        return sc_with_region

    for region in regions:
        regionalized = sc_wo_region.copy()

        regionalized["name"] = regionalized.apply(
            lambda x: "-".join([region, x["carrier"], x["tech"]]), 1
        )

        regionalized["region"] = region

        sc_with_region = pd.concat([sc_with_region, regionalized])

    sc_with_region = sc_with_region.reset_index(drop=True)

    sc_with_region.index.name = "id_scal"

    return sc_with_region


def merge_a_into_b(df_a, df_b, on, how="left", indicator=False, verbose=True):
    r"""
    Writes scalar data from df_a into df_b, according to 'on'. Where df_a provides no data,
    the values of df_b are used. If how='outer', data from df_a that is not in df_b will be
    kept.

    Parameters
    ----------
    df_a : pd.DataFrame
        DataFrame in oemof_b3 scalars format
    df_b : pd.DataFrame
        DataFrame in oemof_b3 scalars format
    on : list
        List of columns to merge on
    how : str
        'left' or 'outer'. Default: 'left'
    indicator : bool
        If True, an indicator column is included. Default: False

    Returns
    -------
    merged : pd.DataFrame
        DataFrame in oemof_b3 scalars format.
    """
    _df_a = df_a.copy()
    _df_b = df_b.copy()

    # save df_b's index name and column order
    df_b_index_name = _df_b.index.name
    df_b_columns = list(_df_b.columns)
    if indicator:
        df_b_columns.append("_merge")

    # Give some information on how the merge affects the data
    set_index_a = set(map(tuple, pd.Index(_df_a.loc[:, on].replace(np.nan, "NaN"))))
    set_index_b = set(map(tuple, pd.Index(_df_b.loc[:, on].replace(np.nan, "NaN"))))

    if verbose:
        a_not_b = set_index_a.difference(set_index_b)
        if a_not_b:
            if how == "left":
                print(
                    f"There are {len(a_not_b)} elements in df_a but not in df_b"
                    f" and are lost (choose how='outer' to keep them): {a_not_b}"
                )
            elif how == "outer":
                print(
                    f"There are {len(a_not_b)} elements in df_a that are"
                    f" added to df_b: {a_not_b}"
                )

        a_and_b = set_index_a.intersection(set_index_b)
        print(f"There are {len(a_and_b)} elements in df_b that are updated by df_a.")

        b_not_a = set_index_b.difference(set_index_a)
        print(
            f"There are {len(b_not_a)} elements in df_b that are unchanged: {b_not_a}"
        )

    # Merge a with b, ignoring all data in b
    merged = _df_b.drop(columns=_df_b.columns.drop(on)).merge(
        _df_a,
        on=on,
        how=how,
        indicator=indicator,
        sort=False,
    )

    merged.index.name = df_b_index_name

    # Where df_a contains no data, use df_b
    merged = merged.reset_index().set_index(
        on
    )  # First reset, then set index to keep it as a column

    merged.update(_df_b.set_index(on), overwrite=False)

    # Set original index and recover column order
    merged = merged.reset_index().set_index(df_b_index_name)

    merged = merged[df_b_columns]

    return merged


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
        df_stacked = pd.concat([df_stacked, df_stacked_column], ignore_index=True)

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
        ["scenario_key", "name", "region", "carrier", "tech", "type", "var_name"]
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


def round_setting_int(df, decimals):
    r"""
    Rounds the columns of a DataFrame to the specified decimals. For zero decimals,
    it changes the dtype to Int64. Tolerates NaNs.
    """
    _df = df.copy()

    for col, dec in decimals.items():
        if col not in _df.columns:
            print(f"No column named '{col}' found when trying to round.")
            continue
        elif dec == 0:
            dtype = "Int64"
        else:
            dtype = float

        _df[col] = pd.to_numeric(_df[col], errors="coerce").round(dec).astype(dtype)

    return _df


def prepare_b3_timeseries(df_year, **kwargs):
    """
    This function takes time series in column format, stacks them, assigns
    values to additional columns and formats the header in order to prepare data in a b3 time
    series format

    Parameters
    ----------
    df_year : pd.Dataframe
        DataFrame with total normalized data in year to be processed
    kwargs : Additional keyword arguments
        time series data (region, scenario key and unit)

    Returns
    -------
    df_stacked : pd.DataFrame
         DataFrame that contains stacked time series

    """
    # Stack time series with data of a year
    df_year_stacked = stack_timeseries(df_year)

    # Add region, scenario key and unit to stacked time series
    for key, value in kwargs.items():
        df_year_stacked[key] = value

    # Make sure that header is in correct format
    df_year_stacked = format_header(df_year_stacked, HEADER_B3_TS, "id_ts")

    return df_year_stacked


def _get_component_id_in_tuple(oemof_tuple, delimiter="-"):
    r"""
    Returns the id of the component in an oemof tuple.
    If the component is first in the tuple, will return 0,
    if it is second, 1.

    Parameters
    ----------
    oemof_tuple : tuple
        tuple of the form (node, node) or (node, None).

    Returns
    -------
    component_id : int
        Position of the component in the tuple
    """
    return max(enumerate(oemof_tuple), key=lambda x: len(x[1].split(delimiter)))[0]


def _get_component_from_tuple(tuple, delimiter="-"):
    # TODO: This is a dummy implementation that can easily fail
    return max(tuple, key=lambda x: len(x.split(delimiter)))


def _get_direction(oemof_tuple):
    comp_id = _get_component_id_in_tuple(oemof_tuple)

    directions = {
        0: "out",
        1: "in",
    }

    other_id = {
        0: 1,
        1: 0,
    }[comp_id]

    if oemof_tuple[other_id] == "nan":
        return ""
    else:
        return directions[comp_id]


def _get_region_carrier_tech_from_component(component, delimiter="-"):

    if isinstance(component, oemof.tabular.facades.Facade):
        region = component.region
        carrier = component.carrier
        tech = component.tech

    elif isinstance(component, str):
        split = component.split(delimiter)

        if len(split) == 3:
            region, carrier, tech = split

        if len(split) > 3:

            region, carrier, tech = "-".join(split[:2]), *split[2:]
            warnings.warn(
                f"Could not get region, carrier and tech by splitting "
                f"component name into {split}. Assumed region='{region}', "
                f"carrier='{carrier}', tech='{tech}'"
            )

    return region, carrier, tech


def oemof_results_ts_to_oemof_b3(df):
    r"""
    Transforms data in oemof-tabular/oemoflex format to stacked b3 timeseries format.

    Parameters
    ----------
    df : pd.DataFrame
        Time series in oemof-tabular/oemoflex format.

    Returns
    -------
    df : pd.DataFrame
        Time series in oemof-tabular/oemoflex format.
    """
    _df = df.copy()

    # The columns of oemof results are multiindex with 3 levels: (from, to, type).
    # This is mapped to var_name = <type>_<in/out> with "in" if bus comes first (from),
    # "out" if bus is second (to). If the multiindex entry is of the form (component, None, type),
    # then var_name = type
    component = df.columns.droplevel(2).map(_get_component_from_tuple)

    # specify direction in var_name
    direction = df.columns.droplevel(2).map(_get_direction)

    var_name = df.columns.get_level_values(2)

    var_name = list(zip(var_name, direction))

    var_name = list(map(lambda x: "_".join(filter(None, x)), var_name))

    # Introduce arbitrary unique columns before stacking.
    _df.columns = range(len(_df.columns))

    _df = stack_timeseries(_df)

    # assign values to other columns
    _df["region"], _df["carrier"], _df["tech"] = zip(
        *component.map(_get_region_carrier_tech_from_component)
    )

    _df["name"] = component

    _df["var_name"] = var_name

    # ensure that the format follows b3 schema
    _df = format_header(_df, HEADER_B3_TS, "id_ts")

    return _df


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
        assert not data.isna().all(), "Cannot append all NaN data."

        _df = data.copy()

        if isinstance(_df, pd.Series):
            _df.name = var_name

            _df = pd.DataFrame(_df)

        _df = stack_var_name(_df)

        _df = format_header(_df, HEADER_B3_SCAL, "id_scal")

        self.scalars = pd.concat([self.scalars, _df])
