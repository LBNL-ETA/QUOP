# QUOP - Quantitative Universal Option Prioritizer

## About the QUOP

QUOP is a three-layer analytical hierarchy process (AHP) based multi-criteria decision-making option evaluation and prioritization tool.


### Statement of Need

Decision-making often entails evaluation of options. Such competing options can either be mutual substitutes or cumulative means to achieve an objective. The options themselves can be methods, tools, technologies, processes, etc.

Stakeholders involved in achieving the objective may view each option characteristic differently, depending on their needs and preferences. The QUOP tool enables a streamlined quantitative collaborative process of weighing the opinion of each stakeholder in evaluating the options.

The evaluation may also be performed under different scenarios, for instance, various option potential estimates, prices, or end-user demand projections.

The QUOP tool can find application in both public and private sectors, as well as on an individual level, for example:

* Assist in making federal or state-level policy decisions, such as defining incentives or laws
* Enable an informed and documented selection of new corporate processes, tools, or project portfolios
* Illuminate importance of various option characteristics to different members of the same household in making purchasing decisions

The major advantage of using the QUOP decision-making tool is in documenting the quantified stakeholder opinion, therefore the background to each decision made, while maintaining high transparency and stakeholder involvement. The tool is particularly suitable for decisions involving a high number of options and option characteristics, that is, aspects of each option that matter to the stakeholders.

### Methodology and Functionality

The prioritization process encapsulated in the QOOP tool consists of three steps:

1. Scoring - implemented in the [scoring.py](prioritization/scoring.py) module

    The step converts quantitative characterization results, given for all options, into mutually comparable quantitative characterization scores.

2. Prioritization - implemented in the in the [scoring.py](prioritization/ahp.py) module. The [AHP module](prioritization/ahp.py) is implemented based on the work published by Thomas L. Saaty - The Analytic Hierarchy Process: Decision Making In Complex Environments.

    The step calculates the relative importance, called a weight, of each of the individual quantitative characterization scores. The prioritization weight development is structured into three priority layers, often interpreted as the importance of, in top down fashion:

    * Stakeholder
    * Group of characteristics to each stakeholder, and 
    * Each individual characteristic in each group of characteristics.

3. Ranking - implemented as a part of the [process.py](prioritization/scoring.py) module

    The final scored and weighted results are summed and
    ranked for each option, both per stakeholder and overall.
    The option ranking can be categorized into informative bins, 
    assigned with flags, for instance green, yellow, and red.

The [process.py](prioritization/scoring.py) module performs all three steps of the calculation, reads in the input file, and, optionally, saves calculation results and visualizations.

The following inputs need to be provided to the tool, in a standardized way:

* Option characterization quantitative results, under all scenarios
* Results scoring range and filtering limits
* Global option characteristic weights
* AHP priority ratings at each prioritization layer

In the output folder under a path indicated in the `run_parameters` table of the input file, a unique-tagged folder is created that contains:

* All input data, as listed above
* Intermediary output data, such as the scored option characterization results and prioritization weights
* Weighed and scored results
* Option rankings
* Results visualzation in form of images


### Research Applications

The QUOP tool is currently used in the final phases of the multi-criteria technology evaluation process for the CEC [CalFlexHub](https://calflexhub.lbl.gov/) project. The project evaluates flexible load technologies useful in reshaping the customer electric loads, with the goal to advance the integration of renewable energy generation, while being affordable, equitable, and reliable for the customers.


## How to Use the QUOP

The QUOP tool is an installable Python package that includes a test suite and example input files.

### Setup and Installation

To install:

1. Make sure that `pip` [is installed](https://pip.pypa.io/en/stable/installing/).

2. Unless you already have [`conda`](https://docs.conda.io/en/latest/) installed, please install the lightweight option [`Miniconda`](https://docs.conda.io/en/latest/miniconda.html) or [`Anaconda`](https://docs.anaconda.com/anaconda/install/) software.

3. Clone the remote repository localy with:
```
git clone https://github.com/LBNL-ETA/QUOP.git
```

4. Navigate to the cloned repo folder, and install the QUOP package with:
```
pip install .
```

### Usage

The usage of the tool requires these two steps:

1. Preparing the standardized format input file in Excel
2. Running the Python tool pointing to the input file

To perform the steps, the user can do the following ([for convenience also provided as a Python notebook](scripts/example.ipynb)):

1. The tool requires an excel input file populated with standardized tables. The table
standardization entails the table naming and column labeling conventions. The
conventions are presented on the info tab of the test input file available at the 
repo and at your local clone at this path:

```
"prioritization/tests/test_input.xlsx"
```

2. To create a prioritizer Python object, the user should customize the following 
class object instantiation command, found below the import statement:

```
from prioritization.process import Prioritizer

prioritizer = Prioritizer(
        inpath="full or relative path to my input file",
        writeout=True,
        create_plots=True,
        os_mapping={
            'win32': my root path, for example ' X:',
            'darwin': my root path, for example '/Volumes/A',
            'linux': my root path, for example '/media/b'})
        number_of_ranking_bins=3,
        lower_ranking_limit_0=False,
        ranking_bin_labels=['red', 'yellow', 'green']
        )
```

The modification can, for instance, be similar to the version below:

```
prioritizer = Prioritizer(
        inpath="prioritization/tests/test_input.xlsx",
        writeout=True,
        create_plots=True,
        os_mapping={
            'win32': 'C:',
            'darwin': '/Volumes/A',
            'linux': '/media/b'},
        number_of_ranking_bins=3,
        lower_ranking_limit_0=False,
        ranking_bin_labels=['red', 'yellow', 'green']
        )
```

The prioritization results can then be calculated as follows:
```
prioritizer.calculate()
```

The main results are stored in a dictionary with keys `long`, `pivoted`, and `summed_and_ranked`:
```
result = prioritizer.scores_and_weights
```

Further details about each of the input keyward arguments are, as is common, provided in the 
`process.Prioritizer` class constructor docstring.

### Testing

The package contains a unit tests with a basic coverage. Those can be run for the whole package with"
```
python -m unittest discover
```

To perform prioritization based on the input file, a simple functional test can be called with, from the repo root:
```
python -m unittest prioritization.tests.test_process
```

To unit test each individual module, one can run:
```
python -m unittest prioritization.tests.test_ahp
python -m unittest prioritization.tests.test_scoring
```

## Contributing

All are invited to contribute to the QUOP software through following the [Guidelines for Contributors](contributing.md).

## About

The software may be distributed under the copyright and a BSD license provided in [legal.md](legal.md).

Milica Grahovac, Shreya Agarwal, Brian Gerke, Sarah Smith, and Marius Stuebs created the contents of this repo and developed its methodology in the scope of the CEC [CalFlexHub](https://calflexhub.lbl.gov/) project.

To cite use format provided at the [DOE CODE](https://www.osti.gov/biblio/1988273) QUOP record.

## Acknowledgements

This work was supported by the California Energy Commission, Public Interest Energy Research Program, under Contract No. EPC-20-025.
