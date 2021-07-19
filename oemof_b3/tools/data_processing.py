import pandas as pd
import numpy as np


def check_consistency_timeindex(df, index, name):
    """
    This function assert that values of a column in a stacked DataFrame are same
    for all time steps

    Parameters
    ----------
    index : string
        Index of values to be checked in the DataFrame
    name : string
        Descriptive name of the index

    Returns
    -------
    value : string
        Single value of the series of duplicates

    """
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
            f"No frequency of your provided data could be detected."
            f"Please provide a DataFrame with a specific frequency (eg. 'H' or 'T')."
        )
    else:
        _df_freq = pd.infer_freq(_df.index)
    if _df.index.freqstr is None:
        raise Warning(
            f"The frequency of your data is not specified in the DataFrame, "
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

    for column in df.columns:
        var_name = column
        timeindex_start = df[column].index.values[0]
        timeindex_stop = df[column].index.values[len(df[column]) - 1]
        timeindex_resolution = df[column].index.freqstr
        series = [pd.Series(df[column].values)]

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

    return df_stacked


def unstack_timeseries(df):
    _df = df.copy()

    # Assert that frequency match for all time steps
    frequency = check_consistency_timeindex(_df, "timeindex_resolution", "frequency")
    timeindex_start = check_consistency_timeindex(_df, "timeindex_start", "start date")
    timeindex_stop = check_consistency_timeindex(_df, "timeindex_stop", "end date")

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

    return df_unstacked
