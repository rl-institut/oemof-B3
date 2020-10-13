import os

from oemofB3.preprocessing import create_default_elements


here = os.path.abspath(os.path.dirname(__file__))

preprocessed_elements = os.path.join(here, 'preprocessed', 'elements')

if not os.path.exists(preprocessed_elements):
    os.mkdir(preprocessed_elements)

create_default_elements(
    preprocessed_elements,
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
