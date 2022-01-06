import os
import sys

from oemof.solph import EnergySystem, Model
from oemof.outputlib import processing

# DONT REMOVE THIS LINE!
# pylint: disable=unusedimport
from oemof.tabular import datapackage  # noqa
from oemof.tabular.facades import TYPEMAP


SOLVER = "cbc"
RECEIVE_DUALS = True
FILENAME_METADATA = "datapackage.json"


if __name__ == "__main__":
    preprocessed = sys.argv[1]

    optimized = sys.argv[2]

    if not os.path.exists(optimized):
        os.mkdir(optimized)

    es = EnergySystem.from_datapackage(
        os.path.join(preprocessed, FILENAME_METADATA), attributemap={}, typemap=TYPEMAP
    )

    # create model from energy system (this is just oemof.solph)
    m = Model(es)

    # tell the model to get the dual variables when solving
    if RECEIVE_DUALS:
        m.receive_duals()

    # solve
    m.solve(solver=SOLVER)

    # get the results from the the solved model(still oemof.solph)
    es.meta_results = processing.meta_results(m)
    es.results = processing.results(m)
    es.params = processing.parameter_as_dict(es)

    # now we use the write results method to write the results in oemoftabular
    # format
    es.dump(optimized)
