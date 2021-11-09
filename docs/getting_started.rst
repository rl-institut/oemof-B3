.. _getting_started_label:

~~~~~~~~~~~~~~~
Getting started
~~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top

Using oemof-B3
==============


Installing the latest (dev) version
-----------------------------------

Clone oemof-B3 from github:

::

    git clone git@github.com:rl-institut/oemof-B3.git


Now you can install your local version of oemof-B3 using pip:

::

    pip install -e <path/to/oemof-B3/root/dir>


Requirements
------------
1. To use `oemof-solph`, which does the energy system optimization in oemof-B3,
   a LP/MILP solver must be installed.
   To use the CBC solver install the `coinor-cbc` package. For further details, read the
   `installation instructions on
   oemof.solph <https://oemof-solph.readthedocs.io/en/latest/readme.html#installing-a-solver>`_.

2. oemof-B3 needs `oemof-tabular` for data preprocessing.
   If you install oemof-b3 locally, the current dev version of oemof.tabular will automatically
   be installed.

If you have installation problems, consider opening an
`issue <https://github.com/rl-institut/oemof-B3/issues>`_.


How to install geopandas under Windows
--------------------------------------
The installation of geopandas on Windows can be challenging. According to the geopandas documentation (https://geopandas.org/getting_started/install.html) there are multiple ways to install it. It is recommended to use one of the following ways:

1) Using the conda-forge channel

Simply type

::

    conda install --channel conda-forge geopandas

in the Anaconda prompt


2) Creating a new environment

Due to possible conflicts caused by installing other geospatial packages from different channels, it can be easier to install geopandas and its dependencies in a clean environment.

The following commands create a new environment with the name geo_env, configures it to install packages always from conda-forge, and installs GeoPandas in it:

::

    conda create -n geo_env

    conda activate geo_env

    conda config --env --add channels conda-forge

    conda config --env --set channel_priority strict

    conda install python=3 geopandas


Required data
-------------

Raw input_data is currently **not** provided with the github repository but will be published at a
later stage:

.. todo: Link to the section that explains raw data.


Workflow management with snakemake: Separating the steps
--------------------------------------------------------

The modeling of energy systems in most cases entails multiple distinct steps with different
processing times (e.g. computations, aggregation, filtering in preprocessing, optimization,
establishing derived results, plots and reports in postprocessing).

Separating these steps allows to work on a certain part of the model pipeline without having to
re-run all steps that are not affected by it. This can save a lot of time.

The model oemof-B3 uses snakemake to keep the
execution of these steps reproducible, adaptable and transparent. Visit the
`snakemake docs <https://snakemake.readthedocs.io/en/stable/>`_ to learn more about snakemake and
how to install it.


How can snakemake help at workflow management? The main characteristics of snakemake
:cite:`Molder.2021` are:

- Lightweight workflow management
- Text-based, python syntax
- split large data-/workflow into single steps, defined by rules
- Infers dependencies and execution order (DAG)
- Reproducible and scalable data analyses
- Supported languages: BASH commands, Python, Inline python code, R script, R markdown files

More features which facilitate the workflow management are

- Parallelization (threads, can be even run on clusters such as AWS S3)
- Resource allocation (entire workflow or per rule)
- Suspend and resume
- Logging
- Modularity
- Report generation

Snakemake on Linux
------------------

To run all example scenarios, execute:

::

     snakemake -j<NUMBER_OF_CPU_CORES> run_all_examples

Alternatively, to create just the output file or directory of one rule, run:

::

     snakemake -j<NUMBER_OF_CPU_CORES> <output file or folder>

Snakemake on Windows
--------------------

When running snakemake with output files in subfolders on Windows with

::

     snakemake -j<NUMBER_OF_CPU_CORES>

a ``MissingRuleException`` is raised. The process is unable to specify the output files in subfolders.
This bug is an `open issue <https://github.com/snakemake/snakemake/issues/46>`_
at `snakemake <https://snakemake.readthedocs.io/>`_.
The `current workaround <https://pypsa-eur.readthedocs.io/en/latest/tutorial.html?highlight=windows#how-to-use-the-snakemake-rules>`_
described in `pypsa-eur <https://pypsa-eur.readthedocs.io/en/latest/index.html>`_
is to run snakemake with the flag ``--keep-target-files`` to the command.

::

     snakemake -j<NUMBER_OF_CPU_CORES> --keep-target-files


Contributing to oemof-B3
========================

You can write `issues <https://github.com/rl-institut/oemof-B3/issues>`_ to announce bugs or
to propose enhancements.