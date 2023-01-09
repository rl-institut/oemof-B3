rule create_empty_scalars:
    input: "scenarios/{scenario}.yml"
    output: "raw/scalars/scalars_{scenario}.csv"
    shell: "python scripts/create_empty_scalars.py {input} {output}"
