# Steam Inventory Prices - Back-End

Steam inventory prices project's backend. This service will handle all the communication with steam api and manage items lists.


# Installing Dependencies

Install virutalenv (if not yet installed): `pip install virtualenv`

Create your virtual environment with `Python 3.10.4`: `python3 -m virutalenv env`

Start your virutal environment: `source env/bin/activate`

Upgrade pip: `pip install --upgrade pip`

Install dependencies: `pip install -r requirements.txt`

Install pre-commit (in case you are developing this project): `pre-commit install --overwrite`


# Running Scripts

When running the project, cd into `backend/src` project and run `export PYTHONPATH=$(pwd)`

To generate the spreadsheet, run `python scripts/generate_spreadsheet.py`


# Managing Dependencies

Needed packages (and optionally their version) are added to `requirements.in` file.

The specific versions installed of a package are added (automatically) to `requirements.txt` file.


## Adding a New Dependency

Add the dependency to `requirements.in` file.

In case you need the most recent version of a dependency, add a line with `[package]`.

In case you need a fixed version of a dependency add a line with: `[package]==[version]`.

In case you need a version smaller than a specific one of a dependency, add a line with `[package]<[version]`.

And then run `pip-compile` to update `requirements.txt` file.

## Updating a Dependency

To update a single dependency run `pip-compile --upgrade-package [package]==[version]` (this will impact only on `requirements.txt` file)

To update all dependencies to the most up to date version tun `pip-compile --upgrade`
