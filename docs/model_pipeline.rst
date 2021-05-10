.. _model_pipeline_label:

~~~~~~~~~~~~~~
Model pipeline
~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 2
    :local:
    :backlinks: top


Separation of processing steps
==============================

The modeling of energy systems in most cases entails multiple distinct steps with different
processing times (e.g. computations, aggregation, filtering in preprocessing, optimization,
establishing derived results, plots and reports in postprocessing).

Separating these steps allows to work on a certain part of the model pipeline without having to
re-run all steps that are not affected by it. This can save a lot of time.

Apart from the complex workflow in energy system modelling itself, open-source software should aim for 
long lasting impact. To achieve this sustainable impact with software dealing with data analysis,
three concepts should be considered: reproducibility, adaptability and transparency.
The first allows technical validation and regeneration of results. It is widely recognized in data analyses.
The latter two should be equally important. 
Adaptability refers to the ability to modify the analysis to answer extended or slightly different
research questions.
Transparency is necessary to judge whether the analysis is not only technically, but methodologically valid.
:cite:`Molder.2021`

Thus, a separation of processing steps is very useful in energy system modelling. 
There are different tools which provide such a workflow management. 
In the oemof-B3 model, the tool snakemake is used.


Workflow management with Snakemake
==================================

Visit the `snakemake docs <>_` to learn more about snakemake and how to install it.


How can snakemake help at workflow management?
----------------------------------------------

The main characteristics of snakemake :cite:`Molder.2021` are

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
- ...
    
Snakemake on Windows
--------------------

When running snakemake with outputfiles in subfolders on Windows with

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


Preprocessing
=============

.. toctree::
   :maxdepth: 1
   :glob:

   preprocessing/*


Optimization
============

.. toctree::
   :maxdepth: 1
   :glob:


Postprocessing
==============

.. toctree::
   :maxdepth: 1
   :glob:
