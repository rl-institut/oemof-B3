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


def add_gas_power_relation_constraints(model, energysystem):
    r"""

    Parameters
    ----------
    model:
    energysystem:

    Returns
    -------

    """
    # loop through busses
    bus_names = ["B-heat_central", "BB-heat_central", "B-heat_decentral", "BB-heat_decentral"]  # todo automate by regions and busses in .yml
    busses = [es.groups[x] for x in bus_names]

    # todo get factor (varies for central/decentral, also for B/BB?)

    for bus in busses:
        region = bus.label.split("-")[0]
        # get gas and electricity powered components depending on bus
        if "decentral" in bus.label:
            heat_pump = energysystem.groups[f"{region}-electricity-heat_pump"]  # todo note: hps missing
            boiler = energysystem.groups[f"{region}-ch4-boiler"]

            # add constraint
            constraints.equate_variables(
                model=model,
                var1=model.InvestmentFlow.invest[heat_pump, bus],
                var2=model.InvestmentFlow.invest[boiler, bus],
                factor1=factor,
            )
        else:
            # electricity components
            heat_pump = energysystem.groups[f"{region}-electricity-heat_pump"]
            res_pth = energysystem.groups[f"{region}-electricity-pth"]
            # gas components
            boiler = energysystem.groups[f"{region}-ch4-boiler"]
            ch4_chp = energysystem.groups[f"{region}-ch4-bpchp"]
            h2_chp = energysystem.groups[f"{region}-h2-bpchp"]

            # add constraint
            constraints.equate_variables(
                model=model,
                var1=model.InvestmentFlow.invest[line12, bus], # todo adding up investment flows
                var2=model.InvestmentFlow.invest[line21, bus],
                factor1=factor,
            )


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

    # add constraints # todo only to be added if factor is given in data
    add_gas_power_relation_constraints(model=m, energysystem=es)

    # select solver 'gurobi', 'cplex', 'glpk' etc
    m.solve(solver=solver)

    # get the results from the the solved model(still oemof.solph)
    es.meta_results = processing.meta_results(m)
    es.results = processing.results(m)
    es.params = processing.parameter_as_dict(es)

    # dump the EnergySystem
    es.dump(optimized)
