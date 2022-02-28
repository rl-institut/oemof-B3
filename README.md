# oemof-B3

Oemof-B3 is an energy system model of Berlin and Brandenburg. It represents many sectors:
Electricity, central and decentral heat, hydrogen, CO2 and methane. It is a multi-node-model, which
means that several distinct regions are represented that are connected via transmission lines.

<img src="/docs/_img/model_structure.svg" width="900"/>

The model is a perfect-foresight, cost minimizing linear optimization model that builds upon
[oemof.solph](https://github.com/oemof/oemof-solph),
[oemof.tabular](https://github.com/oemof/oemof-tabular),
and [oemoflex](https://github.com/rl-institut/oemoflex).

Oemof-B3 is currently under heavy development, which means that first full scenario runs will be
available in the coming months.

## Installation

Currently, Oemof-B3 needs python 3.7 (newer versions may be supported, but installation can take very long).

In order to install oemof-B3 locally, following steps must be made: 
- git-clone oemof-B3 into local folder: `git clone https://github.com/rl-institut/oemof-B3.git`
- enter folder
- create virtual environment using conda: `conda env create environment.yml`
- activate environment: `conda activate oemof_b3`
- install oemof-B3 package using pip, via: `pip install -e .`

Oemof-B3 needs pandoc (version > 2) in order to create reports. Pandoc is included in conda environment config (environment.yml). 
If environment is build otherwise, pandoc must be installed manually. It can be installed following instructions from [Pandoc Installation](https://pandoc.org/installing.html).


## Getting started

Please activate pre-commit hooks (via `pre-commit install`) in order to follow our coding styles.


## Docs

Read the docs [here](https://oemof-b3.readthedocs.io/).

To build the docs locally, simply install the requirements

    pip install -r docs_requirements.txt

and run

    make html

The output will then be located in `docs/_build/html` and can be opened with your favorite browser
