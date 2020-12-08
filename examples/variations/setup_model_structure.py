import os



from oemofB3.model_structure import create_default_data
from oemofB3.variations import VariationGen

here = os.path.abspath(os.path.dirname(__file__))

preprocessed_elements = os.path.join(here, 'preprocessed', 'basic_datapackage', 'data')

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
