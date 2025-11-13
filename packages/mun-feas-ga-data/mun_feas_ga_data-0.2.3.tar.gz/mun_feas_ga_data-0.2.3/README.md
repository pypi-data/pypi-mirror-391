# GAD: GA Data tool

## Installation

To install from [PyPI](pypi.org), run `pip install mun-feas-ga-data`.


## Usage

### Validating GA data

To check that GA data contained in ATsheet or FEAMS format matches aligns with a
curriculum map, use the `validate` command:

```sh
$ gad validate ga-data/ --curriculum-map ENEL-curriculum.xlsx
ECE 4300 (Spring 2024–25) contains 81 results
1 warning(s):
 - contains 3 unnamed columns

ECE 4500 (Spring 2024–25) contains 62 results
ECE 4800 (Spring 2024–25) contains 39 results
1 warning(s):
 - contains 27 unnamed columns
```

You can, additionally, identify assessment tools that do not appear in the curriculum
map using the `-u` / `--unmapped-tools` option:

```sh
$ gad validate --unmapped-tools ga-data/ --curriculum-map ENEL-curriculum.xlsx
ECE 4300 (Spring 2024–25) contains 81 results
2 warning(s):
 - contains 3 unnamed columns
 - 3 unmapped tools: Final exam – design questions, Assignment – evaluate and compare designs, Design labs

ECE 4500 (Spring 2024–25) contains 62 results
1 warning(s):
 - 5 unmapped tools: Assignments, Labs – debugging sections, Design assignment and exam questions, Labs, Labs — info sources

ECE 4800 (Spring 2024–25) contains 39 results
2 warning(s):
 - contains 27 unnamed columns
 - 5 unmapped tools: Course grade , Labs – gather info, Labs – synthesize info, Assignments,  labs - communication
```

### Plotting assessment tool results

To plot the assessment tool results contained in a directory of result files, use the `plot` command:

```sh
$ gad plot ga-data-dir/ --curiculum-map ENEL-curriculum.xlsx --output-dir plots-ENEL/
```

You can also specify the output format (PDF, PNG, SVG, etc.) using the `-f`/`--format`
argument.

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
