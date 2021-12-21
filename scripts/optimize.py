# coding: utf-8
r"""
Inputs
-------
preprocessed : str
    ``results/{scenario}/preprocessed``
optimized : str
    ``results/{scenario}/optimized/``

Outputs
---------
es.dump
    oemof.solph.EnergySystem with results, meta-results and parameters

Description
-------------
Given an EnergyDataPackage, this script creates an oemof.solph.EnergySystem and an
oemof.solph.Model, which is optimized. The EnergySystem with results, meta-results and parameters
is saved.
"""
import os
import sys

from oemof.solph import EnergySystem, Model, constraints
from oemof.outputlib import processing

# DONT REMOVE THIS LINE!
# pylint: disable=unusedimport
from oemof.tabular import datapackage  # noqa
from oemof.tabular.facades import TYPEMAP
from oemof_b3.tools import data_processing as dp

path_scalars = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "raw",
        "base-scenario_emissions_PR70_without_ch4_import.csv",
    )
)  # todo note: this file name should be taken from a central place
scalars = dp.load_b3_scalars(path_scalars)
emission_scalars = scalars.loc[scalars["carrier"] == "emission"].set_index("var_name")
emission_limit = emission_scalars.at["emission_limit", "var_value"]
print(f"################### emission limit {emission_limit} ##############")

if __name__ == "__main__":
    preprocessed = sys.argv[1]

    optimized = sys.argv[2]

    filename_metadata = "datapackage.json"

    solver = "cbc"

    if not os.path.exists(optimized):
        os.mkdir(optimized)

    es = EnergySystem.from_datapackage(
        os.path.join(preprocessed, filename_metadata), attributemap={}, typemap=TYPEMAP
    )

    # create model from energy system (this is just oemof.solph)
    m = Model(es)

    # add constraints
    constraints.emission_limit(m, limit=emission_limit)

    # select solver 'gurobi', 'cplex', 'glpk' etc
    m.solve(solver=solver)

    # get results from the solved model(still oemof.solph)
    es.meta_results = processing.meta_results(m)
    es.results = processing.results(m)
    es.params = processing.parameter_as_dict(es)

    # dump the EnergySystem
    es.dump(optimized)
