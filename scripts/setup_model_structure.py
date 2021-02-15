import sys

from oemof_b3.model.model_structure import create_default_data
from oemof_b3.tools.helpers import load_yaml


if __name__ == '__main__':

    scenario = sys.argv[1]

    destination = sys.argv[2]

    scenario_specs = load_yaml(scenario)

    keys = ['busses', 'select_components', 'select_regions', 'select_links']

    extra_kwargs = {}
    for key in keys:
        if key in scenario_specs:
            extra_kwargs[key] = scenario_specs[key]

    create_default_data(
        destination=destination,
        **extra_kwargs
    )
