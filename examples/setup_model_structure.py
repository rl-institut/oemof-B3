import os
import sys

import pandas as pd

from oemoflex.model.datapackage import EnergyDataPackage

# select scenario
scenario_names = [
    "simple_model",
    "simple_model_1",
    "simple_model_2",
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

# setup default structure
edp = EnergyDataPackage.setup_default(
    name=scenario_name,
    basepath=preprocessed,
    datetimeindex=pd.date_range("1/1/2016", periods=24 * 10, freq="H"),
    regions=["BB", "BE"],
    links=["BB-BE"],
    busses=["electricity", "ch4"],
    components=[
        "electricity-shortage",
        "electricity-curtailment",
        "electricity-demand",
        "electricity-transmission",
        "wind-onshore",
        "solar-pv",
        "ch4-gt",
        # "oil-st",
        # "other-st",
        "electricity-liion_battery",
        # "biomass-st",
    ],
)

# save to csv
edp.to_csv_dir(preprocessed)

# add metadata
edp.infer_metadata()
