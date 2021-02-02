import sys

from oemof_b3.model.model_structure import create_default_data
from oemof_b3.tools.helpers import load_yaml


if __name__ == '__main__':

    scenario = sys.argv[1]

    destination = sys.argv[2]

    scenario_specs = load_yaml(scenario)

    select_components = scenario_specs['components']

    create_default_data(
        destination=destination,
        select_components=select_components,
    )
