# oemof-B3

An energy system optimization model for Brandenburg/Berlin.

## Overview

<img src="/docs/_img/model_structure.svg" width="700"/>

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

## Code linting

In this template, 3 possible linters are proposed:
- flake8 only sends warnings and error about linting (PEP8)
- pylint sends warnings and error about linting (PEP8) and also allows warning about imports order
- black sends warning but can also fix the files for you

You can perfectly use the 3 of them or subset, at your preference. Don't forget to edit
`.travis.yml` if you want to desactivate the automatic testing of some linters!

## License
