import json

from oemof_b3.schema import oemetadata_scal, oemetadata_ts, SCHEMA_SCAL, SCHEMA_TS
from oemof_b3.tools import data_processing as dp


def load_metadata_json_to_dict(filepath):
    with open(filepath, "rb") as f:
        return json.load(f)


def save_metadata_dict_to_json(data, filepath, encoding="utf-8"):
    with open(filepath, "w", encoding=encoding) as f:
        return json.dump(data, f, sort_keys=False, indent=2)


def list_diff(sample, default):
    r"""
    Determines extra and missing items in sample in
    comparison with default.

    Parameters
    ----------
    sample : list
    default : list

    Returns
    -------
    (extra_items, missing_items): (list, list)
    """
    extra_items = dp.get_list_diff(sample, default)

    missing_items = dp.get_list_diff(default, sample)

    if not extra_items and not missing_items:
        return None

    else:
        return (extra_items, missing_items)


def get_suitable_metadata_template(data):
    r"""
    Returns the suitable metadata for your data in b3 format.

    Parameters
    ----------
    data : pd.DataFrame
        Data in b3 schema (scalars or timeseries)
        that you want to create metadata for.

    Returns
    -------
    metadata : dict
        Metadata for scalars or timeseries
    """
    if list_diff(data.columns, SCHEMA_SCAL.columns) is None:
        template = oemetadata_scal
    elif list_diff(data.columns, SCHEMA_TS.columns) is None:
        template = oemetadata_ts
    else:
        raise ValueError("Could not match data with the existing templates.")

    metadata = template.copy()

    return metadata


def upload_df_to_oep_table(df, name, con, schema, logger, if_exists="append", index=False):
    r"""
    Parameters
    ----------
    df : pd.DataFrame
        Data to upload
    name : str
        Name of the table
    con : sqlalchemy.engine.(Engine or Connection) or sqlite3.Connection
    schema : str
        Database schema
    logger : logger
        Logger
    if_exists : str, default=append
    index: boolean, default=False

    Returns
    -------
    None
    """
    try:
        df.to_sql(
            name=name,
            con=con,
            schema=schema,
            if_exists=if_exists,
            index=index,
        )

        logger.info(
            "Inserted data to "
            + schema
            + "."
            + name
        )

    except Exception as e:
        logger.error(e)
        logger.error("Writing to " + name + " failed!")
        logger.error(
            "Note that you cannot load the same data into the table twice."
            " There will be an id conflict."
        )
        logger.error(
            "Delete and recreate with the commands above, if you want to test your"
            " upload again."
        )
