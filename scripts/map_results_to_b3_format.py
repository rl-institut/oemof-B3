import sys
import pathlib

import oemof_b3.tools.data_processing as dp


if __name__ == "__main__":
    postprocessed = pathlib.Path(sys.argv[1])

    target = pathlib.Path(sys.argv[2])

    target.mkdir(exist_ok=True)

    scenario = postprocessed.parts[-2]
    print(scenario)

    # map sequences
    sequences = postprocessed / "sequences" / "by_variable"
    for path in sequences.iterdir():
        file_name = str(path.parts[-1])

        ts = dp.load_tabular_results_ts(path)

        ts = dp.oemof_results_ts_to_oemof_b3(ts)

        ts["scenario_key"] = scenario

        dp.save_df(ts, target / file_name)

    # map scalars
    scal = dp.load_tabular_results_scal(postprocessed / "scalars.csv")

    scal = scal.rename(columns={"scenario": "scenario_key"})

    scal = dp.format_header(scal, dp.HEADER_B3_SCAL, "id_scal")

    dp.save_df(scal, target / "scalars.csv")
