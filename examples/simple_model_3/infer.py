"""
Run this script from the root directory of the datapackage to update
or create meta data.
"""
import os

from oemof.tabular.datapackage import building


name = "simple_model_3"

here = os.path.abspath(os.path.dirname(__file__))

preprocessed = os.path.join(here, "preprocessed", name)

if not os.path.exists(preprocessed):
    os.mkdir(preprocessed)


building.infer_metadata(
    package_name=name,
    foreign_keys={
        "bus": [
            "wind-onshore",
            "solar-pv",
            "electricity-shortage",
            "electricity-curtailment",
            "electricity-demand",
            "electricity-liion_battery",
        ],
        "profile": [
            "wind-onshore",
            "solar-pv",
            "electricity-demand",
        ],
        "from_to_bus": [
            "ch4-gt",
            "oil-st",
            "biomass-st",
            "other-st",
            "electricity-transmission",
        ],
    },
    path=preprocessed,
)
