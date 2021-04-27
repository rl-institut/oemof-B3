import sys

from oemof.solph import EnergySystem
from oemoflex.model.datapackage import ResultsDataPackage


if __name__ == "__main__":

    optimized = sys.argv[1]

    destination = sys.argv[2]

    es = EnergySystem()

    es.restore(optimized)

    rdp = ResultsDataPackage.from_energysytem(es)

    rdp.to_csv_dir(destination)
