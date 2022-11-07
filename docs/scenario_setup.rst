.. _scenario_setup_label:

~~~~~~~~~~~~~~
Scenario setup
~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top

To use oemof-B3, you may want to modify some files, depending on the setup of your Energy System.

While you define scenarios in the directory :attr:`scenarios`, you can specify the structure of
your model in the directory :attr:`model`.
In the directory :attr:`config` you can furthermore choose or modify labels, hard coded constant
parameters or colors within plots.

scenarios
---------
For each scenario you define, you create a YAML-file within :attr:`scenarios`.
You have to provide a name and a label of your scenario.
Inside the fields at :attr:`datetimeindex` you specify which time period is examined in your scenario.
With :attr:`start` you define the start date and time. It must given in the ISO 8601 format.
With :attr:`freq` you set the frequency  in e.g. "H" (hours) and with :attr:`periods` the number of time steps.

In :attr:`model_structure` you pass the structure of your energy system (see section :ref:`model`).
With :attr:`paths_scalars` and :attr:`paths_scalars` you provide all paths to your scalar and time
series data.
A filter selection is specified for scalar data in :attr:`filter_scalars` and for time series in
:attr:`filter_timeseries`.
For both, keys of scenarios are passed with :attr:`scenario_key`. These are used to filter the raw
data according to the corresponding keys. You can

Time series additionally can be filtered by a start time index.


.. _model_scenario_setup_label:
model
-----

config
------