import os
import sys
import yaml

import pandas as pd

from oemoflex.model.datapackage import EnergyDataPackage

# select scenario
scenario_names = [
    "base",
    "more_renewables",
    "more_renewables_less_fossil",
]

try:
    scenario_name = sys.argv[1]

except IndexError:
    raise IndexError("Please pass scenario name.")

assert scenario_name in scenario_names, (
    f"Scenario '{scenario_name}' not found. Please select one"
    f" of the defined scenarios ({scenario_names})."
)

here = os.path.abspath(os.path.dirname(__file__))

preprocessed = os.path.join(here, scenario_name, "preprocessed", scenario_name)

if not os.path.exists(preprocessed):
    os.makedirs(preprocessed)

with open("extra_components.yaml", "r") as yaml_file:
    extra_components = yaml.load(yaml_file, Loader=yaml.FullLoader)

with open("extra_busses.yaml", "r") as yaml_file:
    extra_busses = yaml.load(yaml_file, Loader=yaml.FullLoader)

# setup default structure
edp = EnergyDataPackage.setup_default(
    name=scenario_name,
    basepath=preprocessed,
    datetimeindex=pd.date_range("1/1/2016", periods=24 * 10, freq="H"),
    regions=["B", "BB"],
    links=["BB-B"],
    busses=["electricity", "ch4", "biomass", "oil", "other"],
    components=[
        "electricity-shortage",
        "electricity-curtailment",
        "electricity-demand",
        "electricity-transmission",
        "wind-onshore",
        "solar-pv",
        "ch4-gt",
        "oil-st",
        "other-st",
        "electricity-liion_battery",
        "biomass-st",
    ],
    bus_attrs_update=extra_busses,
    component_attrs_update=extra_components,
)

# save to csv
edp.to_csv_dir(preprocessed)

# add metadata
edp.infer_metadata()
