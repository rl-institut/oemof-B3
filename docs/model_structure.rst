.. _model_structure_label:

~~~~~~~~~~~~~~~
Model structure
~~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top

In oemof-B3, data appears in different formats in each processing step. Here, we give a short
overview.

Raw data
--------

Raw data from external source comes in different formats. As a first step, the model transforms it
into the oemof-B3-resources-format, explained below. Raw data that represents model-own
assumptions is provided in that format already.

oemof-B3 resources
------------------

The resources, i.e. preprocessed data that serves as material for building scenarios, are prepared
by several scripts. They follow a common data schema defined in :file:`oemof_b3/schema/`.

Scalars

.. csv-table::
   :delim: ;
   :file: ../oemof_b3/schema/scalars.csv

Time series

.. csv-table::
   :delim: ;
   :file: ../oemof_b3/schema/timeseries.csv

A few more conventions are important to know. Missing data is left empty. If a value applies to all
regions, this is indicated by :attr:`ALL`. If it applies to the sum of regions, by :attr:`TOTAL`.

Preprocessed datapackages
-------------------------

The input data as described above is then preprocessed. The preprocessed data in turn is organized in
elements (scalars data) and sequences, stored in separate folders and with one file for each component.
Below is an example of the element file for the gas turbine of the base examples scenario, which can be found in
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

Postprocessed data
-------------------
