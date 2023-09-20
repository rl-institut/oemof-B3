# oemof-B3

oemof-B3 is an energy system model of Berlin and Brandenburg. It represents many sectors:
Electricity, central and decentral heat, hydrogen, CO2 and methane. It is a multi-node-model, which
means that several distinct regions are represented that are connected via transmission lines.

<img src="/docs/_img/model_structure.svg" width="900"/>

The model is a perfect-foresight, cost minimizing linear optimization model that builds upon
[oemof.solph](https://github.com/oemof/oemof-solph),
[oemof.tabular](https://github.com/oemof/oemof-tabular),
and [oemoflex](https://github.com/rl-institut/oemoflex).

There are six scenarios available, that you can calculate with oemof-B3:
- 2050-80-el_eff
- 2050-80-gas_moreCH4
- 2050-95-el_eff
- 2050-95-gas_moreCH4
- 2050-100-el_eff
- 2050-100-gas_moreCH4

All six refer to the target year 2050. A further distinction is made between an emissions reduction
of 80, 95 or 100 percent. Furthermore, the scenarios differ in their degree of electrification. 
Scenarios with the index 'el_eff' represent strongly electrified scenarios, while 'gas_moreCH4'
represent scenarios with increased use of methane.
In the documentation you will find instructions on how to run the scenarios with oemof-B3.

## Getting started

### Installation

Currently, oemof-B3 needs python 3.7 or 3.8 (newer versions may be supported, but installation can take very long).

Additionally, you need to install the python dependency manager [poetry](https://python-poetry.org/).
It is recommended to install poetry system-wide via the command below or
[pipx](https://python-poetry.org/docs/#installing-with-pipx):

    curl -sSL https://install.python-poetry.org | python3 -
    poetry install


In order to install oemof-B3, proceed with the following steps:

- git-clone oemof-B3 into local folder via https:

       git clone https://github.com/rl-institut/oemof-B3.git
  or via ssh:

       git clone git@github.com:rl-institut/oemof-B3.git
- enter folder
- create virtual environment using conda:

       conda env create environment.yml
- activate environment:

       conda activate oemof-B3
- install oemof-B3 package using poetry, via:

       poetry install

Alternatively, you can create a virtual environment using other approaches, such as `virtualenv`.

To create reports oemof-B3 requires pandoc (version > 2). Pandoc is included in conda environment config (environment.yml). 
If environment is build otherwise, pandoc must be installed manually. It can be installed following instructions from [Pandoc Installation](https://pandoc.org/installing.html).

For the optimization, oemof-B3 needs a solver. Check out the [oemof.solph](https://oemof-solph.readthedocs.io/en/latest/readme.html#installing-a-solver) documentation for installation notes.

To test if everything works, you can run the [examples](https://oemof-b3.readthedocs.io/en/latest/examples.html).

For developers: Please activate pre-commit hooks (via `pre-commit install`) in order to follow our coding styles.

### Data

Download the raw data for the model from zenodo via:

    snakemake -j1 download_raw_data

### Documentation

Find the documentation [here](https://oemof-b3.readthedocs.io/).

## Contributing

Feedback is welcome. If you notice a bug, please open an 
[issue](https://github.com/rl-institut/oemof-B3/issues). 

### Build the docs locally

To build the docs locally, you have to install related dependencies via

    poetry install -E docs

Afterwards, navigate into the docs directory with
    
    cd docs/
    
and run

    make html

The output will then be located in `docs/_build/html` and can be opened with your favorite browser
