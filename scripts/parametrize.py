import sys

from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.tools.helpers import load_yaml


if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    edp_path = sys.argv[2]

    scenario_specs = load_yaml(scenario_specs)

    # setup default structure
    edp = EnergyDataPackage.from_csv_dir(edp_path)

    edp.parametrize(frame='heat-demand', column='amount', values=1)

    edp.parametrize(frame='heat-demand_profile', column='BB-heat-demand-profile', values=[0] * 240)

    # save to csv
    edp.to_csv_dir(edp_path)
