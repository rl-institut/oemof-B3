import os
import sys
from oemof.visio import ESGraphRenderer
from oemof.solph import EnergySystem
from oemof_b3.config import config


def restore_results(dpath, filename="es_dump.oemof") -> EnergySystem:
    """
    Restores the energy system from a specified directory and filename.
    input:
        dpath: Directory path where the energy system dump file is located.
        filename: Name of the energy system dump file to restore. (default is "es_dump.oemof")

    :return:
        es: EnergySystem object containing the restored energy system.
    """
    restore_results = True
    if restore_results:
        logger.info("Restore the energy system")

        es = EnergySystem()

        # Adjust the path to your specific directory structure
        es.restore(dpath, filename=filename)

        return es


def plot_esys_graph(es, output_dir="optimized", filename="esys_graph.png"):
    """
    Creates and saves a graph visualization of the given energy system.

    Parameters:
    ----------
    es : oemof.solph.EnergySystem
        The energy system to be visualized.
    output_dir : str, optional
        Directory where the graph image will be saved (default is "optimized").
    filename : str, optional
        Name of the output image file (default is "esys_graph.png").

    Returns:
    -------

    """
    os.makedirs(output_dir, exist_ok=True)
    graph_path = os.path.join(output_dir, filename)
    logger.info(f"Creating graph of energy system and saving it to {graph_path}.")

    es_graph = ESGraphRenderer(es, legend=True, filepath=graph_path, img_format="png")
    es_graph.render()

    logger.info("Graph has been created.")


if __name__ == "__main__":
    # Dump directory
    es_optimized = sys.argv[1]
    # Directory where the graph will be saved
    plotted = sys.argv[2]

    logger = config.add_snake_logger("plot_graph")

    # restore the energy system from the specified directory
    es = restore_results(es_optimized)
    plot_esys_graph(es, output_dir=plotted)
    logger.info("Graph has been created.")
