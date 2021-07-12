r"""
Inputs
-------
postprocessed : str
    path to directory which contains the input data which can be plotted
plotted : str
    path where a new directory is created and the plots are saved

Outputs
---------
.pdf
    dispatch plot in pdf-format.

Description
-------------
The script creates dispatch plots based on plot_dispatch function in oemoflex.
The plots are saved as pdf-files in a new directory called plotted.
Timeframes and the carrier for the plot can be chosen.
"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots
import matplotlib.dates as mdates

if __name__ == "__main__":
    postprocessed = sys.argv[1]
    plotted = sys.argv[2]

    # create the directory plotted where all plots are saved
    os.makedirs(plotted)

    bus_directory = os.path.join(postprocessed, "sequences/bus/")
    bus_files = os.listdir(bus_directory)

    # select timeframe
    timeframe = [
        ("2019-01-01 00:00:00", "2019-01-31 23:00:00"),
        ("2019-07-01 00:00:00", "2019-07-31 23:00:00"),
    ]

    # select carrier
    carrier = "electricity"

    selected_bus_files = [file for file in bus_files if carrier in file]

    for bus_file in selected_bus_files:

        bus_name = os.path.splitext(bus_file)[0]
        bus_path = os.path.join(bus_directory, bus_file)

        data = pd.read_csv(bus_path, header=[0, 1, 2], parse_dates=[0], index_col=[0])

        # interactive plotly dispatch plot
        fig_plotly = plots.plot_dispatch_plotly(
            df=data.copy(), bus_name=bus_name, unit="W", conv_number=1000
        )

        fig_plotly.update_layout(title=bus_name + " dispatch")

        file_name = bus_name + "_dispatch_interactive" + ".html"
        fig_plotly.write_html(
            file=os.path.join(plotted, file_name),
            # The following parameters are set according to
            # https://plotly.github.io/plotly.py-docs/generated/plotly.io.write_html.html
            # The files are much smaller now because a script tag containing the plotly.js source
            # code (~3MB) is not included in the output anymore. It is refered to plotlyjs via a
            # link in div of the plot.
            include_plotlyjs="cdn",
            full_html=False,
        )

        # normal dispatch plot
        # plot one winter and one summer month
        for start_date, end_date in timeframe:
            fig, ax = plt.subplots(figsize=(12, 5))
            ax, data = plots.eng_format(ax, data, "W", 1000)

            plots.plot_dispatch(
                ax=ax,
                df=data,
                start_date=start_date,
                end_date=end_date,
                bus_name=bus_name,
            )

            plt.grid()
            plt.title(bus_name + " dispatch", pad=20, fontdict={"size": 22})
            plt.xlabel("Date", loc="right", fontdict={"size": 17})
            plt.ylabel("Power", loc="top", fontdict={"size": 17})
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            # format x-axis representing the dates
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator())

            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position(
                [box.x0, box.y0 + box.height * 0.15, box.width, box.height * 0.85]
            )
            # Put a legend below current axis
            ax.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.1),
                fancybox=True,
                ncol=4,
                fontsize=14,
            )

            fig.tight_layout()
            file_name = bus_name + "_" + start_date[5:7] + ".pdf"
            plt.savefig(os.path.join(plotted, file_name), bbox_inches="tight")
            file_name = bus_name + "_" + start_date[5:7] + ".png"
            plt.savefig(os.path.join(plotted, file_name), bbox_inches="tight")
