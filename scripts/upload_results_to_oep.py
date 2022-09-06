# coding: utf-8
r"""
Inputs
-------

Outputs
---------

Description
-------------
Uploads results data in oemof_b3-format to the OpenEnergyPlatform (OEP).

The oemetadata format is a standardised json file format and required for all data uploaded to
the OEP. It includes the data model and the used data types. This allows us to derive the
necessary tables in sqlalchemy from it.
"""
import os
import sys

import pandas as pd

try:
    from oem2orm import oep_oedialect_oem2orm as oem2orm
except ImportError:
    raise ImportError("Need to install oem2orm to upload results to OEP.")

from oemof_b3.config import config


if __name__ == "__main__":
    filepath = sys.argv[1]  # "./metadata/"
    logfile = sys.argv[2]

    scenario = "scenario"  # TODO: Derive scenario from filepath
    logger = config.add_snake_logger(logfile, "upload_results_to_oep")

    # Setting up the oem2orm logger
    # If you want to see detailed runtime information on oem2orm functions or if errors occur,
    # you can activate the logger with this simple setup function.
    # oem2orm.setup_logger()

    # To connect to the OEP you need your OEP Token and user name. Note: You ca view your token
    # on your OEP profile page after
    # [logging in](https://openenergy-platform.org/user/login/?next=/).
    # The following command will prompt you for your token and store it as an environment variable.
    # When you paste it here, it will only show dots instead of the actual string.
    # save user name & token in environment as OEP_TOKEN & OEP_USER
    db = oem2orm.setup_db_connection()

    # Creating sql tables from oemetadata
    metadata_folder = oem2orm.select_oem_dir(oem_folder_name="metadata")

    # The next command will set up the table. The collect_tables_function collects all metadata
    # files in a folder and retrives the SQLAlchemy ORM objects and returns them. The Tables are
    # ordered by foreign key. Having a valid metadata strings is necessary for the following steps.
    tables_orm = oem2orm.collect_tables_from_oem(db, metadata_folder)

    # create table
    oem2orm.create_tables(db, tables_orm)

    # Writing data into a table
    list_filenames = os.listdir(filepath)

    files = [filename.split(".")[0] for filename in list_filenames]

    logger.info("These files will be uploaded \n")
    logger.info(*files, sep="\n")

    for file in files:

        logger.info(f"{file} is processed")

        filepath = f"./csv/{file}.csv"
        data_upload_df = pd.read_csv(filepath, encoding="utf8", sep=";")

        data_upload_df = data_upload_df.where(pd.notnull(data_upload_df), None)

        # We need to define the location in the OEDB where the data should be written to. The
        # connection information is still available from our steps above
        schema = "model_draft"
        table_name = f"{file}"
        connection = db.engine

        # The following command will write the content of your dataframe to the table on the OEP
        # that was created earlier.<br>
        # Have a look in the OEP after it ran succesfully!
        logger.info(f"{file} is written into table")

        try:
            data_upload_df.to_sql(
                table_name, connection, schema=schema, if_exists="append", index=False
            )

            logger.info("Inserted data to " + schema + "." + table_name)

        except Exception as e:
            logger.error(e)
            logger.error("Writing to " + table_name + " failed!")
            logger.error(
                "Note that you cannot load the same data into the table twice."
                " There will be an id conflict."
            )
            logger.error(
                "Delete and recreate with the commands above, if you want to test your"
                " upload again."
            )

        logger.info(f"{file} writing into table ended")

        # Writing metadata to the table
        # Now that we have data in our table it's high time, that we attach our metadata to it.
        # Since we're using the api, some direct http-requests and a little helper function from
        # the oep-client, we need to import these new dependencies.

        # We use the metadata folder we set up before. (See the Creating tables section)
        # If you wan´t to set another folder use the code below:

        # oem_path = oem2orm.select_oem_dir(oem_folder_name="metadata")
        md_file_name = f"{file}.json"

        # First we're reading the metadata file into a json dictionary.
        logger.info(f"{file} read metadata")

        metadata = oem2orm.mdToDict(
            oem_folder_path=metadata_folder, file_name=md_file_name
        )

        # Then we need to validate the metadata.
        # logger.info(f'{file} metadata validation')
        oem2orm.omi_validateMd(metadata)

        # Now we can upload the metadata.
        # logger.info(f'{file} metadata upload')
        oem2orm.api_updateMdOnTable(metadata)
