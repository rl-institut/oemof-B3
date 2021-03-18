import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def load_regions_file(file_path):
    """
    loads a geopackage containing all regions of Germany and filters for geodata of Berlin and
    all regions in Brandenburg

    Outputs
    --------------
    geopandas.GeoDataFrame
        with geoinformation of Berlin and all regions in Brandenburg
    """
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

    Outputs
    --------------
    pandas.DataFrame
        with new column 'name' containing the region name
    """
    # transform the lat/lon coordinates into a shapely point coordinates and
    # add column named "coordinates"
    register['coordinates'] = list(zip(register.lon, register.lat))
    register['coordinates'] = register['coordinates'].apply(Point)
    register_gdf = gpd.GeoDataFrame(register, geometry='coordinates', crs=4326)
    new_register_gdf = gpd.sjoin(register_gdf, regions, op='within')
    new_register = pd.DataFrame(new_register_gdf)

    return new_register
