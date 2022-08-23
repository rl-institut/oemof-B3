# coding: utf-8
r"""
Inputs
-------
preprocessed : str
    ``results/{scenario}/preprocessed``: Path to preprocessed EnergyDatapackage containing
    elements, sequences and datapackage.json.
optimized : str
    ``results/{scenario}/optimized/`` Target path to store dump of oemof.solph.Energysystem
    with optimization results and parameters.
logfile : str
    ``logs/{scenario}.log``: path to logfile

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
- `equate_flows_by_keyword`: electricty-gas relation is set (electricity/gas = factor).
    This constraint is only added if 'electricity_gas_relation' is added to the scalars.
    To use this constraint you need to copy
    [`equate_flows.py`](https://github.com/oemof/oemof-solph/blob/features/equate-flows/src/oemof/solph/constraints/equate_variables.py)
    of oemof.solph into `/tools` directory of `oemof-B3`.
The EnergySystem with results, meta-results and parameters is saved.

"""
import logging
import os
import sys
import numpy as np

from oemof.solph import EnergySystem, Model, constraints
from oemof.solph import processing

# DONT REMOVE THIS LINE!
# pylint: disable=unusedimport
from oemof.tabular import datapackage  # noqa
from oemof.tabular.facades import TYPEMAP

from oemof_b3.tools import data_processing as dp
from oemof_b3.tools.equate_flows import equate_flows_by_keyword
from oemof_b3.config import config


logger = logging.getLogger()


def drop_values_by_keyword(df, keyword="None"):
    """drops row if `var_value` is None"""
    drop_indices = df.loc[df.var_value == keyword].index
    df = df.drop(drop_indices)
    return df


def get_emission_limit(scalars):
    """Gets emission limit from scalars and returns None if it is missing or None."""
    emission_df_raw = scalars.loc[scalars["carrier"] == "emission"].set_index(
        "var_name"
    )
    emission_df = drop_values_by_keyword(emission_df_raw)

    # return None if no emission limit is given ('None' or entry missing)
    if emission_df.empty or emission_df.at["emission_limit", "var_value"] is np.nan:
        print("No emission limit will be set.")
        return None
    else:
        limit = emission_df.at["emission_limit", "var_value"]
        print(f"Emission limit will be set to {limit}.")
        return limit


def get_electricity_gas_relations(scalars):
    r"""
    Gets electricity/gas relations from scalars. Returns None if no relations are given.

    Returns
    -------
    pd.DataFrame
        Contains rows of scalars with 'var_name' `EL_GAS_RELATION`
    If no relation is given returns None.
    """
    relations_raw = scalars.loc[
        scalars.var_name == config.settings.optimize.el_gas_relation
    ]
    # drop relations that are None
    relations = drop_values_by_keyword(relations_raw)
    if relations.empty:
        print("No gas electricity relation will be set.")
        return None
    else:
        busses = relations.carrier.drop_duplicates().values
        print(f"Gas electricity relations will be set for busses: {busses}")
        return relations


def get_bpchp_output_parameters(scalars):
    r"""Gets 'output_parameters' of backpressure CHPs from scalars and
    returns None if it is missing or None."""
    bpchp_outs_raw = scalars.loc[
        (scalars.tech == "bpchp") & (scalars.var_name == "output_parameters")
    ]

    # drop rows that have empty dict as var_value
    bpchp_outs = drop_values_by_keyword(bpchp_outs_raw, "{}")
    if bpchp_outs.empty:
        return None
    else:
        return bpchp_outs


