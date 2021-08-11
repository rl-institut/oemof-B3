import pandas as pd
import numpy as np


def get_optional_required_header(data_type):
    """
    This function returns the header of
    1. scalars and
    2. time series
    along with two lists: optional and required header items

    Parameters
    ----------
    data_type : string
        "scalars" or "timeseries" depending on DataFrame

    Returns
    -------

    """
    if data_type == "scalars":
        # Name of each column in scalars
        header = [
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
        # Names of optional columns in scalars
        optional_header = ["id_scal", "var_unit", "reference", "comment"]

    elif data_type == "timeseries":
        # Names of all columns in a stacked time series
        header = [
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

        # Names of optional columns in a stacked time series
        optional_header = [
            "id_ts",
            # "region",
            "var_unit",
            "source",
            "comment",
        ]
    else:
        raise ValueError(
            f"{data_type} is not a valid option of a description of the DataFrame type. "
            f"Please choose between 'scalars' and 'timeseries'."
        )

    # Names of required columns in scalars
    required_header = header.copy()
    for optional in optional_header:
        required_header.remove(optional)

    return header, optional_header, required_header


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
        series = [pd.Series(_df[column].values)]

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

    # Process values of series
    values_series = []
    for index, row in _df.iterrows():
        values_series.append(row["series"].values)

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
