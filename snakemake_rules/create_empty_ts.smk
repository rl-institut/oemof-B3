rule create_empty_ts:
    input: directory("scenarios/")
    output:
        "raw/time_series/empty_ts_load.csv",
        "raw/time_series/empty_ts_feedin.csv",
        "raw/time_series/empty_ts_efficiencies.csv"

    shell: "python scripts/create_empty_ts.py {input} {output[0]} {output[1]} {output[2]}"