import sys

import pandas as pd
from oemof_b3.model.datapackage import DataFramePackage
from oemof_b3.model.variations import VariationGenerator

dp_path = sys.argv[1]

destination = sys.argv[2]

variations = pd.read_csv(
    './examples/variations/efficiency_variations.csv',
    header=[0, 1],
    index_col=0
)

# load datapackage
dp = DataFramePackage.from_csv_dir(dp_path)

# setup variation generator
vg = VariationGenerator(dp)

# create variations
vg.create_variations(variations, destination)
