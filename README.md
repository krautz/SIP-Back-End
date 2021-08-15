# Steam Inventory Prices - Back-End

Steam inventory prices project's backend. This service will handle all the communication with steam api and manage items lists.


# Running Scripts

When running the project, cd into `backend` project and run `export PYTHONPATH=$(pwd)`

Install virutalenvironment (if not yet installed): `pip install virtualenv`

Create your virtualenvironment (if not yet created) with `Python 3.8.2`: `python -m virutalenv env`

Start your virutal environment: `source env/bin/activate`

Install dependencies: `pip install -r requirements.txt`

To generate the spreadsheet, run `python scripts/generate_spreadsheet.py`


# Managing Dependencies

Needed packages (and optionally their version) are added to `requirements.in` file.

The specific versions installed of a package are added (automatically) to `requirements.txt` file.

## Installing Dependencies

Create your virtual environment with `Python 3.8.2`: `python3 -m virutalenv env`

Install dependencies: `pip install -r requirements.txt`

## Adding a New Dependency

Add the dependency to `requirements.in` file.

In case you need the most recent version of a dependency, add a line with `[package]`.

In case you need a fixed version of a dependency add a line with: `[package]==[version]`.

In case you need a version smaller than a specific one of a dependency, add a line with `[package]<[version]`.

And then run `pip-compile` to update `requirements.txt` file.

## Updating a Dependency

To update a single dependency run `pip-compile --upgrade-package [package]==[version]` (this will impact only on `requirements.txt` file)

To update all dependencies to the most up to date version tun `pip-compile --upgrade`
