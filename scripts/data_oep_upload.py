from oem2orm import oep_oedialect_oem2orm as oem2orm
import os
import pandas as pd
import getpass

# imports for metadata upload
import json
import requests

### Setting up the oem2orm logger
''' If you want to see detailed runtime information on oem2orm functions or if errors occur, you can activate the logger with this simple setup function. '''
# oem2orm.setup_logger()

# To connect to the OEP you need your OEP Token and user name. Note: You ca view your token on your OEP profile page after [logging in](https://openenergy-platform.org/user/login/?next=/). The following command will prompt you for your token and store it as an environment variable. When you paste it here, it will only show dots instead of the actual string.
# save user name & token in environment as OEP_TOKEN & OEP_USER

db = oem2orm.setup_db_connection()

### Creating sql tables from oemetadata
"""
The oemetadata format is a standardised json file format and required for all data uploaded to the OEP. It includes the data model and the used data types. This allows us to derive the necessary tables in sqlalchemy from it.
In order to create the table(s) we need to tell python where to find our oemetadata file first. To do this we place them in the folder "metadata" which is in the current directory (Path of this jupyter notebbok). Provide the path to your own folder if you want to use your own metadata. oem2orm will process all files that are located in the folder.
"""

metadata_folder = oem2orm.select_oem_dir(oem_folder_name="metadata")

# The next command will set up the table. The collect_tables_function collects all metadata files in a folder and retrives the SQLAlchemy ORM objects and returns them. The Tables are ordered by foreign key. Having a valid metadata strings is necessary for the following steps.
tables_orm = oem2orm.collect_tables_from_oem(db, metadata_folder)

# create table
oem2orm.create_tables(db, tables_orm)

#%debug

## Writing data into a table
'''
In this example we will upload data from a csv file. Pandas has a read_csv function which makes importing a csv-file rather comfortable. It reads csv into a DataFrame. By default, it assumes that the fields are comma-separated. Our example file has columns with semicolons as separators, so we have to specify this when reading the file.
The example file for this tutorial ('upload_tutorial_example_data.csv') is in the 'data' directory, next to this tutorial. Make sure to adapt the path to the file you're using if your file is located elsewhere.
'''

filepath = "./metadata/"

list_filenames = os.listdir(filepath)

files = [filename.split(".")[0] for filename in list_filenames]

print('This files will be uploaded \n')
print(*files, sep="\n")

for file in files:

    print(f'{file} is processed')

    filepath = f"./csv/{file}.csv"
    data_upload_df = pd.read_csv(filepath, encoding='utf8', sep=';')

    data_upload_df = data_upload_df.where(pd.notnull(data_upload_df), None)

    # We need to define the location in the OEDB where the data should be written to. The connection information is still available from our steps above

    schema = "model_draft"
    table_name = f"{file}"
    connection = db.engine

    # The following command will write the content of your dataframe to the table on the OEP that was created earlier.<br>
    # Have a look in the OEP after it ran succesfully!

    print(f'{file} is written into table')

    try:

        data_upload_df.to_sql(table_name, connection, schema=schema, if_exists='append', index=False)

        print('Inserted data to ' + schema + '.' + table_name)
    except Exception as e:
        print(e)
        print('Writing to ' + table_name + ' failed!')
        print('Note that you cannot load the same data into the table twice. There will be an id conflict.')
        print('Delete and recreate with the commands above, if you want to test your upload again.')

    print(f'{file} writing into table ended')
    ## Writing metadata to the table
    # Now that we have data in our table it's high time, that we attach our metadata to it. Since we're using the api, some direct http-requests and a little helper function from the oep-client, we need to import these new dependencies.

    # We use the metadata folder we set up before. (See the Creating tables section)
    # If you wan´t to set another folder use the code below:

    # oem_path = oem2orm.select_oem_dir(oem_folder_name="metadata")
    md_file_name = f"{file}.json"

    # First we're reading the metadata file into a json dictionary.

    print(f'{file} read metadata')

    metadata = oem2orm.mdToDict(oem_folder_path=metadata_folder, file_name=md_file_name)

    # Then we need to validate the metadata.

    # print(f'{file} metadata validation')

    oem2orm.omi_validateMd(metadata)

    # Now we can upload the metadata.

    # print(f'{file} metadata upload')

    oem2orm.api_updateMdOnTable(metadata)