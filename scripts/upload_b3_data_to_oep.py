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
This script performs the following steps:

* Setup a database connection with your credentials (can be saved in oemof_b3/config/.secrets.yaml
* Find all csv files in input directory.
* Create metadata for the data
  (in oemetadata format, using the template in ``oemof-B3/schema/oemetadata.json``)
  for given model results (in oemof-B3-format) and saves them locally as json files.
* Create tables on the OpenEnergyPlatform (OEP) based on the metadata.
* Upload data to the OEP tables.
* Validate metadata.
* Upload metadata to the OEP tables.

The oemetadata format is a standardised json file format and is required for all data uploaded to
the OEP. It includes the data model, the used data types, and general information about the data
context. Tables in sqlalchemy are created based on the information in the oemetadata.
"""
from collections import namedtuple
import logging
import os
import pathlib
import sys
from datetime import date

import pandas as pd

from oemof_b3.config import config
from oemof_b3.tools.oep import (
    get_suitable_metadata_template,
    save_metadata_dict_to_json,
    upload_df_to_oep_table,
)

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


# define table names
def get_table_name(name_prefix, filename):
    r"""
    This is the naming convention for tables: Take a prefix,
    make sure that it does not violate SQL table requirements
    and prepend it to the name of the file.
    """
    file_name_wo_extension = os.path.splitext(filename)[0]

    # make scenario name compatible with oep requirements
    # (Names must consist of lowercase alpha-numeric words or underscores
    # and start with a letter and must be have a maximumlength of 50)
    name_prefix = name_prefix.replace("-", "_").lower()

    return f"{name_prefix}_{file_name_wo_extension}"


def get_title(title_prefix):
    r"""
    Because snakemake cannot pass space characters when calling the script
    as 'shell', we have to use underscores and replace them with spaces here.
    """
    return title_prefix.replace("_", " ")


def write_metadata(metadata, schema, name, title, keywords):
    metadata["name"] = name
    metadata["title"] = title
    metadata["PublicationDate"] = str(date.today())
    # TODO: A method metadata.add_resource, add field would be handy
    metadata["resources"][0]["name"] = f"{schema}.{table}"
    metadata["keywords"] = keywords

    return metadata


if __name__ == "__main__":
    filepath = pathlib.Path(sys.argv[1])
    metadata_path = pathlib.Path(sys.argv[2])
    name_prefix = sys.argv[3]
    title_prefix = sys.argv[4]
    logfile = sys.argv[5]

    # set up the logger
    logger = config.add_snake_logger("upload_results_to_oep")

    if not os.path.exists(metadata_path):
        os.makedirs(metadata_path)

    # find data to upload
    UploadCandidate = namedtuple("UploadCandidate", ["filename", "table_name", "title"])

    upload_candidates = [
        UploadCandidate(
            filename=filename,
            table_name=get_table_name(name_prefix, filename),
            title=get_title(title_prefix),
        )
        for filename in os.listdir(filepath)
        if filename.endswith(".csv")
    ]
    logger.info(
        "These files will be uploaded: "
        + ", ".join([uc.filename for uc in upload_candidates])
    )

    # To connect to the OEP you need your OEP Token and user name. Note: You ca view your token
    # on your OEP profile page after
    # [logging in](https://openenergy-platform.org/user/login/?next=/).
    # The following command will prompt you for your token and store it as an environment variable.
    # When you paste it here, it will only show dots instead of the actual string.
    # save user name & token in environment as OEP_TOKEN & OEP_USER
    db = oem2orm.setup_db_connection()

    # Create the metadata and save it
    for filename, table, title in upload_candidates:
        data_upload_df = pd.read_csv(
            os.path.join(filepath, filename), encoding="utf8", sep=";", index_col=0
        )

        metadata = get_suitable_metadata_template(data_upload_df)

        metadata = write_metadata(
            metadata=metadata,
            schema=config.settings.upload_results_to_oep.schema,
            name=table,
            title=title,
            keywords=["RLI", "oemof_b3"],
        )

        metadata_destination = metadata_path / f"{table}.json"

        save_metadata_dict_to_json(metadata, metadata_destination)

        logger.info(f"Saved metadata to: {metadata_destination}")

    # Creating sql tables from oemetadata
    # The next command will set up the tables. The collect_tables-function collects all metadata
    # files in a folder, creates the SQLAlchemy ORM objects and returns them. The tables are
    # ordered by foreign key. Having a valid metadata strings is necessary for the following steps.
    # TODO: Once [this](https://github.com/OpenEnergyPlatform/oem2orm/issues/35) is resolved,
    # we can collect and create single tables and do not have to leave the loop here.
    tables_orm = oem2orm.collect_tables_from_oem(db, metadata_path)

    # create tables
    oem2orm.create_tables(db, tables_orm)

    # Writing data into the tables
    for filename, table, _ in upload_candidates:

        logger.info(f"{filename} is processed")

        data_upload_df = pd.read_csv(
            os.path.join(filepath, filename), encoding="utf8", sep=";"
        )

        data_upload_df = data_upload_df.where(pd.notnull(data_upload_df), None)

        # The following command will write the content of your dataframe to the table on the OEP
        # that was created earlier.
        # Have a look in the OEP after it ran successfully!
        logger.info(f"{filename} is written into table {table}")

        upload_df_to_oep_table(
            df=data_upload_df,
            name=table,
            con=db.engine,
            schema=config.settings.upload_results_to_oep.schema,
            logger=logger,
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
