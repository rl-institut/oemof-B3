import os

from oemoflex.tools.helpers import load_yaml


here = os.path.dirname(os.path.abspath(__file__))

component_attrs_update = load_yaml(os.path.join(here, "component_attrs_update.yml"))

bus_attrs_update = load_yaml(os.path.join(here, "bus_attrs_update.yml"))

foreign_keys_update = load_yaml(os.path.join(here, "foreign_keys_update.yml"))

MODEL_STRUCTURES = ["model_structure_full", "model_structure_el_only"]

model_structures = {
    s: load_yaml(os.path.join(here, s + ".yml")) for s in MODEL_STRUCTURES
}
