import os

from oemoflex.tools.helpers import load_yaml


here = os.path.dirname(os.path.abspath(__file__))

component_attrs_update = load_yaml(os.path.join(here, "component_attrs_update.yml"))

bus_attrs_update = load_yaml(os.path.join(here, "bus_attrs_update.yml"))
