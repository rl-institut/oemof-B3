import sys

from oemof_b3.model.model_structure import create_default_data


if __name__ == '__main__':

    scenario = sys.argv[1]

    destination = sys.argv[2]

    import yaml

    def load_yaml(file_path):
        with open(file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)

        return yaml_data

    scenario_config = load_yaml(scenario)

    select_components = scenario_config['select_components']

    create_default_data(
        destination=destination,
        select_components=select_components,
    )
