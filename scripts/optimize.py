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
from oemof_b3.config import config


def get_emission_limit(scalars):
    """Reads emission limit from csv file in `preprocessed`."""
    emission_df = scalars.loc[scalars["carrier"] == "emission"].set_index("var_name")

    # drop row if `var_value` is None
    drop_indices = emission_df.loc[emission_df.var_value == "None"].index
    emission_df.drop(drop_indices, inplace=True)

    # return None if no emission limit is given ('None' or entry missing)
    if emission_df.empty:
        print("No emission limit set.")
        return None
    else:
        limit = emission_df.at["emission_limit", "var_value"]
        print(f"Emission limit set to {limit}.")
        return limit


def get_additional_scalars():
    """Returns additional scalars as pd.DataFrame or None if file does not exist"""
    filename_add_scalars = os.path.join(preprocessed, "additional_scalars.csv")
    if os.path.exists(filename_add_scalars):
        scalars = dp.load_b3_scalars(filename_add_scalars)
        return scalars
    else:
        return None


if __name__ == "__main__":
    preprocessed = sys.argv[1]

    optimized = sys.argv[2]

    logfile = sys.argv[3]
    logger = config.add_snake_logger(logfile, "optimize")

    filename_metadata = "datapackage.json"

    solver = "cbc"

    # get additional scalars
    additional_scalars = get_additional_scalars()
    if additional_scalars is not None:
        emission_limit = get_emission_limit(additional_scalars)

    if not os.path.exists(optimized):
        os.mkdir(optimized)

    try:
        es = EnergySystem.from_datapackage(
            os.path.join(preprocessed, filename_metadata),
            attributemap={},
            typemap=TYPEMAP,
        )

        # create model from energy system (this is just oemof.solph)
        m = Model(es)

        # Add an emission constraint
        if additional_scalars is not None:  # only then `emission_limit` exists
            if emission_limit is not None:
                constraints.emission_limit(m, limit=emission_limit)

        # select solver 'gurobi', 'cplex', 'glpk' etc
        m.solve(solver=solver)
    except:  # noqa: E722
        logger.exception(
            f"Could not optimize energysystem for datapackage from '{preprocessed}'."
        )
        raise

    else:
        # get results from the solved model(still oemof.solph)
        es.meta_results = processing.meta_results(m)
        es.results = processing.results(m)
        es.params = processing.parameter_as_dict(es)

        # dump the EnergySystem
        es.dump(optimized)
