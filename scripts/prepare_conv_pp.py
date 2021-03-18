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

from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))

sys.path.append(d)

import oemof_b3.tools.geo as geo


in_path = sys.argv[1] # path to OPSD data
in_path2 = sys.argv[2] # path to geopackage of german regions
out_path = sys.argv[3]

if __name__ == "__main__":
    opsd = pd.read_csv(in_path)
    b3 = opsd[opsd.state.isin(['Brandenburg', 'Berlin'])]
    b3 = b3.copy()
    b3.reset_index(inplace=True, drop=True)

    b3_regions = geo.load_regions_file(in_path2)
    b3 = geo.add_region_to_register(b3, b3_regions)

    # clean up table columns
    b3.drop(b3.loc[b3['status']=='shutdown'].index, inplace = True)
    b3.drop(b3.loc[b3['status'] == 'shutdown_temporary'].index, inplace=True)
    b3.drop(columns=['index_right', 'id_right', 'type_right', 'nuts', 'state_id',
                     'name_bnetza', 'block_bnetza', 'capacity_gross_uba',
                     'name_uba', 'company', 'street', 'postcode', 'city', 'state',
                     'country', 'type_left', 'lat', 'lon', 'eic_code_plant',
                     'eic_code_block', 'network_node', 'voltage', 'network_operator',
                     'efficiency_source', 'shutdown', 'retrofit', 'efficiency_data',
                     'efficiency_estimate', 'commissioned_original', 'energy_source_level_1',
                     'energy_source_level_2', 'energy_source_level_3',
                     'merge_comment', 'comment', 'coordinates'], inplace=True)
    b3.rename(columns={'name': 'region', 'capacity_net_bnetza': 'capacity_net'}, inplace=True)

    # aggregate

    b3.to_excel(out_path, index=False)
    #b3.to_csv(out_path, index=False)
