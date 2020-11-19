.. _model_structure_label:

~~~~~~~~~~~~~~
Model structure
~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top


An `oemof.solph.EnergySystem` in tabular form comprises scalar data (elements) and data with a time
index (sequences).


Elements
--------

The element-files describe the busses and components of the energy system.

All `oemof.solph.Bus` es are defined in a single file :file:`bus.csv`.

The other components are split between several files.

Filenames for the components are of the form
carrier-tech.csv (e.g. :file:`electricity-demand.csv`, :file:`gas-bpchp.csv`).

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

Sequences
---------

The sequences-files contain all timeseries, like load profiles or possible renewable generation.

The filenames are of the form carrier-type_profile (e.g.
:file:`wind-offshore_profile.csv`, :file:`electricity-demand_profile.csv`).


Available components
====================

The components that are available in oemoflex are defined in the file
:file:`oemofB3/model_structure/components.csv`. The attributes of the available components are
defined in :file:`oemofB3/model_structure/components_attrs`. Here is an overview over all
components.

.. csv-table::
   :header-rows: 1
   :file: ../oemofB3/model_structure/components.csv

If you want to add a component, create a new file describing the component's attributes in
:file:`oemofB3/model_structure/components_attrs` and add an entry for the component to the file
:file:`oemofB3/model_structure/components.csv`.