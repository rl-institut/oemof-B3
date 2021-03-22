r"""
Inputs
-------
in_path1 : str
    path of input file with raw opsd data
in_path2 : str
    path of input file with geodata of regions in Germany
out_path : str
    path of output file with prepared data

Outputs
---------
pandas.DataFrame
    with grouped and aggregated data of conventional power plants in Berlin and Brandenburg.
    Data is grouped by region, energy source, technology and chp capability and contains
    net capacity and efficiency.

Description
-------------
The script filters the OPSD conventional power plant package for power plants
in Berlin and Brandenburg. The retrieved data is stored in a new dataframe, aggregated and
saved as a csv file.
Only operating power plants are considered.
"""
import sys
import pandas as pd
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))

sys.path.append(d)

import oemof_b3.tools.geo as geo


in_path1 = sys.argv[1] # path to OPSD data
in_path2 = sys.argv[2] # path to geopackage of german regions
out_path = sys.argv[3]

if __name__ == "__main__":
    opsd = pd.read_csv(in_path1)
    b3 = opsd[opsd.state.isin(['Brandenburg', 'Berlin'])]
    b3 = b3.copy()
    b3.reset_index(inplace=True, drop=True)

    b3_regions = geo.load_regions_file(in_path2)
    b3 = geo.add_region_to_register(b3, b3_regions)

    # clean up table columns
    b3.drop(b3.loc[b3['status'] == 'shutdown'].index, inplace=True)
    b3.drop(b3.loc[b3['status'] == 'shutdown_temporary'].index, inplace=True)
    b3.drop(b3.loc[b3['status'] == 'reserve'].index, inplace=True)
    b3.drop(columns = b3.columns.difference(['capacity_net_bnetza', 'energy_source', 'technology',
                                             'chp', 'chp_capacity_uba', 'efficiency_estimate' ,'name']), inplace=True)
    b3.rename(columns={'name': 'region', 'capacity_net_bnetza': 'capacity_net_el'}, inplace=True)

    # group and aggregate data by region, energy source, technology and chp capability
    b3_aggS = b3.groupby(['region','energy_source', 'technology', 'chp']).agg({'capacity_net_el': 'sum',
                                                                          'efficiency_estimate': 'mean'})
    b3_agg = pd.DataFrame(b3_aggS)
    b3_agg.reset_index(level=['region', 'energy_source', 'technology', 'chp'], inplace=True)

    b3_agg.to_csv(out_path, index=False)
