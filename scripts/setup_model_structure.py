import sys
import pandas as pd
from oemoflex.model.model_structure import create_default_data
from oemoflex.tools.helpers import load_yaml


if __name__ == "__main__":

    scenario = sys.argv[1]

    destination = sys.argv[2]

    datetimeindex = (pd.date_range(start="2019-01-01", freq="H", periods=8760),)

    scenario_specs = load_yaml(scenario)

    keys = ["busses", "select_components", "select_regions", "select_links"]

    extra_kwargs = {}
    for key in keys:
        if key in scenario_specs:
            extra_kwargs[key] = scenario_specs[key]

    create_default_data(
        destination=destination, datetimeindex=datetimeindex, **extra_kwargs
    )
