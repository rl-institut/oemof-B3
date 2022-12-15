rule download_resources:
    output:
        "results/_resources/ts_feedin.csv",
        "results/_resources/ts_load_electricity.csv",
        "results/_resources/ts_load_electricity_vehicles.csv",
        "results/_resources/scal_costs_efficiencies.csv",
        "results/_resources/ts_efficiency_heatpump_small.csv",
        "results/_resources/scal_load_heat.csv",
        "results/_resources/ts_load_heat.csv",
        "results/_resources/scal_power_potential_wind_pv.csv",
    shell: "python scripts/download_resources.py {output}"

rule download_all_resources:
    input: rules.download_resources.output