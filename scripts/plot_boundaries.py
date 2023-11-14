#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import geopandas as gpd
import matplotlib.pyplot as plt


file_path = sys.argv[1]

destination = sys.argv[2]

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

print(de.head())

def plot():
    fig, ax = plt.subplots(dpi=600, figsize=(2,2))
    de.plot(ax=ax)
    b.plot(ax=ax, color='r')
    bb.plot(ax=ax, color='g', edgecolor='k', linewidth=0.1)


    xlim = ([bb.total_bounds[0]-1, bb.total_bounds[2]+1])
    ylim = ([bb.total_bounds[1]-1, bb.total_bounds[3]+1])

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)


    return fig, ax

plot()

plt.axis('off')

plt.tight_layout()

plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

plt.savefig(destination, format='png', dpi=600)
