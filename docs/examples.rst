.. _examples_label:

~~~~~~~~
Examples
~~~~~~~~

Example 1
=========
The model consists of two nodes, one for Brandenburg and one for Berlin.

Modelled components are 

- renewable energies (wind, photovoltaic, biomass)
- conventional power plants (gas, oil, others)

Data for capacities of wind, photovoltaic and biomass as well as electricity demand have been taken
from the grid development plan
(`Netzentwicklungsplan <https://www.netzentwicklungsplan.de/sites/default/files/paragraphs-files/NEP_2035_V2021_1_Entwurf_Teil1.pdf>`_, p. 41 ff.).
Data for efficiency and costs (specific annuity, fuel costs) are based on different sources as well
as own assumptions and can be adjusted.


All electricity generating components can be expanded. 
Additionally, it can be invested into grid expansion and battery storage.

Three scenarios have been built based on the grid development plan:

- **base**: This scenario represents a future energy system with higher capacities for renewables
  compared to the current system. The assumed capacities corresponds to those of scenario A 2035 of
  the grid development plan.
- **more_renewable**: This scenario assumes larger capacities of renewable energies (wind, pv,
  biomass) compared to the base scenario, corresponding to scenario B 2035 of the grid development
  plan.
- **more_renewable_less_fossil**: This scenario represents a system with more renewable capacities
  compared to the previous and assumes that the capacities of fossil (gas, oil) powerplants have
  been reduced further. The capacities correspond to scenario B 2040 of the grid development plan.
