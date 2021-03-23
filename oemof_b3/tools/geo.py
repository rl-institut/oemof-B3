import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def load_regions_file(file_path):
    r"""
    Loads a geopackage containing all regions of Germany.

    Parameters
    ---------------
    'file_path' : string
        Path to geopackage containing geoinformation for all regions in Germany

    Returns
    ----------
    regions_file : geopandas.GeoDataFrame
        Geoinformation of all regions in Germany
    """
    de = gpd.read_file(file_path)

    return de


def filter_regions_file(de, regions):
    """
    filters the data of a geopackage according to regions

    Input
    ---------------
    'de': geopandas.GeoDataFrame
        geoinformations of all regions in Germany
    'regions': list
        with the names of the regions by which the GeoDataFrame shall be filtered

    Outputs
    --------------
    geopandas.GeoDataFrame
        with geoinformation of desired regions in Germany
    """
    de_regions = de.loc[de["name"].isin(regions)]

    return de_regions


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
    register["coordinates"] = list(zip(register.lon, register.lat))
    register["coordinates"] = register["coordinates"].apply(Point)
    register_gdf = gpd.GeoDataFrame(register, geometry="coordinates", crs=4326)
    new_register_gdf = gpd.sjoin(register_gdf, regions, op="within")
    new_register = pd.DataFrame(new_register_gdf)

    return new_register
