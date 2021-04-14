import os
import sys

import pandas as pd
# DONT REMOVE THIS LINE!
# pylint: disable=unused-import
from oemof.tabular import datapackage  # noqa
from oemof.tabular.facades import TYPEMAP
from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.tools.helpers import load_yaml

if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    destination = sys.argv[2]

    scenario_specs = load_yaml(scenario_specs)

    datetimeindex = (pd.date_range(start="2019-01-01", freq="H", periods=8760),)

    print(scenario_specs)
    keys = ["busses", "select_components", "select_regions", "select_links"]

    extra_kwargs = {}
    for key in keys:
        if key in scenario_specs:
            extra_kwargs[key] = scenario_specs[key]


    # setup default structure
    edp = EnergyDataPackage.setup_default(
        # TODO: Pass scenario specs.
        name='simple_model',
        basepath=preprocessed,
        datetimeindex=pd.date_range("1/1/2016", periods=24 * 10, freq="H"),
        components=[
            'ch4-boiler',
            'heat-demand'
        ],
        busses=[
            'ch4',
            'heat',
        ],
        regions=['A', 'B'],
        links=['A-B'],
    )

    # save to csv
    edp.to_csv_dir(preprocessed)

    # add metadata
    edp.infer_metadata()

    create_default_data(
        destination=destination, datetimeindex=datetimeindex, **extra_kwargs
    )
