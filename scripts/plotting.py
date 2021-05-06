import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots

if __name__ == "__main__":
    postprocessed = sys.argv[1]
    plotted = sys.argv[2]

    # create the directory plotted where all plots are saved
    os.makedirs(plotted)

    bus_directory = os.path.join(postprocessed, "sequences/bus/")
    bus_files = os.listdir(bus_directory)
    for i in bus_files:
        if "electricity" in i:
            electricity_bus_file = i
            electricity_bus_name = os.path.splitext(electricity_bus_file)[0]
            electricity_bus_path = os.path.join(bus_directory, electricity_bus_file)

            data = pd.read_csv(electricity_bus_path, header=[0, 1, 2], parse_dates=[0], index_col=[0])

            fig, ax = plt.subplots(figsize=(12, 5))
            data = plots.eng_format(ax, data, 'W', 1000)

            start_date = '2019-12-01 00:00:00'
            end_date = '2019-12-13 23:00:00'
            plots.plot_dispatch(ax=ax, df=data, start_date=start_date, end_date=end_date,
                                bus_name=electricity_bus_name, demand_name='BB-electricity-demand')

            plt.legend(loc='best')
            plt.tight_layout()

            file_name = electricity_bus_name + ".pdf"
            plt.savefig(os.path.join(plotted, file_name))
