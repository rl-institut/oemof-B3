.. _model_structure_label:

~~~~~~~~~~~~~~~
Model structure
~~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top


The input data consists of scalar data (elements) and data with a time index (sequences).
The model oemof-B3 uses `oemoflex <https://github.com/rl-institut/oemoflex>`_ to build empty
DataPackages and fills them with concrete numbers using the input data (see :ref:`buid_datapckage<build_datapackage>`).


Elements
--------

The element-files describe the busses and components of the energy system. All `oemof.solph.Bus` es
are defined in a single file :file:`bus.csv`. The other components are split between several files.

Filenames for the components are of the form
carrier-tech.csv (e.g. :file:`electricity-demand.csv`, :file:`gas-bpchp.csv`).

There is a set of general variables that appear in all components:

* **id_scal** Numbering of the component (Optional)

* **scenario** ...

* **name** Unique name of the form :py:attr:`'region-carrier-tech'` (e.g. :py:attr:`'LU-gas-bpchp'`,
  :py:attr:`'AT-electricity-airsourcehp'`).

* **var_name** ...

* **carrier** Energy carrier of the flow into the component (e.g. solar, wind, biomass, coal,
  lignite, uranium, oil, gas, methane, hydro, waste, electricity, heat). This allows to categorize
  the component and should correspond to the bus to which the component is connected.

* **region** Region of a component. (the regions are defined in the topology file
  :file: ../oemof_b3/model/topology.yml)

* **tech** More detailled specification of the technology (e.g. st, ocgt, ccgt, pv, onshore,
  offshore, ror, phs,
  extchp, bpchp, battery)
* **type** Type of oemof.tabular.facade, defined in `TYPEMAP`.

* **var_value**

* **var_unit**

* **source**

* **comment**

Below is an example of the gas turbine of the base examples scenario, which can be found in
:file:`examples/base/preprocessed/base/data/elements/ch4-gt.csv`.

=======  =========  ==========  =======  =====  ========  ==============  ========  =============  ===========  =============  =============  ==========  =================
region   name       type        carrier  tech   from_bus  to_bus          capacity  capacity_cost  efficiency   carrier_cost   marginal_cost  expandable  output_paramters
=======  =========  ==========  =======  =====  ========  ==============  ========  =============  ===========  =============  =============  ==========  =================
BE       BE-ch4-gt  conversion  ch4      gt     BE-ch4    BE-electricity  1500000                  0.619        0.021          0.0045         False       {}
BB       BB-ch4-gt  conversion  ch4      gt     BB-ch4    BB-electricity  600000                   0.619        0.021          0.0045         False       {}
=======  =========  ==========  =======  =====  ========  ==============  ========  =============  ===========  =============  =============  ==========  =================

Beyond that, there are specific variables which depend on the type of the component. Components and
their properties are defined in
`oemoflex <https://github.com/rl-institut/oemoflex/tree/dev/oemoflex/model>`_.

Sequences
---------

The sequences-files contain all timeseries, like load profiles or possible renewable generation.

The filenames are of the form carrier-type_profile (e.g.
:file:`wind-offshore_profile.csv`, :file:`electricity-demand_profile.csv`).
