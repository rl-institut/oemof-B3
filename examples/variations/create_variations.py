import os

import pandas as pd

from oemofB3.variations import VariationGen


here = os.path.abspath(os.path.dirname(__file__))

preprocessed_elements = os.path.join(here, 'preprocessed', 'basic_datapackage', 'data')

basis_dp_path = preprocessed_elements

destination = '.'

variations = pd.read_csv('efficiency_variations.csv')

vg = VariationGen(basis_dp_path)

vg.create_variations(variations, destination)