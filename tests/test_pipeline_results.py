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

scenario_groups = [
    "examples",
    "all-scenarios",
    "all-custom-order",
    "all-optimized",
]

for scenario in scenarios:

    output_rule_list = [
        "results/" + scenario + "/preprocessed",
        "results/" + scenario + "/optimized",
        "results/" + scenario + "/postprocessed",
        "results/" + scenario + "/b3_results/data",
        "results/" + scenario + "/tables",
        "results/" + scenario + "/plotted/dispatch",
        "results/" + scenario + "/plotted/storage_level",
        "results/" + scenario + "/plotted/scalars",
        "results/" + scenario + "/report",
    ]

for scenario_group in scenario_groups:
    output_rule_list = [
        "results/joined_scenarios/" + scenario_group + "/joined",
        "results/joined_scenarios/" + scenario_group + "/joined_tables",
        "results/joined_scenarios/" + scenario_group + "/joined_plotted",
    ]

# snakemake -j1 prepare_re_potential
output_rule_list = ["results/_resources/RE_potential"]
