import sys

from datapackage import DataPackage
import pandas as pd

from oemofB3.variations import VariationGen


dp_path = sys.argv[1]

destination = sys.argv[2]

variations = pd.read_csv('efficiency_variations.csv')

# load datapackage
dp = DataPackage(dp_path)

# setup variation generator
vg = VariationGen(dp)

# create variations
vg.create_variations(variations, destination)