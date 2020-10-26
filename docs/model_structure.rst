.. _model_structure_label:

~~~~~~~~~~~~~~
Model structure
~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top


An `oemof.solph.EnergySystem` in tabular form comprises scalar data (elements) and data with a time
index (sequences). There is a general classification scheme introduced by oemof.tabular

* carrier
* tech
* type

Elements
--------

All `oemof.solph.Bus` es are defined in a single file :file:`bus.csv`.

The other components are split between several files. Filenames for the components are of the form
carrier-tech.csv (e.g. :file:`electricity-demand.csv`, :file:`gas-bpchp.csv`).

* **region** Region of a component. (the regions are defined in the regions file
  :file: ../oemofB3/model_structure/components.csv)
* **name** Unique name of the form :py:attr:`'region-carrier-tech'` (e.g. :py:attr:`'LU-gas-bpchp'`,
  :py:attr:`'AT-electricity-airsourcehp'`).
* **carrier** Energy carrier of the flow into the component (e.g. solar, wind, biomass, coal,
  lignite, uranium, oil, gas, methane, hydro, waste, electricity, heat).
* **tech** Specification of the technology (e.g. st, ocgt, ccgt, pv, onshore, offshore, ror, phs,
  extchp, bpchp, battery)
* **type** Type of oemof.tabular.facade, defined in `TYPEMAP`.

Sequences
---------

The filenames are of the form carrier-type_profile (e.g.
:file:`wind-offshore_profile.csv`, :file:`electricity-demand_profile.csv`).


Available components
====================

These components are available in oemoflex.

.. csv-table::
   :header-rows: 1
   :file: ../oemofB3/model_structure/components.csv