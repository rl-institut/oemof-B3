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


Installation
------------

Currently, oemof-B3 needs python 3.7 or 3.8 (newer versions may be supported, but installation can take very long).

In order to install oemof-B3, proceed with the following steps:

- git-clone oemof-B3 into local folder: `git clone https://github.com/rl-institut/oemof-B3.git`
- enter folder
- create virtual environment using conda: `conda env create environment.yml`
- activate environment: `conda activate oemof-B3`
- install oemof-B3 package using poetry, via: `poetry install`

Alternatively, you can create a virtual environment using other approaches, such as `virtualenv`.

To create reports oemof-B3 requires pandoc (version > 2). Pandoc is included in conda environment config (environment.yml).
If the environment is build otherwise, pandoc must be installed manually. It can be installed following instructions from
`Pandoc Installation <https://pandoc.org/installing.html>`_.

To test if everything works, you can run the examples. To do this, please follow the instructions in chapter :ref:`examples`.


For developers: Please activate pre-commit hooks (via `pre-commit install`) in order to follow our coding styles.

Required: An LP-solver
----------------------

To use `oemof-solph`, which does the energy system optimization in oemof-B3,
a LP/MILP solver must be installed.
To use the CBC solver install the `coinor-cbc` package. For further details, read the
`installation instructions on
oemof.solph <https://oemof-solph.readthedocs.io/en/latest/readme.html#installing-a-solver>`_.

If you have installation problems, consider opening an
`issue <https://github.com/rl-institut/oemof-B3/issues>`_.


How to install geopandas under Windows
--------------------------------------
Geopandas is necessary in `oemof-B3` for a small subset of the modeling steps. Therefore it is part of the extras requirements.
The installation of geopandas on Windows can be challenging. According to the geopandas documentation (https://geopandas.org/getting_started/install.html) there are multiple ways to install it. We recommend to use the conda-forge channel:

Simply type

::

    conda install --channel conda-forge geopandas

in the Anaconda prompt.


Required data
-------------

Raw input data is currently **not** provided with the github repository but will be published at a
later stage. More information about the raw data format can be found here: :ref:`Raw data`


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
- Split large data-/workflow into single steps, defined by rules
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


.. _how_to_run_model_label:

How to run the model
--------------------

Snakemake on Linux
^^^^^^^^^^^^^^^^^^

To run the scenarios, execute:

::

     snakemake -j<NUMBER_OF_CPU_CORES> run_all_scenarios


Alternatively you can run a single scenario with:

::

     snakemake -j<NUMBER_OF_CPU_CORES> results/<scenario_name>/postprocessed

whereby scenario_name corresponds to the name in the YAML file of the respective scenario in the scenarios directory.
To run the scenarios, the corresponding raw data in the raw directory is required.

.. note:: Please note that the debug mode is activated as default. This will execute only three time steps of the optimization. To turn off the debug mode you need to set debug to `false` in :file:`oemof_b3/config/settings.yaml`.


Alternatively, to create just the output file or directory of one rule, run:

::

     snakemake -j<NUMBER_OF_CPU_CORES> <output file or folder>


Snakemake on Windows
^^^^^^^^^^^^^^^^^^^^

When running snakemake with output files in subfolders on Windows with

::

     snakemake -j<NUMBER_OF_CPU_CORES>

a ``MissingRuleException`` is raised. The process is unable to specify the output files in subfolders.
This bug is an `open issue <https://github.com/snakemake/snakemake/issues/46>`_
in snakemake.
A current workaround is described in `pypsa-eur <https://pypsa-eur.readthedocs.io/en/latest/tutorial.html?highlight=windows#how-to-use-the-snakemake-rules>`_.
is to run snakemake with the flag ``--keep-target-files`` to the command.

::

     snakemake -j<NUMBER_OF_CPU_CORES> --keep-target-files


Contributing to oemof-B3
========================

You can write `issues <https://github.com/rl-institut/oemof-B3/issues>`_ to announce bugs or
to propose enhancements.
