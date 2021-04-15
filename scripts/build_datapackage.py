import sys

import pandas as pd
from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.tools.helpers import load_yaml

if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    destination = sys.argv[2]

    scenario_specs = load_yaml(scenario_specs)

    datetimeindex = (pd.date_range(start="2019-01-01", freq="H", periods=8760),)

    # setup default structure
    edp = EnergyDataPackage.setup_default(
        basepath=destination,
        datetimeindex=pd.date_range("1/1/2016", periods=24 * 10, freq="H"),
        **scenario_specs,
    )

    # save to csv
    edp.to_csv_dir(destination)

    # add metadata
    edp.infer_metadata()
