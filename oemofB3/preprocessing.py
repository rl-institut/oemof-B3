import os

import pandas as pd


module_path = os.path.dirname(os.path.abspath(__file__))

datetimeindex = pd.date_range(start='2019-01-01', freq='H', periods=8760)

regions_list = list(
    pd.read_csv(os.path.join(module_path, 'model_structure', 'regions.csv'), squeeze=True)
)

link_list = list(
    pd.read_csv(os.path.join(module_path, 'model_structure', 'links.csv'), squeeze=True)
)


def create_default_elements(
        dir,
        busses_file=os.path.join(module_path, 'model_structure', 'busses.csv'),
        components_file=os.path.join(module_path, 'model_structure', 'components.csv'),
        component_attrs_dir=os.path.join(module_path, 'model_structure', 'component_attrs'),
        select_components=None,
):
    r"""
    Prepares oemoef.tabluar input CSV files:
    * includes headers according to definitions in CSVs in directory 'component_attrs_dir'
    * pre-define all oemof elements (along CSV rows) without actual dimensions/values

    Parameters
    ----------
    dir : str (dir path)
        target directory where to put the prepared CSVs

    components_file : str (file path)
        CSV where to read the components from

    component_attrs_dir : str (dir path)
        CSV where to read the components' attributes from

    select_components : list
        List of default elements to create

    Returns
    -------
    None
    """
    components_file = os.path.join(module_path, components_file)

    # TODO Better put this as another field into the components.csv as well?
    component_attrs_dir = os.path.join(module_path, component_attrs_dir)

    components = pd.read_csv(components_file).name.values

    if select_components is not None:
        undefined_components = set(select_components).difference(set(components))

        assert not undefined_components,\
            f"Selected components {undefined_components} are not in components."

        components = [c for c in components if c in select_components]

    bus_df = create_bus_element(busses_file)

    bus_df.to_csv(os.path.join(dir, 'bus.csv'))

    for component in components:
        component_attrs_file = os.path.join(component_attrs_dir, component + '.csv')

        df = create_component_element(component_attrs_file)

        # Write to target directory
        df.to_csv(os.path.join(dir, component + '.csv'))


def create_bus_element(busses_file):
    r"""

    Parameters
    ----------
    busses_file : path
        Path to busses file.

    Returns
    -------
    bus_df : pd.DataFrame
        Bus element DataFrame
    """
    busses = pd.read_csv(busses_file, index_col='carrier')

    regions = []
    carriers = []
    balanced = []

    for region in regions_list:
        for carrier, row in busses.iterrows():
            regions.append(region)
            carriers.append(region + '-' + carrier)
            balanced.append(row['balanced'])

    bus_df = pd.DataFrame({
        'region': regions,
        'name': carriers,
        'type': 'bus',
        'balanced': balanced
    })

    bus_df = bus_df.set_index('region')

    return bus_df


def create_component_element(component_attrs_file):
    r"""
    Loads file for component attribute specs and returns a pd.DataFrame with the right regions,
    links, names, references to profiles and default values.

    Parameters
    ----------
    component_attrs_file : path
        Path to file with component attribute specifications.

    Returns
    -------
    component_df : pd.DataFrame
        DataFrame for the given component with default values filled.

    """
    try:
        component_attrs = pd.read_csv(component_attrs_file, index_col=0)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"There is no file {component_attrs_file}") from e

    # Collect default values and suffices for the component
    defaults = component_attrs.loc[component_attrs['default'].notna(), 'default'].to_dict()

    suffices = component_attrs.loc[component_attrs['suffix'].notna(), 'suffix'].to_dict()

    comp_data = {key: None for key in component_attrs.index}

    # Create dict for component data
    if defaults['type'] == 'link':
        # TODO: Check the diverging conventions of '-' and '_' and think about unifying.
        comp_data['region'] = [link.replace('-', '_') for link in link_list]
        comp_data['name'] = link_list
        comp_data['from_bus'] = [link.split('-')[0] + suffices['from_bus'] for link in link_list]
        comp_data['to_bus'] = [link.split('-')[1] + suffices['to_bus'] for link in link_list]

    else:
        comp_data['region'] = regions_list
        comp_data['name'] = [region + suffices['name'] for region in regions_list]

        for key, value in suffices.items():
            comp_data[key] = [region + value for region in regions_list]

    for key, value in defaults.items():
        comp_data[key] = value

    component_df = pd.DataFrame(comp_data).set_index('region')

    return component_df
