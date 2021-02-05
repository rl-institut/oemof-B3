![](https://reiner-lemoine-institut.de/wp-content/uploads/2015/10/logo_oemof.png)
## oemof-B3

The Open Energy Modelling Framework B3 (oemof-B3) is a simple model to map the electricity network in the area of Berlin-Brandenburg (Germany).
It serves as a basis for further development.

## How It Works
The model consists of two nodes, one for Berlin and one for Brandenburg. 
Modelled components are 
- renewable energies (wind, photovoltaic, biomass)
- conventional power plants (gas, oil, others)

Data for capacities of wind, photovoltaic and biomass as well as electricity demand have been taken from
the grid development plan ([Netzentwicklungsplan](https://www.netzentwicklungsplan.de/sites/default/files/paragraphs-files/NEP_2035_V2021_1_Entwurf_Teil1.pdf)), p. 41 ff..
Data for efficiency and costs (specific annuity, fuel costs) are based on different sources as well as own assumptions and can be adjusted.


All electricity generating components can be expanded. 
Additionally, it can be invested into grid expansion and battery storage.

Three scenarios have been built based on the grid development plan:
- simple_model: corresponds to scenario A 2035 of the grid development plan
- simple_model_2: corresponds to scenario B 2035 of the grid development plan
- simple_model_3: corresponds to scenario B 2040 of the grid development plan

## Installation

pip install -r requirements.txt

## Docs

Read the docs [here](https://oemof-b3.readthedocs.io/).

To build the docs locally, simply go to the `docs` folder

    cd docs

Install the requirements

    pip install -r docs_requirements.txt

and run

    make html

The output will then be located in `docs/_build/html` and can be opened with your favorite browser

## Code linting

In this template, 3 possible linters are proposed:
- flake8 only sends warnings and error about linting (PEP8)
- pylint sends warnings and error about linting (PEP8) and also allows warning about imports order
- black sends warning but can also fix the files for you

You can perfectly use the 3 of them or subset, at your preference. Don't forget to edit
`.travis.yml` if you want to desactivate the automatic testing of some linters!

## License