def add_output_parameters_to_bpchp(parameters, energysystem):
    r"""
    Adds keywords for electricity-gas relation constraint to backpressure CHPs.

    This is necessary as oemof.tabular does not support `output_parameters` of these components,
    yet. The keywords are set as attributes of the output flow towards `heat_bus`.

    Parameters
    ----------
    parameters : pd.DataFrame
        Contains output_parameters of backpressure CHP scalars.
    energysystem : oemof.solph.network.EnergySystem
        The energy system
    """
    # rename column 'name' as is collides with iterrows()
    parameters.rename(columns={"name": "name_"}, inplace=True)
    for i, element in parameters.iterrows():
        if element.name_ in energysystem.groups:
            # get heat bus the component is connected to
            bus = energysystem.groups[element.name_].heat_bus

            # get keyword and boolean value
            split_str = element.var_value.split('"')
            keyword = split_str[1]
            value = bool(split_str[2].split("}")[0].split()[1])

            # set keyword as attribute with value
            setattr(
                energysystem.groups[element.name_].outputs.data[bus], keyword, value
            )
        else:
            logging.warning(
                f"No element '{element.name_}' in EnergySystem. Cannot add output_parameters."
            )

    return energysystem


def add_electricity_gas_relation_constraints(model, relations):
    r"""
    Adds constraint `equate_flows_by_keyword` to `model`.

    The components belonging to one constraint are selected by keywords. The keywords of components
    powered by any gas start with `GAS_KEY` and such powered with electricity with `EL_KEY`,
    respectively: <`GAS_KEY`>-<carrier>-<region>.
    Attention: Although a value is provided for the keywords in the input data
    (e.g. {"electricity-heat_central-B": 1}) this value does not have any effect, at the moment.
    If a component is not to be taken into account the keyword must not be provided.

    Parameters
    ----------
    model : oemof.solph.Model
        optmization model
    relations : pd.DataFrame
        Contains electricity/gas relations in column 'var_value'. Further contains at least columns
        'carrier' and 'region'.
    """
    for index, row in relations.iterrows():
        # Formulate suffix for keywords <carrier>-<region>
        suffix = f"{row.carrier}-{row.region}"
        equate_flows_by_keyword(
            model=model,
            keyword1=f"{config.settings.optimize.gas_key}-{suffix}",
            keyword2=f"{config.settings.optimize.el_key}-{suffix}",
            factor1=row.var_value,
            name=f"equate_flows_{suffix}",
        )


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

    # get additional scalars, set to None at first
    emission_limit = None
    el_gas_relations = None
    bpchp_out = None
    additional_scalars = get_additional_scalars()
    if additional_scalars is not None:
        emission_limit = get_emission_limit(additional_scalars)
        el_gas_relations = get_electricity_gas_relations(additional_scalars)
        bpchp_out = get_bpchp_output_parameters(additional_scalars)

    if not os.path.exists(optimized):
        os.mkdir(optimized)

    try:
        es = EnergySystem.from_datapackage(
            os.path.join(preprocessed, config.settings.optimize.filename_metadata),
            attributemap={},
            typemap=TYPEMAP,
        )

        # Reduce number of timestep for debugging
        if config.settings.optimize.debug:
            es.timeindex = es.timeindex[:3]

            logger.info(
                "Optimizing in DEBUG mode: Run model with first 3 timesteps only."
            )

        # add output_parameters of bpchp
        if bpchp_out is not None:
            es = add_output_parameters_to_bpchp(parameters=bpchp_out, energysystem=es)

        # create model from energy system (this is just oemof.solph)
        m = Model(es)

        # add constraints
        if emission_limit is not None:
            constraints.emission_limit(m, limit=emission_limit)
        if el_gas_relations is not None:
            add_electricity_gas_relation_constraints(
                model=m, relations=el_gas_relations
            )

        # tell the model to get the dual variables when solving
        if config.settings.optimize.receive_duals:
            m.receive_duals()

        # save solver log to scenario specific location
        solve_kwargs = config.settings.optimize.solve_kwargs
        solve_kwargs["logfile"] = logfile.split(".")[0] + "_solver_log.log"

        logger.info(
            f"Solving with solver '{config.settings.optimize.solver}' "
            f"using solve_kwargs '{config.settings.optimize.solve_kwargs}' "
            f"and cmdline_options '{config.settings.optimize.cmdline_options}'."
        )

        m.solve(
            solver=config.settings.optimize.solver,
            solve_kwargs=config.settings.optimize.solve_kwargs,
            cmdline_options=config.settings.optimize.cmdline_options,
        )

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
