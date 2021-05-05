import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import oemoflex.tools.plots as plots

if __name__ == "__main__":
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    data = pd.read_csv(in_path, header=[0,1,2], parse_dates=[0], index_col=[0])

    fig, ax = plt.subplots(figsize=(12,5))
    data = plots.eng_format(ax, data, 'W', 1000)


    start_date = '2019-12-01 00:00:00'
    end_date = '2019-12-13 23:00:00'
    plots.plot_dispatch(ax=ax, df=data, start_date=start_date, end_date=end_date,
                        bus_name='BB-electricity', demand_name='BB-electricity-demand')

    plt.legend(loc='best')
    plt.tight_layout()
    #plt.show()

    os.makedirs(out_path)
    file_name = "BB-electricity.pdf"
    plt.savefig(os.path.join(out_path,file_name))
