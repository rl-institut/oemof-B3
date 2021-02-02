import os

from oemof.tabular.datapackage import building
from oemof_b3.tools.helpers import load_yaml


# Path definitions
module_path = os.path.dirname(os.path.abspath(__file__))

FOREIGN_KEYS = 'foreign_keys.yml'


all_foreign_keys = load_yaml(os.path.join(module_path, FOREIGN_KEYS))


def infer(select_components, package_name, path):

    foreign_keys = {}

    for key, lst in all_foreign_keys.items():

        selected_lst = [item for item in lst if item in select_components]

        if selected_lst:
            foreign_keys[key] = selected_lst

    building.infer_metadata(
        package_name=package_name,
        foreign_keys=foreign_keys,
        path=path,
    )
