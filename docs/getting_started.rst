.. _getting_started_label:

~~~~~~~~~~~~~~~
Getting started
~~~~~~~~~~~~~~~

Using oemof-B3
==============


Installation
------------

Currently, oemof-B3 needs python 3.8, 3.9 or 3.10 (newer versions may be supported, but installation can take very long).

Additionally, you need to install the python dependency manager `poetry <https://python-poetry.org/>`_.
It is recommended to install poetry system-wide via the command below or
`pipx <https://python-poetry.org/docs/#installing-with-pipx>`_:

::

    curl -sSL https://install.python-poetry.org | python3 -
    poetry install


**In order to install oemof-B3, proceed with the following steps:**

1. Clone oemof-B3 into local folder:

::

    git clone git@github.com:rl-institut/oemof-B3.git

2. Enter folder

::

    cd oemof-B3

3. Create virtual environment using conda:

::

    conda env create environment.yml

4. Activate environment:

::

    conda activate oemof-B3

5. Install oemof-B3 package using poetry, via:

::

    poetry install

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


How to install geopandas
------------------------
Geopandas is necessary in `oemof-B3` for a small subset of the modeling steps. Therefore it is part
of the extras requirements. To install geopandas execute

::

    poetry install -E preprocessing


The installation of geopandas on **Windows** can be challenging. According to the geopandas documentation (https://geopandas.org/getting_started/install.html) there are multiple ways to install it. We recommend to use the conda-forge channel:

Simply type

::

    conda install --channel conda-forge geopandas

in the Anaconda prompt.


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

To run the model, raw input data has to be downloaded from zenodo first via:

::

    snakemake -j1 download_raw_data

To use preprocessed resources from the OEP instead, set `prepare_resources_locally: False` in
`oemof_b3.config.settings.yaml`.

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

The calculations of scenarios in the :file:`results` directory can be deleted on Darwin/macOS
systems by executing the following rule:

::

    snakemake -j1 clean

To remove all scenario results on a Windows based system, the following rule can be executed:

::

    snakemake -j1 clean_on_win_sys

Contributing to oemof-B3
========================

You can use oemof-B3 to calculate your own scenarios.
To adapt the energy system of Brandenburg and Berlin according to your requirements, a modification
of the componentes in the subdirectory oemof_b3 can be done.
But you can also modify oemof_b3 to define your own energy system of another city or district.
For all these use cases, the data in the raw directory
must be adapted. For this purpose, it is advisable to have energy system-specific empty scalar data
and time series created for each scenario. See further information in :ref:`How to customize oemof-B3`.

Executing the rule

::

    snakemake -j1 create_empty_scalars

will create empty scalars.

The rule

::

    snakemake -j1 create_empty_ts

will create empty time series data.
The empty scalars and time series data can be used to verify your energy system model in the preprocessing stage.

You can write `issues <https://github.com/rl-institut/oemof-B3/issues>`_ to announce bugs or
to propose enhancements.
