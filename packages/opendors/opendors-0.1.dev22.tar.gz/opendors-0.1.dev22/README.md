# `opendors`

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

Construct and interact with OpenDORS datasets.

> [!important]
> `opendors` is work in progress.
> Prior to major version 1, it may not be complete, usable, reliable or well-engineered.

## Installation

Install directly from PyPI: `pip install opendors`.

Install from source (requires [Poetry](https://python-poetry.org/)):

```shell
# Clone git repository & change into clone directory
git clone git@gitlab.dlr.de:drus_st/opendorslib.git
cd opendorslib

# Install with poetry
poetry install
```

If you want to use the [`repository`](opendors/rules/repository.py) workflow rule,
you also need to install Ruby with the `github-linguist` and `licensee` gems.

This repository contains a definition for a conda environment that you can use to install these extra dependencies:
[`conda-environment.yml`](conda-environment.yml).
To install the dependencies, do:

```shell
mamba env create -n opendors --file conda-environment.yml
mamba activate opendors
gem install github-linguist
gem install licensee
```

Keep the environment activated to use the [`repository`](opendors/rules/repository.py) rule.

## Usage

`opendors` provides both an API for creating an OpenDORS dataset,
and a CLI tool to interact with an OpenDORS dataset.

```shell
usage: opendors [-h] [-c] [-v] {schema,filter,stats,merge} ...

Utilities to work with OpenDORS datasets.

positional arguments:
  {schema,filter,stats,merge}
                        Available commands
    schema              Exports the JSON schema for the opendors model to 'schema.json'.
    filter              Filters a given dataset by programming language and/or before/after dates.
    stats               Gather statistics on a given OpenDORS dataset.
    merge               Merge OpenDORS datasets into a single file.

options:
  -h, --help            show this help message and exit
  -c, --compressed      Export as unindented JSON
  -v, --verbose         Print tracebacks on error
```

## Build Python package

Run `poetry build`.

To publish to PyPI, run `poetry publish`.
You need to have a PyPI API token configured to do this.

# Run tests

Tests can be run locally as follows:

```bash
poetry run pytest tests/
```

## Test coverage

Coverage (with branch coverage) can be displayed as follows:

```bash
poetry run python -m pytest tests --cov=opendors --cov-branch --cov-report=html --cov-report=term
```
