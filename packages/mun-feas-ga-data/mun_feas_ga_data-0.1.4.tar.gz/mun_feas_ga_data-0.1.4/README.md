# GAD: GA Data tool

## Installation

To install from [PyPI](pypi.org), run `pip install mun-feas-ga-data`.


## Usage

### Parsing GA data

To parse GA data in the ATsheet format (assessment tool results), point the `parse` command at a file, directory or set of files and directories:

```sh
$ gad parse ga-data/ some-more-data.csv
```

To extract data from the FEAMS format, you will also need a curriculum map:

```sh
$ gad parse ga-data/ --curriculum-map ENEL-curriculum.xlsx
```

### Converting GA data to FEAMS format

Given some GA data in a directory called `ga-data` and a curriculum map in a file
called `ENEL-map.xlsx`, you can convert the data into a format ready for FEAMS
processing using the following command:

```sh
$ gad feamsify ga-data/ --curriculum-map ENEL-map.xlsx --output FEAMS-ENEL/
```

This will *check* the data for consistency with the curriculum map, *convert* it into FEAMS' expected format and *output* that data to the specified output directory (here, `FEAMS-ENEL`).

## Development

To hack on GAD, install [Python](https://www.python.org/downloads) and [Poetry](https://python-poetry.org/docs/#installation), check out this repository and then run `poetry install`. By default, this will install GAD in editable mode: make changes to the code and they will be immediately reflected when you next run `gad`.