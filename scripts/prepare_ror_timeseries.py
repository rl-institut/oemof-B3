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
import numpy as np
import pandas as pd

if __name__ == "__main__":
    #ror_raw = sys.argv[1]  # path to raw ror data

    ror_raw = r"\\FS01\RL-Institut\04_Projekte\305_UMAS_Gasspeicher\03-Projektinhalte\Daten\raw\time_series\DIW_Hydro_availability.csv"
    ror_raw = r"\\FS01\RL-Institut\04_Projekte\305_UMAS_Gasspeicher\03-Projektinhalte\Daten\raw\time_series\DIW_Hydro_availability.csv"
    df = pd.read_csv(ror_raw, index_col=0, skiprows=3, delimiter=";")
    print(df)
    df2 = df.reindex(pd.date_range("2019-01-01 00:00:00", "2019-12-31 23:00:00", 8760))
    print(df2)
    x = dp.stack_timeseries(df2)
    print(x)
