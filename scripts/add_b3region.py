import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from tabulate import tabulate

opsd = pd.read_csv (r'C:\Users\meinm\Documents\Git\oemof-B3\raw\conventional_power_plants_DE.csv')

b3 = opsd[opsd.state.isin(['Brandenburg', 'Berlin'])]
b3 = b3.copy()
b3.reset_index(inplace=True, drop=True)
#print(tabulate(b3, headers='keys', tablefmt='psql'))





def load_regions_file():
    file_path = r"C:\Users\meinm\Documents\Git\oemof-B3\raw\boundaries_germany_nuts3.gpkg"
    de = gpd.read_file(file_path)

    b3_regions = [
        'Berlin',
        'Barnim',
        'Brandenburg an der Havel',
        'Cottbus',
        'Dahme-Spreewald',
        'Elbe-Elster',
        'Frankfurt (Oder)',
        'Havelland',
        'Barnim',
        'Brandenburg',
        'Cottbus',
        'Dahme-Spreewald',
        'Elbe-Elster',
        'Frankfurt (Oder)',
        'Havelland',
        'Märkisch-Oderland',
        'Oberhavel',
        'Oberspreewald-Lausitz',
        'Oder-Spree',
        'Ostprignitz-Ruppin',
        'Potsdam',
        'Potsdam-Mittelmark',
        'Prignitz',
        'Spree-Neiße',
        'Teltow-Fläming',
        'Uckermark',
    ]
    b3_regions = de.loc[de['name'].isin(b3_regions)]

    return b3_regions


def add_region_to_register(register, regions):
    """
    adds the region to a power plant
    Input
    ---------------
    'register': pandas.DataFrame
        with columns lat, lon
    'region': geopandas.GeoDataFrame
        with rows for the specific regions
    returns
    --------------
    pandas.DataFrame
        with new column containing the region name
    """
    # transform the lat/lon coordinates into a shapely point coordinates and
    # add column named "coordinates"
    register['coordinates'] = list(zip(register.lon, register.lat))
    register['coordinates'] = register['coordinates'].apply(Point)
    register_gdf = gpd.GeoDataFrame(register, geometry='coordinates', crs=4326)
    #regions_gdf = gpd.GeoDataFrame(regions, geometry='geometry')
    new_register = gpd.sjoin(register_gdf, regions, op='within')

    new_register.drop(columns=['index_right', 'id_right', 'type_right', 'nuts', 'state_id'], inplace=True)
    new_register.rename(columns={'id_left': 'id', 'name': 'region'}, inplace=True)

    return(new_register)

bbb = load_regions_file()
new_b3 = add_region_to_register(b3, bbb)

print(tabulate(new_b3, headers='keys', tablefmt='psql'))
print(new_b3.shape)


a = new_b3.groupby('region')
print(tabulate(a, headers='keys', tablefmt='psql'))

b = a.agg({'capacity_net_bnetza':'sum'})
print(tabulate(b, headers='keys', tablefmt='psql'))

print(type(a), type(b))

def regional_aggregate(df):
    print('Hallo')
