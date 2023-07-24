.. _model_pipeline_label:

~~~~~~~~~~~~~~
Model pipeline
~~~~~~~~~~~~~~

The main functionality of oemof-B3 is a data processing pipeline which is managed using snakemake.
The pipeline preprocesses raw data into scalar and time series resources that are used to
build tabular datapackages representing single energy system optimization problems. These can be
understood by `oemof.tabular <https://github.com/oemof/oemof-tabular>`_ and optimized by
`oemof.solph <https://github.com/oemof/oemof-solph>`_. In the next steps, the results of the
optimization are postprocessed and plotted. The individual steps are documented in detail in the
following sections.

.. 	image:: _img/model_pipeline.svg
   :scale: 100 %
   :alt: schematic of model pipeline
   :align: center

.. created with snakemake --rulegraph run_all_scenarios plot_grouped_scenarios run_all_examples | dot -Tpdf > docs/_img/model_pipeline.svg

The subdirectories of oemof-B3 shown below contain configurations and data of the model.
:file:`Examples` contains pre-fabricated datapackages that can readily be optimized. The directory
:file:`scenarios` contains :file:`.yml`-files defining individual scenarios. Raw data is not part
of the repo and has to be provided in :file:`raw`. You can use the raw data we provide.
For instructions on how to automatically load the raw data into oemof-B3, see section section :ref:`How to run the model`.

Intermediate and final results as well as the
corresponding logfiles are saved in :file:`results`.

.. code-block::

    .
    ├── examples
    ├── oemof_b3
    │     ├── config
    │     ├── model
    │     ├── schema
    ├── raw
    ├── results
    ├── scenarios

Raw data
========
Raw data from external source comes in different formats. It is not part of the model on GitHub, but has to be downloaded from Zenodo at the beginning.
As a first step, preprocessing scripts in the model pipeline (see :ref:`Prepare resources`) convert it into the
oemof-B3-resources-format, explained in the next section (see :ref:`Schema`). Raw data that represents model-own assumptions is provided in
that format already. When providing raw data you have to follow some conventions, which are summarized in the section :ref:`Conventions`.


.. _Schema_label:

Schema
------

Raw data with model-own assumptions and oemof-B3-resources-format follow a common data schema defined in :file:`oemof_b3/schema/`.
There is a separate schema for scalars and for timeseries:

Scalars

.. csv-table::
   :delim: ;
   :file: ../oemof_b3/schema/scalars.csv

Time series

.. csv-table::
   :delim: ;
   :file: ../oemof_b3/schema/timeseries.csv


.. _conventions_label:

Conventions
-----------

A few more conventions are important to know:

* Missing data is left empty.

* There is no unit transformation within the model, i.e. the user needs to ensure the consistency of units. In the plotting functions MW, MWh, EUR/MWh etc. are used as units. Therefore, please provide your data in just these units if you want to use the plotting functions. In the future we would like to drop this restriction.

* The parameters :attr:`id_scal` and :attr:`id_ts` are optional and will be added automatically if you do not specify them.

* The parameter :attr:`name` must be specified in a certain fixed concatenation of parameters: :attr:`region`-:attr:`carrier`-:attr:`tech` (example: :attr:`B-biomass-gt`).

* If :attr:`region` is set to :attr:`ALL` in the model-own assumptions, :attr:`name` is to be left blank. The name will be automatically added per region modelling the energy system.

* Different attributes can be set for :attr:`var_name`. oemof-B3 can process

  * attributes of the components in oemoflex (which component is assigned to which attributes can be found in chapter `Overview <https://oemoflex.readthedocs.io/en/latest/overview.html>`_ of the :attr:`oemoflex` documentation) and
  * attributes needed to calculate annuized costs. For this, :attr:`capacity_cost_overnight`, :attr:`storage_capacity_cost_overnight`, :attr:`wacc`, :attr:`lifetime` and :attr:`fixom_cost` must be passed with :attr:`var_name`.

