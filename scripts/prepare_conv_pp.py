r"""
Inputs
-------
in_path : str
    path of input file with raw data

Outputs
---------
out_path : str
    path of output file with prepared data

Description
-------------
The script filters the OPSD conventional power plant package for power plants
in Berlin and Brandenburg. The retrieved data is stored in a new dataframe and
saved as a csv file.
"""

import sys
import pandas as pd

in_path = sys.argv[1]
out_path = sys.argv[2]

if __name__ == '__main__':
    opsd = pd.read_csv(in_path)
    b3 = opsd[opsd.state.isin(['Brandenburg', 'Berlin'])]
    b3.to_csv(out_path, index=False)