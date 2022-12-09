rule optimize:
    input: "results/{scenario}/preprocessed"
    output: directory("results/{scenario}/optimized/")
    params:
        logfile="results/{scenario}/{scenario}.log"
    shell: "python scripts/optimize.py {input} {output} {params.logfile}"