* Components can receive keywords for the electricity-gas-relation-constraint via the attribute :attr:`output_parameters`.

  * Keywords of components powered by gas start with :attr:`config.settings.optimize.gas_key` and
  * such powered with electricity with :attr:`config.settings.optimize.el_key` followed by :attr:`carrier` and :attr:`region` (example: :attr:`{"electricity-heat_decentral-B": 1}`).
  * Do not provide :attr:`output_parameters` or leave their :attr:`var_value` empty to neglect a component in the constraint.

* The capacity of specific components of a scenario can be expanded during an optimization, if the facade attribute `expandable` is set on `True`.

  * To adjust this setting, the attribute needs to be specified in the file :attr:`costs_efficiencies.csv`.
  * An overview of all facades, which includes `expandable` can be found in the facade attributes overview <https://oemof-tabular.readthedocs.io/en/latest/facades.html#>`_ provided by oemof.tabular.

* The maximum capacity and the already installed capacity of specific components can be set individually

  * In the file :attr:`capacities.csv`, the already installed capacity can be set as 0 for
    a Greenfield assumption or as a positive numeric value for a Brownfield assumption.
    Changes can be done for the attribute :attr:`capacity` in :attr:`var_name`.
  * In the file :attr:`potentials.csv`, the maximum capacity can be set as a positive numeric value
    for the attribute :attr:`capacity_potential` in :attr:`var_name`. If the
    :attr:`capacity_potential` is left empty, an infinite capacity potential is assumed.

.. _prepare_resources_label:

Prepare resources
=================

Rules
-----

.. toctree::
   :maxdepth: 1
   :glob:

   prepare_resources/*


Outputs
-------

Output files are saved in :file:`results/_resources`.

The resources are preprocessed data that serve as material for building scenarios.
They are a first intermediate result in oemof-B3 and follow the schema presented in section :ref:`Schema`.


.. _build_datapackages_label:

Build datapackages
==================

Rules
-----

.. toctree::
   :maxdepth: 1
   :glob:

   build_datapackage/*

Outputs
-------

Output files are saved in :file:`results/scenario/preprocessed`.

Next intermediate results are preprocessed datapackage, which is built using resources,
scenario information and the information about the model structure.
A preprocessed datapackage represents an instance of an :class:`oemof.solph.EnergySystem`.

A datapackage is a collection of data in form of csv-files and metadata in form of a json.
The data consists of one file for all busses and one for each
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
the scenario information :file:`scenarios/<scenario>.yml` and the `model structure <https://github.com/rl-institut/oemof-B3/tree/dev/oemof_b3/model/model_structure>`_.

Components and their attributes are defined in
`oemoflex <https://github.com/rl-institut/oemoflex/tree/dev/oemoflex/model/component_attrs.yml>`_.
Components and properties can also be added or updated in oemof-B3 using the files in :file:`oemof_b3/model/`.

Optimization
============

Rules
-----

.. toctree::
   :maxdepth: 1
   :glob:

   optimization/*

Outputs
-------

Output files are saved in :file:`results/scenario/optimized`.

The results are optimized energy systems.

.. _postprocessing_label:

Postprocessing
==============

Rules
-----

.. toctree::
   :maxdepth: 1
   :glob:

   postprocessing/*

Outputs
-------

Output files are saved in :file:`results/scenario/postprocessed`.

Data postprocessing makes use of oemoflex's functionality, thus postprocessed data follows its
data format. See oemoflex' documention on
`postprocessed results <https://oemoflex.readthedocs.io/en/latest/overview.html#postprocess-results>`_
for further information.

.. _visualization_label:

Visualization
=============

Rules
-----

.. toctree::
   :maxdepth: 1
   :glob:

   visualization/*

Outputs
-------

Output files are saved  in :file:`results/scenario/plotted`.

.. _oep_upload_download_label:

OEP upload/download
=====================

Rules
-----

.. toctree::
   :maxdepth: 1
   :glob:

   oep_upload_download/*
