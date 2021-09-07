import sys

import pandas as pd
from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.tools.helpers import load_yaml

from oemof_b3.model import component_attrs_update, bus_attrs_update


def update_with_checks(old, new):
    # Check if some data would get lost
    if not new.index.isin(old.index).all():
        raise Warning("Index of new data is not in the index of old data.")

    try:
        # Check if it overwrites by setting errors = 'raise'
        old.update(new, errors="raise")
    except ValueError:
        raise Warning("Update would overwrite existing data.")


def parametrize_scalars(edp, scalars):

    edp.stack_components()

    update_with_checks(edp.data["component"], scalars)

    edp.unstack_components()

    return edp


if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    destination = sys.argv[2]

    scenario_specs = load_yaml(scenario_specs)

    # setup empty EnergyDataPackage
    datetimeindex = pd.date_range(start="2019-01-01", freq="H", periods=8760)

    # setup default structure
    edp = EnergyDataPackage.setup_default(
        basepath=destination,
        datetimeindex=datetimeindex,
        bus_attrs_update=bus_attrs_update,
        component_attrs_update=component_attrs_update,
        name=scenario_specs["name"],
        regions=scenario_specs["regions"],
        links=scenario_specs["links"],
        busses=scenario_specs["busses"],
        components=scenario_specs["components"],
    )

    # parametrize
    paths_scalars = scenario_specs["paths_scalars"]

    for path in paths_scalars:
        print(f"Updating DataPackage with data from '{path}'.")
        scalars = pd.read_csv(path, index_col=[0, 1])["var_value"]
        edp = parametrize_scalars(edp, scalars)

    # save to csv
    edp.to_csv_dir(destination)

    # add metadata
    edp.infer_metadata()
