"""
Run this script from the root directory of the datapackage to update
or create meta data.
"""
import os

from oemof.tabular.datapackage import building


name = 'simple_model'

here = os.path.abspath(os.path.dirname(__file__))

preprocessed = os.path.join(here, 'preprocessed')

if not os.path.exists(preprocessed):
    os.mkdir(preprocessed)


building.infer_metadata(
    package_name=name,
    foreign_keys={
        'bus': [
            'wind-onshore',
            'wind-offshore',
            'solar-pv',
            'electricity-shortage',
            'electricity-curtailment',
            'electricity-demand',
            'heat-demand',
            'heat-excess',
            'heat-shortage',
        ],
        'profile': [
            'wind-onshore',
            'wind-offshore',
            'solar-pv',
            'electricity-demand',
            'heat-demand',
        ],
        'chp': [
            'ch4-extchp',
        ],
    },
    path=preprocessed
)
