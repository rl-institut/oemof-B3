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
from oemof_b3.model import foreign_keys_update
import oemof_b3.tools.data_processing as dp
from pandas.testing import assert_frame_equal

if __name__ == "__main__":
    path_lb = sys.argv[1]

    path_ub = sys.argv[2]

    destination = sys.argv[3]

    n = int(sys.argv[4])

    logfile = sys.argv[5]

    logger = config.add_snake_logger(logfile, "build_linear_slide")

    if not os.path.exists(destination):
        os.mkdir(destination)

    lb = EnergyDataPackage.from_metadata(os.path.join(path_lb, "datapackage.json"))
    ub = EnergyDataPackage.from_metadata(os.path.join(path_ub, "datapackage.json"))

    # load additional scalars and make sure that they are the same
    # TODO: Currently, varying the parameters for the constraints is not supported.
    #  As soon as the additional scalars representing for contraints are part of the
    #  datapackage, this step can be removed.
    additional_scalars_lb = dp.load_b3_scalars(
        os.path.join(path_lb, "additional_scalars.csv")
    )
    additional_scalars_ub = dp.load_b3_scalars(
        os.path.join(path_ub, "additional_scalars.csv")
    )
    assert_frame_equal(additional_scalars_lb, additional_scalars_ub)

    lb.stack_components()
    ub.stack_components()

    sensitivity = EDPSensitivity(lb, ub)

    logger.info(f"Creating {n} samples.")
    samples = sensitivity.get_linear_slide(n)

    for n_sample, sample in samples.items():

        sample.unstack_components()

        path = os.path.join(destination, str(n_sample), "preprocessed")

        sample.basepath = path

        sample.to_csv_dir(path)

        dp.save_df(additional_scalars_lb, os.path.join(path, "additional_scalars.csv"))

        sample.infer_metadata(foreign_keys_update)
