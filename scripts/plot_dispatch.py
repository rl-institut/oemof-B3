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

            # plot one winter and one summer month
            for i in ["01", "07"]:
                fig, ax = plt.subplots(figsize=(12, 5))
                data = plots.eng_format(ax, data, 'W', 1000)

                start_date = '2019-' + i + '-01 00:00:00'
                end_date = '2019-' + i + '-31 23:00:00'
                plots.plot_dispatch(ax=ax, df=data, start_date=start_date, end_date=end_date,
                                    bus_name=electricity_bus_name)

                plt.grid()
                plt.title(electricity_bus_name + " Dispatch", pad=20, fontdict={'size': 22})
                plt.xlabel("Date", loc='right', fontdict={'size': 17})
                plt.ylabel("Power", loc='top', fontdict={'size': 17})
                plt.xticks(fontsize=14)
                plt.yticks(fontsize=14)

                # Shrink current axis's height by 10% on the bottom
                box = ax.get_position()
                ax.set_position([box.x0, box.y0 + box.height * 0.15,
                                 box.width, box.height * 0.85])
                # Put a legend below current axis
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                          fancybox=True, ncol=5, fontsize=14)

                fig.tight_layout()
                file_name = electricity_bus_name + " " + start_date[5:7] + ".pdf"
                plt.savefig(os.path.join(plotted, file_name), bbox_inches='tight')
