rule upload_results_to_oep:
    input: "results/{scenario}/b3_results/data"
    output: directory("results/{scenario}/b3_results/metadata")
    params:
        logfile="results/{scenario}/{scenario}.log",
        name_prefix="results_{scenario}",
        title_prefix="Model_results_oemof-B3_{scenario}"
    shell: "python scripts/upload_b3_data_to_oep.py {input} {output} {params.name_prefix} {params.title_prefix} {params.logfile}"

rule upload_resources_to_oep:
    input: "results/_resources"
    output: directory("results/_resources/metadata")
    params:
        logfile="results/_resources/upload_resources_to_oep.log",
        name_prefix="resources",
        title_prefix="Prepared_resources_for_oemof-B3"
    shell: "python scripts/upload_b3_data_to_oep.py {input} {output} {params.name_prefix} {params.title_prefix} {params.logfile}"