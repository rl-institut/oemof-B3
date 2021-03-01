import os

from oemof.solph import EnergySystem, Model

# DONT REMOVE THIS LINE!
# pylint: disable=unused-import
from oemof.tabular import datapackage  # noqa
from oemof.tabular.facades import TYPEMAP


here = os.path.abspath(os.path.dirname(__file__))

name = "simple_model"

preprocessed = os.path.join(here, "preprocessed", name)

optimized = os.path.join(here, "optimized")

if not os.path.exists(optimized):
    os.mkdir(optimized)

es = EnergySystem.from_datapackage(
    os.path.join(preprocessed, "datapackage.json"),
    attributemap={},
    typemap=TYPEMAP,
)

# create model from energy system (this is just oemof.solph)
m = Model(es)

# select solver 'gurobi', 'cplex', 'glpk' etc
m.solve(solver="cbc")

# get the results from the the solved model(still oemof.solph)
es.results = m.results()

# now we use the write results method to write the results in oemof-tabular
# format
es.dump(optimized)
