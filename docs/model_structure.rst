.. _model_structure_label:

~~~~~~~~~~~~~~~
Model structure
~~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top


An `oemof.solph.EnergySystem` in the form of a tabular Datapackage form comprises scalar data
(elements) and data with a time index (sequences). The model oemof-B3 uses
[oemoflex](https://github.com/rl-institut/oemoflex) to build empty
DataPackages and fills them with concrete numbers.


Elements
--------

The element-files describe the busses and components of the energy system. All `oemof.solph.Bus` es
are defined in a single file :file:`bus.csv`. The other components are split between several files.

Filenames for the components are of the form
carrier-tech.csv (e.g. :file:`electricity-demand.csv`, :file:`gas-bpchp.csv`).

There is a set of general variables that appear in all components:

* **region** Region of a component. (the regions are defined in the regions file
  :file: ../oemofB3/model_structure/components.csv)
* **name** Unique name of the form :py:attr:`'region-carrier-tech'` (e.g. :py:attr:`'LU-gas-bpchp'`,
  :py:attr:`'AT-electricity-airsourcehp'`).
* **carrier** Energy carrier of the flow into the component (e.g. solar, wind, biomass, coal,
  lignite, uranium, oil, gas, methane, hydro, waste, electricity, heat). This allows to categorize
  the component and should correspond to the bus to which the component is connected.
* **tech** More detailled specification of the technology (e.g. st, ocgt, ccgt, pv, onshore,
  offshore, ror, phs,
  extchp, bpchp, battery)
* **type** Type of oemof.tabular.facade, defined in `TYPEMAP`.

Beyond that, there are specific variables which depend on the type of the component. Components and
their properties are defined in
[oemoflex](https://github.com/rl-institut/oemoflex/tree/dev/oemoflex/model).

Sequences
---------

The sequences-files contain all timeseries, like load profiles or possible renewable generation.

The filenames are of the form carrier-type_profile (e.g.
:file:`wind-offshore_profile.csv`, :file:`electricity-demand_profile.csv`).
