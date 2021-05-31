import os
import sys

from oemof.solph import EnergySystem, Model

# DONT REMOVE THIS LINE!
# pylint: disable=unused-import
from oemof.tabular import datapackage  # noqa
from oemof.tabular.facades import TYPEMAP

# select scenario
scenario_names = [
    'simple_model',
    'simple_model_1',
    'simple_model_2',
]

try:
    scenario_name = sys.argv[1]

except IndexError:
    raise IndexError("Please pass scenario name.")

assert scenario_name in scenario_names, f"Scenario '{scenario_name}' not found. Please select one" \
                                        f" of the defined scenarios ({scenario_names})."

# define directories
here = os.path.abspath(os.path.dirname(__file__))

preprocessed = os.path.join(here, scenario_name, "preprocessed", scenario_name)

optimized = os.path.join(here, scenario_name, "optimized")

if not os.path.exists(optimized):
    os.mkdir(optimized)

# create an EnergySystem
print("Creating EnergySystem from Datapackage.")
es = EnergySystem.from_datapackage(
    os.path.join(preprocessed, "datapackage.json"),
    attributemap={},
    typemap=TYPEMAP,
)

# create model from energy system (this is just oemof.solph)
print("Creating optimization model from EnergySystem.")
m = Model(es)

# select solver 'gurobi', 'cplex', 'glpk' etc
print("Solving optimization model.")
m.solve(solver="cbc")

# get the results from the the solved model(still oemof.solph)
es.results = m.results()

# dump the optimization results
print("Saving the EnergySystem with results.")
es.dump(optimized)
