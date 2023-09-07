import pandas as pd

try:
    import geopandas as gpd
    from shapely.geometry import Point

except ImportError:
    raise ImportError(
        "No module named 'geopandas'. You need to install 'geopandas' in order to use this script."
    )


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
    regions_file = gpd.read_file(file_path)

    return regions_file


def filter_regions_file(de, regions):
    r"""
    Filters the data of a geopackage according to regions.

    Parameters
    ---------------
    'de': geopandas.GeoDataFrame
        Geoinformations of all regions in Germany
    'regions': list
        List with the names of the regions by which the GeoDataFrame shall be filtered

    Returns
    --------------
    geopandas.GeoDataFrame
        Geoinformation of desired regions in Germany
    """
    de_regions = de.loc[de["name"].isin(regions)]

    return de_regions


def add_region_to_register(register, regions):
    r"""
    Adds the region to a power plant.

    Parameters
    ---------------
    'register': pandas.DataFrame
        DataFrame with columns lat, lon
    'region': geopandas.GeoDataFrame
        GeoDataFrame with rows for the specific regions

    Returns
    --------------
    pandas.DataFrame
        DataFrame with new column 'name' containing the region name
    """
    # transform the lat/lon coordinates into a shapely point coordinates and
    # add column named "coordinates"
    register["coordinates"] = list(zip(register.lon, register.lat))
    register["coordinates"] = register["coordinates"].apply(Point)
    register_gdf = gpd.GeoDataFrame(register, geometry="coordinates", crs=4326)
    new_register_gdf = gpd.sjoin(register_gdf, regions, predicate="within")
    new_register = pd.DataFrame(new_register_gdf)

    return new_register
