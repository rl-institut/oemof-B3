# coding: utf-8
r"""
Inputs
-------
in_path: str
    ``results/{scenario}/b3_results/data``: path to scalar results in oemof-B3-format
out_path: str
    ``results/{scenario}/b3_results/metadata``: path to metadata directory
params:
    ``results/{scenario}/{scenario}.log``: path to logfile

Outputs
---------
``results/{scenario}/b3_results/metadata``: directory with automatically created metadata.

Description
-------------
Creates tables on the OpenEnergyPlatform (OEP) based on related oemetadata. Uploads results data
in oemof_b3-format to the OEP.

The script can delete existing tables on the OEP that have been uploaded with an affiliated OEP user
account.

The oemetadata format is a standardised json file format and is required for all data uploaded to
the OEP. It includes the data model, the used data types, and general information about the data
context. Tables in sqlalchemy are created based on the information in the oemetadata.
"""
import json
import logging
import os
import pathlib
import sys
from datetime import date

import pandas as pd

from oemof_b3.config import config
from oemof_b3.schema import oemetadata_scal, oemetadata_ts, SCHEMA_SCAL, SCHEMA_TS
from oemof_b3.tools import data_processing as dp

try:
    from oem2orm import oep_oedialect_oem2orm as oem2orm
except ImportError:
    raise ImportError("Need to install oem2orm to upload results to OEP.")

logger = logging.getLogger()

# try to get oep_user and oep_token from .secrets.yaml
try:
    os.environ["OEP_USER"] = config.settings.oep_user
    os.environ["OEP_TOKEN"] = config.settings.oep_token
except AttributeError:
    logger.warning(
        "No oep_user and/or oep_token provided in oemof_b3/config/.secrets.yaml. "
        "Will have to type provide them manually when uploading to OEP."
    )


SCHEMA = "model_draft"


def save_dict_to_json(data, filepath, encoding="utf-8"):
    with open(filepath, "w", encoding=encoding) as f:
        return json.dump(data, f, sort_keys=True, indent=2)


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


def create_metadata(data, template=None):
    if template is not None:
        pass
    elif list_diff(data.columns, SCHEMA_SCAL.columns) is None:
        template = oemetadata_scal
    elif list_diff(data.columns, SCHEMA_TS.columns) is None:
        template = oemetadata_ts
    else:
        raise ValueError("Could not match data with the existing templates.")

    metadata = template.copy()

    return metadata


if __name__ == "__main__":
    filepath = pathlib.Path(sys.argv[1])
    metadata_path = pathlib.Path(sys.argv[2])
    logfile = sys.argv[3]

    # set up the logger
    scenario = "scenario"  # TODO: Derive scenario from filepath
    logger = config.add_snake_logger(logfile, "upload_results_to_oep")

    if not os.path.exists(metadata_path):
        os.makedirs(metadata_path)

    # find data to upload
    dict_table_filename = {
        os.path.splitext(filename)[0]: filename for filename in os.listdir(filepath)
    }
    logger.info(
        "These files will be uploaded: " + ", ".join(dict_table_filename.values())
    )

    # To connect to the OEP you need your OEP Token and user name. Note: You ca view your token
    # on your OEP profile page after
    # [logging in](https://openenergy-platform.org/user/login/?next=/).
    # The following command will prompt you for your token and store it as an environment variable.
    # When you paste it here, it will only show dots instead of the actual string.
    # save user name & token in environment as OEP_TOKEN & OEP_USER
    db = oem2orm.setup_db_connection()

    # Create the metadata and save it
    for table, filename in dict_table_filename.items():
        data_upload_df = pd.read_csv(
            os.path.join(filepath, filename), encoding="utf8", sep=";", index_col=0
        )

        metadata = create_metadata(data_upload_df)

        metadata["name"] = f"{scenario}_{table}"

        metadata["PublicationDate"] = str(date.today())

        # TODO: A method metadata.add_resource, add field would be handy
        metadata["resources"][0]["name"] = f"{SCHEMA}.{scenario}_{table}"

        save_dict_to_json(metadata, metadata_path / f"{table}.json")

        logger.info(f"Saved metadata to: {metadata_path}")

    # Creating sql tables from oemetadata
    # The next command will set up the tables. The collect_tables-function collects all metadata
    # files in a folder, creates the SQLAlchemy ORM objects and returns them. The tables are
    # ordered by foreign key. Having a valid metadata strings is necessary for the following steps.
    tables_orm = oem2orm.collect_tables_from_oem(db, metadata_path)

    # create tables
    oem2orm.create_tables(db, tables_orm)

    # Writing data into the tables
    for table, filename in dict_table_filename.items():

        logger.info(f"{filename} is processed")

        data_upload_df = pd.read_csv(
            os.path.join(filepath, filename), encoding="utf8", sep=";"
        )

        data_upload_df = data_upload_df.where(pd.notnull(data_upload_df), None)

        # The following command will write the content of your dataframe to the table on the OEP
        # that was created earlier.
        # Have a look in the OEP after it ran successfully!
        logger.info(f"{filename} is written into table {scenario}_{table}")

        try:
            data_upload_df.to_sql(
                f"{scenario}_{table}",
                con=db.engine,
                schema=SCHEMA,
                if_exists="append",
                index=False,
            )

            logger.info("Inserted data to " + SCHEMA + "." + table)

        except Exception as e:
            logger.error(e)
            logger.error("Writing to " + table + " failed!")
            logger.error(
                "Note that you cannot load the same data into the table twice."
                " There will be an id conflict."
            )
            logger.error(
                "Delete and recreate with the commands above, if you want to test your"
                " upload again."
            )

        logger.info(f"{filename} writing into table ended")

        # Writing metadata to the table
        # Now that we have data in our table, it is time to metadata to it.
        md_file_name = f"{table}.json"

        # First we are reading the metadata file into a json dictionary.
        logger.info(f"{table} read metadata")
        metadata = oem2orm.mdToDict(
            oem_folder_path=metadata_path, file_name=md_file_name
        )

        # Then we need to validate the metadata.
        logger.info(f"{table} metadata validation")
        oem2orm.omi_validateMd(metadata)

        # Now we can upload the metadata.
        logger.info(f"{table} metadata upload")
        oem2orm.api_updateMdOnTable(metadata)
