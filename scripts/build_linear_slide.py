# coding: utf-8
r"""
Inputs
-------
scenario_specs : str
    ``scenarios/{scenario}.yml``: path of input file (.yml) containing scenario specifications
destination : str
    ``results/{scenario}/preprocessed``: path of output directory
logfile : str
    ``logs/{scenario}.log``: path to logfile

Outputs
---------
oemoflex.EnergyDatapackage
    EnergyDatapackage that can be read by oemof.tabular, with data (scalars and timeseries)
    as csv and metadata (describing resources and foreign key relations) as json.

Description
-------------
The script creates an empty EnergyDatapackage from the specifications given in the scenario_specs,
fills it with scalar and timeseries data, infers the metadata and saves it to the given destination.
Further, additional parameters like emission limit are saved in a separate file.
"""
import os
import sys
from oemof_b3.config import config
from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.model.variations import EDPSensitivity


if __name__ == "__main__":
    path_lb = sys.argv[1]

    path_ub = sys.argv[2]

    destination = sys.argv[3]

    n = int(sys.argv[4])

    logfile = sys.argv[5]

    logger = config.add_snake_logger(logfile, "build_linear_slide")

    if not os.path.exists(destination):
        os.mkdir(destination)

    lb = EnergyDataPackage.from_csv_dir(path_lb)
    ub = EnergyDataPackage.from_csv_dir(path_ub)

    lb.stack_components()
    ub.stack_components()

    sensitivity = EDPSensitivity(lb, ub)

    logger.info(f"Creating {n} samples.")
    samples = sensitivity.get_linear_slide(n)

    for n_sample, sample in samples.items():
        # TODO get edps and use sample.basepath
        path = os.path.join(destination, str(n_sample) + ".csv")
        sample.to_csv(path)
