from collections import namedtuple
from oemof_b3.config import config
from oemof_b3.tools import oep

OEP_SCHEMA = "model_draft"

RESOURCES_DIR = config.ROOT_DIR / "results" / "_resources"
Resource = namedtuple("Resource", ("name", "tablename"))
RESOURCES = (Resource("test", "sedos_extended_scalars"),)  # TODO: Fill in all resources


def download_resources():
    for resource in RESOURCES:
        output_filename = RESOURCES_DIR / f"{resource.name}.csv"
        oep.download_table_from_OEP(output_filename, resource.tablename, OEP_SCHEMA)


if __name__ == "__main__":
    download_resources()
