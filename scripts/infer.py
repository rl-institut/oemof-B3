import sys
import os

from oemof_b3.model.inferring import infer
from oemof_b3.tools.helpers import load_yaml


if __name__ == "__main__":

    scenario_specs = load_yaml(sys.argv[1])

    destination = os.path.dirname(sys.argv[2])

    infer(scenario_specs["select_components"], scenario_specs["scenario"], destination)
