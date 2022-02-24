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
oemof.solph.Model, which is optimized.
The following constraints are added:
- `emission_limit`: maximum amount of emissions
- `equate_flows_by_keyword`: gas-power relation is set. This constraint is only added if
    'electricity_gas_relation' is added to the scalars. To use this constraint you need to copy
    [`equate_flows.py`](https://github.com/oemof/oemof-solph/blob/features/equate-flows/src/oemof/solph/constraints/equate_variables.py)
    of oemof.solph into `/tools` directory of `oemof-B3`.
The EnergySystem with results, meta-results and parameters is saved.

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
from oemof_b3.tools.equate_flows import equate_flows_by_keyword

# global variables
EL_GAS_RELATION = "electricity_gas_relation"
EMISSION_LIMIT = "emission_limit"
EL_KEY = "electricity"  # prefix of keywords for gas electricity relation
GAS_KEY = "gas"  # prefix of keywords for gas electricity relation


def drop_values_by_keyword(df, keyword="None"):
    """drops row if `var_value` is None"""
    drop_indices = df.loc[df.var_value == keyword].index
    df.drop(drop_indices, inplace=True)
    return df


def get_emission_limit(scalars):
    """Gets emission limit from scalars and returns None if it is missing or None."""
    emission_df_raw = scalars.loc[scalars["carrier"] == "emission"].set_index(
        "var_name"
    )
    emission_df = drop_values_by_keyword(emission_df_raw)

    # return None if no emission limit is given ('None' or entry missing)
    if emission_df.empty:
        print("No emission limit set.")
        return None
    else:
        limit = emission_df.at[EMISSION_LIMIT, "var_value"]
        print(f"Emission limit set to {limit}.")
        return limit


def get_electricity_gas_relations(scalars):
    r"""
    Gets electricity/gas relations from scalars. Returns None if no relations are given.

    Returns
    -------
    pd.DataFrame
        Contains rows of scalars with 'var_name' `EL_GAS_RELATION`
    If no factor is given returns None.
    """
    relations_raw = scalars.loc[scalars.var_name == EL_GAS_RELATION]
    # drop relations that are None
    relations = drop_values_by_keyword(relations_raw)
    if relations.empty:
        print("No gas electricity relation is set.")
        return None
    else:
        busses = relations.carrier.drop_duplicates().values
        print(f"Gas electricity relations are set for busses: {busses}")
        return relations


def add_electricity_gas_relation_constraints(model, relations):
    r"""
    Adds constraint `equate_flows_by_keyword` to `model`.
    """
    for index, row in relations.iterrows():
        suffix = f"{row.carrier.split('_')[1]}-{row.region}"
        equate_flows_by_keyword(
            model=model,
            keyword1=f"{EL_KEY}_{suffix}",
            keyword2=f"{GAS_KEY}_{suffix}",
            factor1=row.var_value,
        )


if __name__ == "__main__":
    preprocessed = sys.argv[1]

    optimized = sys.argv[2]

    filename_metadata = "datapackage.json"

    solver = "cbc"

    # get additional scalars containing emission limit and gas electricity relation
    path_additional_scalars = os.path.join(preprocessed, "additional_scalars.csv")
    scalars = dp.load_b3_scalars(path_additional_scalars)

    # get emission limit, electricity gas relations and output_parameters of bpchp from `scalars`
    emission_limit = get_emission_limit(scalars)
    el_gas_relations = get_electricity_gas_relations(scalars)
    bpchp_out = get_bpchp_output_parameters(scalars)

    if not os.path.exists(optimized):
        os.mkdir(optimized)

    es = EnergySystem.from_datapackage(
        os.path.join(preprocessed, filename_metadata), attributemap={}, typemap=TYPEMAP
    )

    # create model from energy system (this is just oemof.solph)
    m = Model(es)

    # add constraints
    if emission_limit is not None:
        constraints.emission_limit(m, limit=emission_limit)
    if el_gas_relations is not None:
        add_electricity_gas_relation_constraints(model=m, relations=el_gas_relations)

    # select solver 'gurobi', 'cplex', 'glpk' etc
    m.solve(solver=solver)

    # get results from the solved model(still oemof.solph)
    es.meta_results = processing.meta_results(m)
    es.results = processing.results(m)
    es.params = processing.parameter_as_dict(es)

    # dump the EnergySystem
    es.dump(optimized)
