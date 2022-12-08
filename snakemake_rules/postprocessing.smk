rule postprocess:
    input: "results/{scenario}/optimized"
    output: directory("results/{scenario}/postprocessed/")
    params:
        logfile="results/{scenario}/{scenario}.log"
    shell: "python scripts/postprocess.py {input} {wildcards.scenario} {output} {params.logfile}"

def get_scenarios_in_group(wildcards):
    return [os.path.join("results", scenario, "postprocessed") for scenario in scenario_groups[wildcards.scenario_group]]

rule join_scenario_results:
    input: get_scenarios_in_group
    output: directory("results/joined_scenarios/{scenario_group}/joined/")
    shell: "python scripts/join_scenarios.py {input} {output}"

rule map_results_to_b3_format:
    input:
        "results/{scenario}/postprocessed"
    output:
        directory("results/{scenario}/b3_results/data")
    params:
        logfile="results/{scenario}/{scenario}.log"
    shell:
        "python scripts/map_results_to_b3_format.py {input} {output} {params.logfile}"
