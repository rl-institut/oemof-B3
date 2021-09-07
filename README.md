# oemof-B3

Oemof-B3 is an energy system model of Berlin and Brandenburg. It represents many sectors:
Electricity, central and decentral heat, hydrogen, CO2 and methane. It is a multi-node-model, which
means that several distinct regions are represented that are connected via transmission lines.

<img src="/docs/_img/model_structure.svg" width="700"/>

The model is a perfect-foresight, cost minimizing linear optimization model that builds upon
[oemof.solph](https://github.com/oemof/oemof-solph),
[oemof.tabular](https://github.com/oemof/oemof-tabular),
and [oemoflex](https://github.com/rl-institut/oemoflex).

Oemof-B3 is currently under heavy development, which means that first full scenario runs will be
available in the coming months.

## Getting started

## Docs

Read the docs [here](https://oemof-b3.readthedocs.io/).

To build the docs locally, simply go to the `docs` folder

    cd docs

Install the requirements

    pip install -r docs_requirements.txt

and run

    make html

The output will then be located in `docs/_build/html` and can be opened with your favorite browser

## License
