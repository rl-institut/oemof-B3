import os

from oemoflex.tools.helpers import load_yaml


here = os.path.dirname(os.path.abspath(__file__))

component_attrs_update = load_yaml(os.path.join(here, "component_attrs_update.yml"))

bus_attrs_update = load_yaml(os.path.join(here, "bus_attrs_update.yml"))

foreign_keys_update = load_yaml(os.path.join(here, "foreign_keys_update.yml"))

MODEL_STRUCTURE_DIR = os.path.join(here, "model_structure")

model_structures = {
    os.path.splitext(f_name)[0]: load_yaml(os.path.join(MODEL_STRUCTURE_DIR, f_name))
    for f_name in os.listdir(MODEL_STRUCTURE_DIR)
}
