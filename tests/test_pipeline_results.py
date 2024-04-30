# Delete data from test run of pipeline if True otherwise False
delete_switch = True

scenarios = [
    "2050-100-el_eff",
    "2050-95-el_eff",
    "2050-80-el_eff",
    "2050-100-gas_moreCH4",
    "2050-95-gas_moreCH4",
    "2050-80-gas_moreCH4",
]

for scenario in scenarios:

    output_rule_list = [
        "results/" + scenario + "/preprocessed",
        "results/" + scenario + "/optimized",
        "results/" + scenario + "/postprocessed",
        # "results/joined_scenarios/{scenario_group}/joined",
        "results/" + scenario + "/b3_results/data",
        "results/" + scenario + "/tables",
        # "results/joined_scenarios/{scenario_group}/joined_tables",
        "results/" + scenario + "/plotted/dispatch",
        "results/" + scenario + "/plotted/storage_level",
        "results/" + scenario + "/plotted/scalars",
        # "results/joined_scenarios/{scenario_group}/joined_plotted",
        "results/" + scenario + "/report",
    ]
