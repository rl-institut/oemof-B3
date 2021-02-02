import os

from oemof_b3.model.model_structure import create_default_data


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
        'electricity-transmission',
        'wind-onshore',
        'solar-pv',
        'ch4-gt',
        'oil-st',
        'other-st',
        'electricity-liion_battery',
        'biomass-st',
    ],
    dummy_sequences=True,
)
