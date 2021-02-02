import yaml


def load_yaml(file_path):
    with open(file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    return yaml_data
