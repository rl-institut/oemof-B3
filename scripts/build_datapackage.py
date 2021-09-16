import sys
from collections import OrderedDict

import pandas as pd
from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.tools.helpers import load_yaml

from oemof_b3.model import bus_attrs_update, component_attrs_update, foreign_keys_update
from oemof_b3.tools.data_processing import (
    filter_df,
    load_b3_scalars,
    load_b3_timeseries,
    unstack_timeseries,
)


def update_with_checks(old, new):
    # Check if some data would get lost
    if not new.index.isin(old.index).all():
        raise Warning("Index of new data is not in the index of old data.")

    try:
        # Check if it overwrites by setting errors = 'raise'
        old.update(new, errors="ignore")
    except ValueError:
        print("Update overwrites existing data.")


def parametrize_scalars(edp, scalars):

    edp.stack_components()

    update_with_checks(edp.data["component"], scalars)

    edp.unstack_components()

    return edp


def parametrize_sequences(edp, ts):

    ts_groups = ts.groupby("var_name")

    for name, data in ts_groups:

        data["var_name"] = data["region"] + "-" + data["var_name"]

        data_unstacked = unstack_timeseries(data)

        edp.data[name].update(data_unstacked)

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

    # parametrize scalars
    path_scalars = scenario_specs["path_scalars"]

    scalars = load_b3_scalars(path_scalars)

    filters = OrderedDict(sorted(scenario_specs["filter_scalars"].items()))

    for id, filt in filters.items():
        filtered = scalars.copy()

        for key, value in filt.items():

            filtered = filter_df(filtered, key, value)

        filtered = filtered.set_index(["name", "var_name"]).loc[:, "var_value"]

        edp = parametrize_scalars(edp, filtered)

        print(f"Updated DataPackage with scalars filtered by {filt}.")

    # parametrize timeseries
    paths_timeseries = scenario_specs["paths_timeseries"]

    ts = load_b3_timeseries(paths_timeseries)

    ts_filtered = ts

    edp = parametrize_sequences(edp, ts)

    print(f"Updated DataPackage with timeseries from '{paths_timeseries}'.")

    # save to csv
    edp.to_csv_dir(destination)

    # add metadata
    edp.infer_metadata(foreign_keys_update=foreign_keys_update)
