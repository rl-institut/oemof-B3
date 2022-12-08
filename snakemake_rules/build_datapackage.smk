from oemof_b3.config.config import load_yaml

def get_paths_scenario_input(wildcards):
    scenario_specs = load_yaml(f"scenarios/{wildcards.scenario}.yml")
    paths_scenario_inputs = list()
    for key in ["paths_scalars", "paths_timeseries"]:
        paths = scenario_specs[key]
        if isinstance(paths, list):
            paths_scenario_inputs.extend(paths)
        elif isinstance(paths, str):
            paths_scenario_inputs.append(paths)
    return paths_scenario_inputs

rule build_datapackage:
    input:
        get_paths_scenario_input,
        scenario="scenarios/{scenario}.yml"
    output: directory("results/{scenario}/preprocessed")
    params:
        logfile="results/{scenario}/{scenario}.log"
    wildcard_constraints:
        # Do not use this rule for the examples. Use prepare_example instead
        scenario=r"(?!example_).*"
    shell: "python scripts/build_datapackage.py {input.scenario} {output} {params.logfile}"
