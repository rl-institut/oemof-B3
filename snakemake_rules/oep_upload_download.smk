rule upload_results_to_oep:
    input: "results/{scenario}/b3_results/data"
    output: directory("results/{scenario}/b3_results/metadata")
    params:
        logfile="results/{scenario}/{scenario}.log"
    shell: "python scripts/upload_results_to_oep.py {input} {output} {params.logfile}"