import os

from oemofB3.preprocessing import create_default_elements


here = os.path.abspath(os.path.dirname(__file__))

preprocessed = os.path.join(here, 'preprocessed')

if not os.path.exists(preprocessed):
    os.mkdir(preprocessed)


create_default_elements(
    os.path.join(preprocessed, 'elements'),
    select_components=[
        'electricity-shortage',
        'electricity-curtailment',
        'electricity-demand',
        'heat-demand',
        'heat-excess',
        'heat-shortage',
        'wind-offshore',
        'wind-onshore',
        'solar-pv',
        'ch4-extchp',
    ]

)
