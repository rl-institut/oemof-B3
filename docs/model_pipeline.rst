.. _model_pipeline_label:

~~~~~~~~~~~~~~
Model pipeline
~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 2
    :local:
    :backlinks: top

The main functionality of oemof-B3 is a data processing pipeline which is managed using snakemake.
The pipeline preprocesses raw data into scalar and time series resources that is used to
build tabular datapackages representing single energy system optimization problems. These can be
understood by `oemof.tabular <https://github.com/oemof/oemof-tabular>`_ and optimized by
`oemof.solph <https://github.com/oemof/oemof-solph>`_. In the next steps, the results of the
optimization are postprocessed and plotted. The individual steps are documented in detail in the
following sections.

.. 	image:: _img/model_pipeline.svg
   :scale: 100 %
   :alt: schematic of model pipeline
   :align: center

.. created with snakemake --rulegraph process_all_scenarios plot_grouped_scenarios plot_all_examples | dot -Tpdf > docs/_img/model_pipeline.svg

The subdirectories of oemof-B3 shown below contain configurations and data of the model.
:file:`Examples` contains pre-fabricated datapackages that can readily be optimized. The directory
:file:`scenarios` contains :file:`.yml`-files defining individual scenarios. Raw data is not part
of the repo and has to be provided in :file:`raw`. Intermediate and final results will be saved in
:file:`results`. Logs are saved in :file:`logs`.

.. code-block::

    .
    ├── examples
    ├── logs
    ├── oemof_b3
    │     ├── config
    │     ├── model
    │     ├── schema
    ├── raw
    ├── results
    ├── scenarios


Prepare resources
=================

.. toctree::
   :maxdepth: 1
   :glob:

   prepare_resources/*

Output files are saved in :file:`results/_resources`.

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

Build datapackages
==================

.. toctree::
   :maxdepth: 1
   :glob:

   build_datapackage/*

Output files are saved in :file:`results/scenario/preprocessed`.

Next intermediate results are preprocessed datapackage, which is built using resources,
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

Optimization
============

.. toctree::
   :maxdepth: 1
   :glob:

   optimization/*

Output files are saved in :file:`results/scenario/optimized`.

The results are optimized energy systems

Postprocessing
==============

.. toctree::
   :maxdepth: 1
   :glob:

   postprocessing/*

Output files are saved in :file:`results/scenario/postprocessed`.

Plotting
==============

.. toctree::
   :maxdepth: 1
   :glob:

   plotting/*

Output files are saved  in :file:`results/scenario/plotted`.
