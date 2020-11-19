.. _postprocessing_label:

~~~~~~~~~~~~~~
Postprocessing
~~~~~~~~~~~~~~

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top


The results of the optimization have to be postprocessed to be fully useful. The following derived
results are most important.

flow_in
    Flow into the component

flow_out
    Flow out of the component

losses_storage
    flow_in - storage_content - flow_out

losses_transmission
    gross_flow - net_flow ?

capacity
    TODO

capacity_invest
    TODO

storage_capacity
    storage_capacity

storage_capacity_invest

cost_invest
    capacity_cost * invest

cost_marginal
    marginal_cost * flow_out

cost_carrier
    carrier_cost * flow_in

total_system_cost
    Sum of cost_invest, cost_marginal, cost_carrier

re_generation
    Sum of all flow_out to electricity from renewables

emissions
    Not part of the current data structure

cost_emission
    Not part of the current data structure
