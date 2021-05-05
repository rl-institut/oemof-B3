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


Now you can install it your local version of oemoflex using pip:

::

    pip install -e <path/to/oemof-B3/root/dir>


Requirements
------------
1. To use `oemof-solph`, the core of oemof-B3, a LP/MILP solver must be installed.
   To use the CBC solver install the `coinor-cbc` package:

   ::

    apt-get install coinor-cbc

2. oemof-B3 needs `oemof-tabular` for data preprocessing.
   Please install the dev version from github rather than installing from PyPi/pip.

   ::

    git clone https://github.com/oemof/oemof-tabular.git
    cd oemof-tabular/
    git checkout dev
    pip install -e ./


.. for the moment, as a todo:

(for further installing issues and their solution, see https://github.com/rl-institut/oemof-B3/issues)


Required data
-------------

**Not** provided with the github repository:

* Raw input data, see :ref:`input data format`.
* Output template data, see :ref:`postprocessing`.

Contributing to oemof-B3
========================

You can write issues to announce bugs or errors or to propose
enhancements.