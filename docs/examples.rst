.. _examples_label:

~~~~~~~~~~~~~~~
Examples
~~~~~~~~~~~~~~~

Example 1
=====
The model consists of two nodes, one for Brandenburg and one for Berlin.

Modelled components are 

- renewable energies (wind, photovoltaic, biomass)
- conventional power plants (gas, oil, others)

Data for capacities of wind, photovoltaic and biomass as well as electricity demand have been taken from
the grid development plan (`Netzentwicklungsplan <https://www.netzentwicklungsplan.de/sites/default/files/paragraphs-files/NEP_2035_V2021_1_Entwurf_Teil1.pdf>`_, p. 41 ff.).
Data for efficiency and costs (specific annuity, fuel costs) are based on different sources as well as own assumptions and can be adjusted.


All electricity generating components can be expanded. 
Additionally, it can be invested into grid expansion and battery storage.

Three scenarios have been built based on the grid development plan:

- simple_model: corresponds to scenario A 2035 of the grid development plan
- simple_model_2: corresponds to scenario B 2035 of the grid development plan
- simple_model_3: corresponds to scenario B 2040 of the grid development plan


Installation
====

pip install -r requirements.txt
