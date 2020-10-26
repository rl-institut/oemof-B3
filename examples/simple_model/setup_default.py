import os

from oemofB3.preprocessing import create_default_data


here = os.path.abspath(os.path.dirname(__file__))

preprocessed_elements = os.path.join(here, 'preprocessed', 'simple_model', 'data')

if not os.path.exists(preprocessed_elements):
    os.makedirs(preprocessed_elements)

create_default_data(
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
    ],
    dummy_sequences=True,
)
