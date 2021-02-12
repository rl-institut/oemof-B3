# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 10:40:09 2021

@author: Julius
"""

import sys
import pandas as pd

in_path = sys.argv[1] + '\conventional_power_plants_DE.csv'
out_path = sys.argv[2] + '\processed_conv_pp.csv'

if __name__ == '__main__':
    opsd = pd.read_csv(in_path)
    b3 = opsd[opsd.state.isin(['Brandenburg', 'Berlin'])]
    b3.to_csv(out_path, index=False)
