# coding: utf-8
r"""
Inputs
-------
optimized : str
    ``results/{scenario}/optimized``: Directory containing dump of oemof.solph.Energysystem
    with optimization results and parameters.
scenario_name : str
    ``{scenario}``: Name of the scenario.
destination : str
    ``results/{scenario}/postprocessed``: Target path for postprocessed results.
logfile : str
    ``results/{scenario}/{scenario}.log``: path to logfile

Outputs
---------
oemoflex.ResultsDatapackage
    ResultsDatapackage

Description
-------------
The script performs the postprocessing of optimization results.

Explanations about the structure of the postprocessed data can be found in section
:ref:`Postprocessed data` of the `docu <https://oemof-b3.readthedocs.io/en/latest/index.html>`_.
"""
import os
import sys
import pandas as pd

from oemof.solph import EnergySystem
from oemoflex import config as oemoflexconfig
from oemoflex.model.datapackage import ResultsDataPackage

from oemof_b3.config import config


def get_separator():
    return config.settings.general.separator


if __name__ == "__main__":

    optimized = sys.argv[1]

    scenario_name = sys.argv[2]

    destination = sys.argv[3]

    logfile = sys.argv[4]
    logger = config.add_snake_logger(logfile, "postprocess")

    oemoflexconfig.config.settings.SEPARATOR = get_separator()

    try:
        es = EnergySystem()

        es.restore(optimized)

        rdp = ResultsDataPackage.from_energysytem(es)

        rdp.set_scenario_name(scenario_name)

        rdp.to_csv_dir(destination)

        pd.Series({"objective": es.meta_results["objective"]}).to_csv(
            os.path.join(destination, "objective.csv"),
            sep=oemoflexconfig.config.settings.SEPARATOR,
        )

    except:  # noqa: E722
        logger.exception(
            f"Could not postprocess data from energysystem in '{optimized}'."
        )
        raise
