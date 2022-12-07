.. _how_to_customize_oemof-B3_label:

~~~~~~~~~~~~~~~~~~~~~~~~~
How to customize oemof-B3
~~~~~~~~~~~~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top

To use oemof-B3, you may want to modify some files, depending on what you want to model.

While you define scenarios in the directory :attr:`scenarios`, you can specify the structure of
your model in the directory :attr:`model`.
In the directory :attr:`config` you can furthermore choose or modify labels, hard coded constant
parameters or colors within plots.

Scenarios
---------
For each scenario you define, you create a YAML-file within :attr:`scenarios`.
You have to provide a name and a label of your scenario.
Inside the fields at :attr:`datetimeindex` you specify which time period is examined in your scenario.
With :attr:`start` you define the start date and time. It must be given in the ISO 8601 format.
With :attr:`freq` you set the frequency  in e.g. "H" (hours) and with :attr:`periods` the number of time steps.

In :attr:`model_structure` you pass the structure of your energy system (see section :ref:`model`).
With :attr:`paths_scalars` and :attr:`paths_scalars` you provide all paths to your scalar and time
series data.
A filter selection is specified for scalar data in :attr:`filter_scalars` and for time series in
:attr:`filter_timeseries`. Time series additionally can be filtered by a start time index.
For both, keys of scenarios are passed with :attr:`scenario_key`. These are used to filter the raw
data according to the corresponding keys. This way you can assign different values to attributes
or assign a different time series depending on the scenario.
If you want to calculate only one scenario, you can use a single :attr:`scenario_key`.

.. _model_scenario_setup_label:

Model
-----

The :attr:`model` directory is structured as follow:

.. code-block::

    model
    ├── model_structure
    │     ├── model_structure_el_only.yml
    │     ├── model_structure_full.yml
    ├── bus_attrs_update.yml
    ├── component_attrs_update.yml
    ├── foreign_keys_update.yml
    ├── __init__.py

Within directory :attr:`model_structure` you'll find the structure of the whole energy system used
in oemof-B3 and the one with electricity sector only.
You can also set up your own energy system in a new YAML file.

In the parent directory :attr:`model` buses are stored in :attr:`bus_attrs_update.yml` which
differ from the default in oemoflex (compare
`busses.yml in oemoflex <https://github.com/rl-institut/oemoflex/blob/dev/oemoflex/model/busses.yml>`_).
The same applies to the files :attr:`component_attr_update.yml` and :attr:`foreign_keys.yml`.
These are extended for the energy system in oemof-B3 (or depending on the composition of your
energy system) with information deviating from the default in oemoflex (cf.
`component_attrs <https://github.com/rl-institut/oemoflex/blob/dev/oemoflex/model/component_attrs.yml>`_
and
`foreign_keys.yml <https://github.com/rl-institut/oemoflex/blob/dev/oemoflex/model/foreign_keys.yml>`_)

Configuration
--------------------

The :attr:`config` directory is structured as follow:

.. code-block::

    config
    ├── labels
    │     ├── de.yml
    │     ├── en.yml
    ├── __init__.py
    ├── colors.csv
    ├── colors.yml
    ├── config.py
    ├── settings.yml

Within directory :attr:`labels` there are YAML-files which contain labels.
They are used in some of the visualization scripts (cf. :ref:`Visualization`).
The  labels are assigned to the keys of the components stored in
:attr:`component_attrs_update.yml`.
In the parent directory :attr:`config` colors are stored in the files :attr:`colors.yml`
and :attr:`colors.csv`. While :attr:`colors.yml` uses keys from
:attr:`component_attrs_update.yml`, :attr:`colors.csv` expects the labels of these keys.
In :attr:`settings.yml`, besides assumptions and values taken as constant, paths and settings in
oemof-B3 are stored.
