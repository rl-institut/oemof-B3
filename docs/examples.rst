.. _examples_label:

~~~~~~~~
Examples
~~~~~~~~

To give a quick intro into oemof-B3's capabilities, we provide 3 simple
`example scenarios <https://github.com/rl-institut/oemof-B3/tree/dev/examples>`_.

The energy system of Brandenburg and Berlin is represented by two nodes, one each of the regions.

Modelled components are 

* renewable energies (wind, photovoltaic, biomass),
* conventional power plants (gas, oil, others),
* li-ion batteries,
* transmission grid connection between BB and BE.

The heat sector is not included in the example scenarios.

Data for capacities of wind, photovoltaic and biomass as well as electricity demand have been taken
from the grid development plan
(`Netzentwicklungsplan <https://www.netzentwicklungsplan.de/sites/default/files/paragraphs-files/NEP_2035_V2021_1_Entwurf_Teil1.pdf>`_, p. 41 ff.)
:cite:`NEP2021_Entwurf_1`.
Data for efficiencies and costs (specific annuity, fuel costs) are based on different sources as well
as own assumptions.


The electricity generating components and the grid cannot be expanded. Both are fixed.
But it can be invested into battery storage to expand it.


The three scenarios have been built based on the grid development plan:

* **base**: This scenario represents a future energy system with higher capacities for renewables
  compared to the current system. The assumed capacities corresponds to those of scenario A 2035 of
  the grid development plan.
* **more_renewable**: This scenario assumes larger capacities of renewable energies (wind, pv,
  biomass) compared to the base scenario, corresponding to scenario B 2035 of the grid development
  plan.
* **more_renewable_less_fossil**: This scenario represents a system with more renewable capacities
  compared to the previous and assumes that the capacities of fossil (gas, oil) powerplants have
  been reduced further. The capacities correspond to scenario B 2040 of the grid development plan.
