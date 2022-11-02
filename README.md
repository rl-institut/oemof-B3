# oemof-B3

oemof-B3 is an energy system model of Berlin and Brandenburg. It represents many sectors:
Electricity, central and decentral heat, hydrogen, CO2 and methane. It is a multi-node-model, which
means that several distinct regions are represented that are connected via transmission lines.

<img src="/docs/_img/model_structure.svg" width="900"/>

The model is a perfect-foresight, cost minimizing linear optimization model that builds upon
[oemof.solph](https://github.com/oemof/oemof-solph),
[oemof.tabular](https://github.com/oemof/oemof-tabular),
and [oemoflex](https://github.com/rl-institut/oemoflex).

oemof-B3 is currently under heavy development, which means that first full scenario runs will be
available in the coming months.

## Getting started

### Installation

Currently, oemof-B3 needs python 3.7 or 3.8 (newer versions may be supported, but installation can take very long).

In order to install oemof-B3, proceed with the following steps:

- git-clone oemof-B3 into local folder: `git clone https://github.com/rl-institut/oemof-B3.git`
- enter folder
- create virtual environment using conda: `conda env create environment.yml`
- activate environment: `conda activate oemof-B3`
- install oemof-B3 package using poetry, via: `poetry install`

Alternatively, you can create a virtual environment using other approaches, such as `virtualenv`.

To create reports oemof-B3 requires pandoc (version > 2). Pandoc is included in conda environment config (environment.yml). 
If environment is build otherwise, pandoc must be installed manually. It can be installed following instructions from [Pandoc Installation](https://pandoc.org/installing.html).

For the optimization, oemof-B3 needs a solver. Check out the [oemof.solph](https://oemof-solph.readthedocs.io/en/latest/readme.html#installing-a-solver) documentation for installation notes.

To test if everything works, you can run the examples (cf. :ref:`How to run the model`).

For developers: Please activate pre-commit hooks (via `pre-commit install`) in order to follow our coding styles.

### Data

The raw data necessary to run the scenarios is not part of the model. It is not public yet and will
be provided in the coming months. 

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
