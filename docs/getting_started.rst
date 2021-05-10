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


Required data
-------------

Raw input_data is currently **not** provided with the github repository but will be published at a
later stage:

.. todo: Link to the section that explains raw data.

Contributing to oemof-B3
========================

You can write `issues <https://github.com/rl-institut/oemof-B3/issues>`_ to announce bugs or
to propose enhancements.