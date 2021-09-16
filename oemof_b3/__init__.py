import os
from collections import OrderedDict

import pandas as pd
from oemoflex.tools.helpers import load_yaml

dir_name = os.path.abspath(os.path.dirname(__file__))

labels_dict = load_yaml(os.path.join(dir_name, "config", "labels.yml"))

colors_csv = pd.read_csv(
    os.path.join(dir_name, "config", "colors.csv"), header=[0], index_col=[0]
)

colors_csv = colors_csv.T
colors_odict = OrderedDict()
for i in colors_csv.columns:
    colors_odict[i] = colors_csv.loc["Color", i]
