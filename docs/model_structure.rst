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

Raw data from external source comes in different formats. As a first step, preprocessing scripts in
the model pipeline (see :ref:`Preprocessing`) convert it into the oemof-B3-resources-format,
explained in the next section. Raw data that represents model-own assumptions is provided in that format already.

oemof-B3 resources
------------------

The resources are preprocessed data that serves as material for building scenarios. They follow
a common data schema defined in :file:`oemof_b3/schema/`.

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
There is no unit transformation within the model, i.e. the user needs to ensure the consistency of units.

Preprocessed datapackages
-------------------------

The resources are then again preprocessed together with the scenario information to generate
scenario-specific datapackages. A preprocessed datapackage represents an instance of an energy system scenario.
It is a collection of .csv-files, one file for all busses and one for each
component, stored in :file:`elements` (scalars data) and :file:`sequences` (time series for e.g.
renewable feedin or demand profiles), stored in separate folders. Below is an example of the element
file for the gas turbine of the base examples scenario, which can be found in
:file:`examples/base/preprocessed/base/data/elements/ch4-gt.csv`.

.. todo: Explain more about scenarios, where and how they are defined and thus how new ones can be made

=======  =========  ==========  =======  =====  ========  ==============  ========  =============  ===========  =============  =============  ==========  =================
region   name       type        carrier  tech   from_bus  to_bus          capacity  capacity_cost  efficiency   carrier_cost   marginal_cost  expandable  output_paramters
=======  =========  ==========  =======  =====  ========  ==============  ========  =============  ===========  =============  =============  ==========  =================
BE       BE-ch4-gt  conversion  ch4      gt     BE-ch4    BE-electricity  1500000                  0.619        0.021          0.0045         False       {}
BB       BB-ch4-gt  conversion  ch4      gt     BB-ch4    BB-electricity  600000                   0.619        0.021          0.0045         False       {}
=======  =========  ==========  =======  =====  ========  ==============  ========  =============  ===========  =============  =============  ==========  =================

More generally, there are specific variables which depend on the type of the component. Components and
their properties are defined in
`oemoflex <https://github.com/rl-institut/oemoflex/tree/dev/oemoflex/model>`_.
Components and properties and also be added or updated in oemof-B3 using the files in :file:`oemof_b3/model/`.

.. todo: Explain how to do this and when it is relevant.

Postprocessed data
-------------------

Data postprocessing makes use of oemoflex's functionality, thus postprocessed data follows its
data format.
