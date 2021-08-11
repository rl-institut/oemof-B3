import os
import ast
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


def load_scalars(path):
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
    # Get header of scalars
    scalars_header = get_optional_required_header("scalars")
    header = scalars_header[0]
    optional_header = scalars_header[1]
    required_header = scalars_header[2]

    # Get file name
    filename = os.path.splitext(path)[0]

    # Read data
    df = pd.read_csv(path)

    # Save header of DataFrame to variable
    df_header = list(df.columns)

    # Check whether required columns are missing in the DataFrame
    missing_required = []
    for required in required_header:
        if required not in df_header:
            # Add required columns, that are missing, to a list
            missing_required.append(required)

    # Interrupt if required columns are missing and print all affected columns
    if len(missing_required) > 0:
        raise KeyError(
            f"The data in {filename} is missing the required column(s): {missing_required}"
        )

    # Check whether optional columns are missing
    for optional in optional_header:
        if optional not in df_header:
            # ID in the form of numbering is added if "id_scal" is missing
            if optional is optional_header[0]:
                df[optional] = np.arange(0, len(df))
            else:
                # For every other optional column name, an empty array is added with the name as
                # header - A user info is printed
                df[optional] = [np.nan] * len(df["var_value"])
                print(
                    f"User info: The data in {filename} is missing the optional column: {optional}."
                    f"An empty column named {optional} is added automatically to the DataFrame."
                )

    # Sort the DataFrame to match the header of the template
    df = df[header]

    return df


def load_timeseries(path):
    """
    This function loads a time series from a csv file

    A stacked and non-stacked time series can be passed.
    If a non-stacked time series is passed, it will be stacked in this function.

    Parameters
    ----------
    path : str
        path of input file of csv format

    Returns
    -------
    df : pd.DataFrame
        DataFrame with loaded time series

    """
    # Get header of time series
    timeseries_header = get_optional_required_header("timeseries")
    header = timeseries_header[0]
    optional_header = timeseries_header[1]
    required_header = timeseries_header[2]

    # Read smaller set of data to check its format
    df = pd.read_csv(path, nrows=3)

    # Check if the format matches the one from the results
    # It has a multiIndex with "from", "to", "type" and "timeindex"
    if (
        "from" in df.columns
        and df["from"][0] == "to"
        and df["from"][1] == "type"
        and df["from"][2] == "timeindex"
    ):
        # As a work around for the multiIndex these four lines are combined in one header
        # The convenion is the following:
        # <type> from <from> to <to>
        # E.g.: flow from BB-biomass-st to BB-electricity
        df_columns = []
        for index, col in enumerate(df.columns):
            # First column is the datetime column with the name timeindex
            if index == 0:
                df_columns.append("timeindex")
            # Assign new header of above mentioned format for each column
            else:
                df_columns.append(df[col][1] + " from " + col + " to " + df[col][0])

        # Read the data, which has the format of the results, skipping the multiIndex
        # and adding the assigned header to each column of the data
        df = pd.read_csv(path, skiprows=3)
        for index, col in enumerate(df.columns):
            df.rename(columns={col: df_columns[index]}, inplace=True)

    # Make sure to only stack the DataFrame if it is not stacked already
    stacked = False
    for item in list(df.columns):
        if item in required_header:
            stacked = True

    if not stacked:
        # Convert timeindex column to datetime format
        df["timeindex"] = pd.to_datetime(df[df.columns[0]])
        # In case there is another datetime series with other header than timeindex,
        # it is redundant and deleted
        if df.columns[0] != "timeindex":
            del df[df.columns[0]]
        # Set timeindex as index
        df = df.set_index("timeindex")

        # Stack time series
        df = stack_timeseries(df)

    else:
        # Read data with stacked time series out of a csv
        df = pd.read_csv(path)

        # Save header of DataFrame to variable
        df_header = list(df.columns)

        # Get file name
        filename = os.path.splitext(path)[0]

        # Check whether required columns are missing in the DataFrame
        missing_required = []
        for required in required_header:
            if required not in df_header:
                if "region" not in required:
                    # Add required columns, that are missing, to a list
                    missing_required.append(required)

        # Interrupt if required columns are missing and print all affected columns
        if len(missing_required) > 0:
            raise KeyError(
                f"The data in {filename} is missing the required column(s): {missing_required}"
            )

        # Set timeindex as default name of timeindex_start index
        # This is necessary if DataFrame is to be unstacked afterwards
        df["timeindex_start"].index.name = "timeindex"
        # Convert to datetime format
        df["timeindex_start"] = pd.to_datetime(df["timeindex_start"])
        df["timeindex_stop"] = pd.to_datetime(df["timeindex_stop"])
        # Convert series values from string to list
        for number, item in enumerate(df["series"].values):
            df["series"].values[number] = ast.literal_eval(item)

    # "region" can be extraced from var_name. Therefore a further
    # required header required_header_without_reg is introduced
    required_header_without_reg = required_header.copy()
    required_header_without_reg.remove("region")
    # If optional columns are missing in the stacked DataFrame
    if (
        list(df.columns) == required_header
        or list(df.columns) == required_header_without_reg
    ) and list(df.columns) != header:
        # ID in the form of numbering is added if "id_ts" is missing
        if optional_header[0] not in df.columns:
            df[optional_header[0]] = np.arange(0, len(df))

        # The region is extracted out of "var_name"
        if required_header[0] not in df.columns:
            region = []
            for row in np.arange(0, len(df)):
                # "BE_BB" is added if both "BE" and "BB" in var_name
                if "BE" in df["var_name"][row] and "BB" in df["var_name"][row]:
                    region.append("BE_BB")
                # "BE" is added if "BE" in var_name
                elif "BE" in df["var_name"][row] and "BB" not in df["var_name"][row]:
                    region.append("BE")
                # "BB" is added if "BB" in var_name
                elif "BE" not in df["var_name"][row] and "BB" in df["var_name"][row]:
                    region.append("BB")
                # An error is raised since the region is missing in var_name
                else:
                    raise ValueError(
                        "The data is missing the region."
                        "Please add BB or BE to var_name column"
                    )
            # Add list with region to DataFrame
            df[required_header[0]] = region

        for num_col in np.arange(1, len(optional_header)):
            # For every other optional column name, an empty array is added with the name as
            # header - A user info is printed
            if optional_header[num_col] not in df.columns:
                df[optional_header[num_col]] = [np.nan] * len(df["series"])

    # Sort the DataFrame to match the header of the template
    df = df[header]

    return df


def save_scalars(df, path):
    """
    This funtion saves scalars to a csv file

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with scalars

    path : str
        Path to save the file

    """
    # Save scalars to csv file
    df.to_csv(path, index=False)

    # Print user info
    print(f"User info: The scalars have been saved to: {path}.")


def save_timeseries(df, path):
    """
    This funtion saves a time series to a csv file

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with time series

    path : str
        Path to save the file

    """
    # Save time series to csv file
    df.to_csv(path, index=False)

    # Print user info
    print(f"User info: The time series has been saved to: {path}.")


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
