import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

opsd = pd.read_csv (r'C:\Users\meinm\Documents\Git\oemof-B3\raw\conventional_power_plants_DE.csv')

b3 = opsd[opsd.state.isin(['Brandenburg', 'Berlin'])]
b3 = b3.copy()
b3.reset_index(inplace=True, drop=True)


b3.loc[:,'coordinates'] = pd.Series(zip(b3.lon, b3.lat))
b3['coordinates'] = b3['coordinates'].apply(Point)

b3_gdf = gpd.GeoDataFrame(b3, geometry='coordinates', crs=4326)


file_path = r"C:\Users\meinm\Documents\Git\oemof-B3\raw\boundaries_germany_nuts3.gpkg"
de = gpd.read_file(file_path)

b = ['Berlin']
bb = [
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
b = de.loc[de['name'].isin(b)]
bb = de.loc[de['name'].isin(bb)]

new_b3 = gpd.sjoin(b3_gdf, b, op='within')

print(new_b3)
#print(list(new_b3))