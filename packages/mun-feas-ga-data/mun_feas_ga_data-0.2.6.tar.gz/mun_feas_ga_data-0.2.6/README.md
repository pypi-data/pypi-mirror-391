# GAD: GA Data tool

## Install

To install from [PyPI](pypi.org), run `pip install mun-feas-ga-data`.


## Validate GA data

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


## Plot data

### Per-course assessment tool results

To plot the assessment tool results contained in a directory of result files, use the `plot` command:

```sh
$ gad plot tools ga-data-dir/ --curiculum-map ENEL-curriculum.xlsx --output-dir plots-ENEL/
```

You can also specify the output format (PDF, PNG, SVG, etc.) using the `-f`/`--format`
argument.


## Interoperate with FEAMS

To convert GA data (in ATsheets, FEAMS or both) into a unified directory ready for
[FEAMS](https://gitlab.com/MemorialU/Engineering/continuousimprovement/feams) ingestion,
use the `feamsify` command:

```sh
$ gad feamsify ga-data/ --curriculum-map ENEL-map.xlsx --output FEAMS-ENEL/
```

* `ga-data/`: a directory containing ATsheets and/or FEAMS data files
* `ENEL-map.xlsx`: curriculum map for an Engineering program (here, Electrical)
* `FEAMS-ENEL/`: the directory to write FEAMS-formatted files into for FEAMS parsing


## Work on GAD

To hack on GAD, install [Python](https://www.python.org/downloads) and [Poetry](https://python-poetry.org/docs/#installation), check out this repository and then run `poetry install`. By default, this will install GAD in editable mode: make changes to the code and they will be immediately reflected when you next run `gad`.
