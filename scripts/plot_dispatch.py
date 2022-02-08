# coding: utf-8
r"""
Inputs
-------
postprocessed : str
    ``results/{scenario}/postprocessed/``: path to directory which contains the input data which
    can be plotted
plotted : str
    ``results/{scenario}/plotted/``: path where a new directory is created and the plots are saved

Outputs
---------
.pdf
    dispatch plot in pdf-format.
.html
    interactive plotly dispatch plot in html-format.

Description
-------------
The script creates dispatch plots based on plot_dispatch and plot_dispatch_plotly
functions in oemoflex.
The static plots are saved as pdf-files and the interactive plotly plots as html-files
in a new directory called plotted.
Timeframes and the carrier for the plot can be chosen.
"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots
import matplotlib.dates as mdates

from oemof_b3 import labels_dict, colors_odict


if __name__ == "__main__":
    postprocessed = sys.argv[1]
    plotted = sys.argv[2]

    # create the directory plotted where all plots are saved
    os.makedirs(plotted)

    bus_directory = os.path.join(postprocessed, "sequences/bus/")
    bus_files = os.listdir(bus_directory)

    # select carrier
    carriers = ["electricity", "heat_central", "heat_decentral"]

    selected_bus_files = [
        file for file in bus_files for carrier in carriers if carrier in file
    ]

    for bus_file in selected_bus_files:

        bus_name = os.path.splitext(bus_file)[0]
        bus_path = os.path.join(bus_directory, bus_file)

        data = pd.read_csv(bus_path, header=[0, 1, 2], parse_dates=[0], index_col=[0])

        # prepare dispatch data
        # convert data to SI-unit
        conv_number = 1000
        data = data * conv_number
        df, df_demand = plots.prepare_dispatch_data(
            data,
            bus_name=bus_name,
            demand_name="demand",
            labels_dict=labels_dict,
        )

        # interactive plotly dispatch plot
        fig_plotly = plots.plot_dispatch_plotly(
            df=df, df_demand=df_demand, unit="W", colors_odict=colors_odict
        )
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
        # select timeframe
        start_date_data = str(data.index[0])
        end_date_data = str(data.index[31 * 24 - 1])
        timeframe = [
            (start_date_data, end_date_data),
            (
                start_date_data.replace("01-", "07-"),
                end_date_data.replace("01-", "07-"),
            ),
        ]
        for start_date, end_date in timeframe:
            fig, ax = plt.subplots(figsize=(12, 5))

            # filter timeseries
            df_time_filtered = plots.filter_timeseries(df, start_date, end_date)
            df_demand_time_filtered = plots.filter_timeseries(
                df_demand, start_date, end_date
            )
            # plot time filtered data
            plots.plot_dispatch(
                ax=ax,
                df=df_time_filtered,
                df_demand=df_demand_time_filtered,
                unit="W",
                colors_odict=colors_odict,
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
