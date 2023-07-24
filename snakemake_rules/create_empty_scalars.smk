rule create_empty_scalars:
    input: "scenarios/"
    output: "raw/scalars/empty_scalars.csv"
    shell: "python scripts/create_empty_scalars.py {input} {output}"