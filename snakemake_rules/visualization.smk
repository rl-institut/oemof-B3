rule table_costs_efficiencies:
    input: "raw/scalars/costs_efficiencies.csv"
    output: "results/_tables/technical_and_cost_assumptions_{scenario_key}.csv"
    params:
        logfile="results/_tables/technical_and_cost_assumptions_{scenario_key}.log"
    shell: "python scripts/table_costs_efficiencies.py {input} {wildcards.scenario_key} {output} {params.logfile}"

rule table_results:
    input: "results/{scenario}/postprocessed/"
    output: directory("results/{scenario}/tables/")
    params:
        logfile="results/{scenario}/{scenario}.log"
    shell: "python scripts/table_results.py {input} {output} {params.logfile}"

rule table_joined_results:
    input: "results/joined_scenarios/{scenario_group}/joined/"
    output: directory("results/joined_scenarios/{scenario_group}/joined_tables/")
    params:
        logfile="results/joined_scenarios/{scenario_group}/{scenario_group}.log"
    shell: "python scripts/table_results.py {input} {output} {params.logfile}"

rule plot_dispatch:
    input: "results/{scenario}/postprocessed/"
    output: directory("results/{scenario}/plotted/dispatch")
    params:
        logfile="results/{scenario}/{scenario}.log"
    shell: "python scripts/plot_dispatch.py {input} {output} {params.logfile}"

rule plot_storage_level:
    input: "results/{scenario}/postprocessed/"
    output: directory("results/{scenario}/plotted/storage_level")
    params:
        logfile="results/{scenario}/{scenario}.log"
    shell: "python scripts/plot_storage_levels.py {input} {output} {params.logfile}"

rule plot_conv_pp_scalars:
    input:
        data="results/_resources/{resource}.csv",
    output: "results/_resources/plots/{resource}-{var_name}.png"
    shell: "python scripts/plot_conv_pp_scalars.py {input.data} {wildcards.var_name} {output}"

rule plot_scalar_results:
    input: "results/{scenario}/postprocessed/"
    output: directory("results/{scenario}/plotted/scalars/")
    params:
        logfile="results/{scenario}/{scenario}.log"
    shell: "python scripts/plot_scalar_results.py {input} {output} {params.logfile}"

rule plot_joined_scalars:
    input: "results/joined_scenarios/{scenario_group}/joined/"
    output: directory("results/joined_scenarios/{scenario_group}/joined_plotted/")
    params:
        logfile="results/joined_scenarios/{scenario_group}/{scenario_group}.log"
    shell: "python scripts/plot_scalar_results.py {input} {output} {params.logfile}"

rule report:
    input:
        template="report/report.md",
        template_interactive="report/report_interactive.md",
        plots_scalars="results/{scenario}/plotted/scalars",
        plots_dispatch="results/{scenario}/plotted/dispatch",
    output:
        directory("results/{scenario}/report/")
    params:
        logfile="results/{scenario}/{scenario}.log",
        all_plots="results/{scenario}/plotted/",
    run:
        import os
        import shutil
        import platform

        os.makedirs(output[0])
        shutil.copy(src=input[0], dst=output[0])
        shutil.copy(src=input[1], dst=output[0])

        if platform.system() == "Linux" or platform.system() == "Darwin":
            # static pdf report
            shell(
            """
            pandoc -V geometry:a4paper,margin=2.5cm \
            --lua-filter report/pandoc_filter.lua \
            --resource-path={params.all_plots} \
            --metadata title="Results for scenario {wildcards.scenario}" \
            {output}/report.md -o {output}/report.pdf
            """
            )
            # static html report
            shell(
            """
            pandoc --resource-path={params.all_plots} \
            --lua-filter report/pandoc_filter.lua \
            --metadata title="Results for scenario {wildcards.scenario}" \
            --self-contained -s --include-in-header=report/report.css \
            {output}/report.md -o {output}/report.html
            """
            )
            # interactive html report
            shell(
            """
            pandoc --resource-path={params.all_plots} \
            --lua-filter report/pandoc_filter.lua \
            --metadata title="Results for scenario {wildcards.scenario}" \
            --self-contained -s --include-in-header=report/report.css \
            {output}/report_interactive.md -o {output}/report_interactive.html
            """
            )
            os.remove(os.path.join(output[0], "report.md"))
            os.remove(os.path.join(output[0], "report_interactive.md"))

        elif platform.system() == "Windows":
            raise UserWarning("Sorry, at the moment the report is not available for Windows users.")
        else:
            raise UserWarning("Sorry, the report is not supported for the system you are using. "
                              "Please use either a Linux or a Darwin System.")
