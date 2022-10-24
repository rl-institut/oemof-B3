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

Raw data from external source comes in different formats. It is not part of the model on GitHub, but has to be downloaded separately and provided in the directory :file:`raw/`.
As a first step, preprocessing scripts in the model pipeline (see :ref:`Preprocessing`) convert it into the
oemof-B3-resources-format, explained in the next section. Raw data that represents model-own assumptions is provided in
that format already.

The following additional information about specific parameters should be considered:
Components can receive keywords for the electricity-gas-relation-constraint via the attribute :attr:`output_parameters`.
Keywords of components powered by gas start with :attr:`config.settings.optimize.gas_key` and such powered
with electricity with :attr:`config.settings.optimize.el_key` followed by :attr:`carrier` and :attr:`region` (example: :attr:`{"electricity-heat_decentral-B": 1}`).
Do not provide :attr:`output_parameters` or leave their :attr:`var_value` empty to neglect a component in the constraint.

oemof-B3 resources
------------------

The resources are preprocessed data that serve as material for building scenarios.
Because they are a first intermediate result, resources will be saved in :file:`results/_resources`.
The resources follow a common data schema defined in :file:`oemof_b3/schema/`.
There is a separate schema for scalars and for timeseries:

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

The next intermediate step is a preprocessed datapackage, which is built using resources,
scenario information and the information about the model structure.
A preprocessed datapackage represents an instance of an :class:`oemof.solph.EnergySystem`.

A datapackage is a collection of data in form of csv-files and metadata in form of a json.
The data consists one file for all busses and one for each
component, stored in :file:`results/<scenario>/preprocessed/data/elements` (scalar data) and
:file:`results/<scenario>/preprocessed/data/sequences` (time series for e.g. renewable feed-in or demand profiles),
stored in separate folders.

The examples in oemof-B3 are readily preprocessed datapackages (e.g. `<https://github.com/rl-institut/oemof-B3/tree/dev/examples/example_base/preprocessed>`_).
Below is an example of the element file for the gas turbine of the base examples scenario, which can be found in
:file:`examples/base/preprocessed/base/data/elements/ch4-gt.csv`.

.. csv-table::
   :delim: ,
   :file: ../examples/example_base/preprocessed/data/elements/ch4-gt.csv

A separate file, :file:`additional_scalars.csv`, can contain additional information on constraints.
This file is not described in the metadata yet, but will become an official part of the datapackage in the future.

Other than the examples, the datapackages representing actual scenarios are built automatically from the resources,
the scenario informationscenario/<scenario.yml> and the `model structure <https://github.com/rl-institut/oemof-B3/tree/dev/oemof_b3/model/model_structure>`_.

Components and their attributes are defined in
`oemoflex <https://github.com/rl-institut/oemoflex/tree/dev/oemoflex/model/component_attrs.yml>`_.
Components and properties can also be added or updated in oemof-B3 using the files in :file:`oemof_b3/model/`.

Postprocessed data
-------------------

Data postprocessing makes use of oemoflex's functionality, thus postprocessed data follows its
data format. See oemoflex' documention on
`postprocessed results <https://oemoflex.readthedocs.io/en/latest/overview.html#postprocess-results>`_
for further information.
