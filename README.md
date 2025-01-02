# ifq

[![PyPI](https://img.shields.io/pypi/v/ifq.svg)](https://pypi.org/project/ifq/)
[![Changelog](https://img.shields.io/github/v/release/zmoog/ifq?include_prereleases&label=changelog)](https://github.com/zmoog/ifq/releases)
[![Tests](https://github.com/zmoog/ifq/actions/workflows/test.yml/badge.svg)](https://github.com/zmoog/ifq/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/zmoog/ifq/blob/master/LICENSE)

CLI tool and Python library to download PDF issues of ilfattoquotidiano.it

## Installation

Install this tool using `pip`:
```bash
pip install ifq
```
## Usage

For help, run:
```bash
ifq --help
```
You can also use:
```bash
python -m ifq --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd ifq
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
