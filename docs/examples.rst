.. _examples_label:

~~~~~~~~
Examples
~~~~~~~~

To give a quick intro into oemof-B3's capabilities, we provide 3 simple
`examples <https://github.com/rl-institut/oemof-B3/tree/dev/examples>`_.

To run all example scenarios, execute:

::

     snakemake -j<NUMBER_OF_CPU_CORES> run_all_examples


The energy system of Brandenburg (BB) and Berlin (BE) is represented by two nodes, one for each of the regions.

Modelled components are 

* renewable energies (wind, photovoltaic, biomass),
* conventional power plants (gas, oil, others),
* li-ion batteries,
* transmission grid connection between BB and BE.

The examples are limited to the electricity sector, the heat sector is not modelled.

Data for capacities of wind, photovoltaic and biomass as well as electricity demand have been taken
from the grid development plan
(`Netzentwicklungsplan <https://www.netzentwicklungsplan.de/sites/default/files/2022-11/NEP_2035_V2021_1_Entwurf_Teil1_1.pdf>`_, p. 41 ff.)
:cite:`NEP2021_Entwurf_1`.
Data for efficiencies and costs (specific annuity, fuel costs) are based on different sources as well
as on own assumptions.


The electricity generating components and the grid cannot be expanded. Both are fixed.
But the model can invest into the battery storage to expand it.


The three examples have been built based on the grid development plan:

* **example_base**: This example represents a future energy system with higher capacities for renewables
  compared to the current system. The assumed capacities corresponds to those of scenario A 2035 of
  the grid development plan.
* **example_more_re**: This example assumes larger capacities of renewable energies (wind, pv,
  biomass) compared to the base example, corresponding to scenario B 2035 of the grid development
  plan.
* **example_more_re_less_fossil**: This example represents a system with more renewable capacities
  compared to the previous and assumes that the capacities of fossil (gas, oil) powerplants have
  been reduced further. The capacities correspond to scenario B 2040 of the grid development plan.