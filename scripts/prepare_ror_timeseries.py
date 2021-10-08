r"""
Inputs
-------


Outputs
---------


Description
-------------

"""
import sys
import oemof_b3.tools.data_processing as dp
import pandas as pd

if __name__ == "__main__":
    #ror_raw = sys.argv[1]  # path to raw ror data

    ts = r"C:\Users\meinm\Documents\Git\oemof-B3\oemof_b3\schema\timeseries.csv"
    ror_raw = r"..\raw\time_series\DIW_Hydro_availability.csv"

    template = pd.read_csv(ts, index_col=0, delimiter=";")
    df_hydro = pd.read_csv(ror_raw, index_col=0, skiprows=3, delimiter=";")

    df_hydro.index = pd.date_range("2019-01-01 00:00:00", "2019-12-31 23:00:00", 8760)
    df_hydro_stacked = dp.stack_timeseries(df_hydro)

    for region in ["BB", "B"]:
        df_hydro_stacked["region"] = region
        df_hydro_stacked["var_name"] = "hydro-ror-profile"
        df_hydro_stacked["scenario"] = "all"

        df_hydro_stacked = df_hydro_stacked[["scenario","region", "var_name", "timeindex_start", "timeindex_stop", "timeindex_resolution", "series"]]

        df_hydro_stacked["var_unit"] =""
        df_hydro_stacked["source"] = "https://zenodo.org/record/1044463"
        df_hydro_stacked["comment"] = ""

        template = pd.concat([template,df_hydro_stacked])

    template.reset_index(drop=True, inplace=True)
    template.index.name = "id_ts"
    dp.save_df(template, r"..\raw\time_series\timeseries_hydro.csv")


