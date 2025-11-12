# FlickerPrint

FlickerPrint is a software package for conducting flicker spectroscopy analysis to find the interfacial tension and bending rigidity of soft bodies such as biomolecular condensates and vesicles from their shape fluctuations in confocal microscopy images.

## Prerequisites

FlickerPrint requires Python 3.9 to 3.11 and an installation of Java.
Full details of how to install these prerequisites are available in the [documentation](https://flickerprint.github.io/FlickerPrint/).

## Installation

FlickerPrint can be installed directly using pip:

```bash
python3 -m pip install flickerprint
```

To build the package from the source code, clone the Git repository, then navigate to the ``FlickerPrint/src`` directory of the repository and run:

```bash
python3 -m pip install -e .
```

## Usage

FlickerPrint is primarily used through the command line. To see the available commands and options, run:

```bash
flickerprint --help
```

To create a new experiment, run:

```bash
flickerprint create-project <project_name>
```

To analyse a dataset, ``cd`` into the experiment directory and run:

```bash
flickerprint run [-c cores]
```

To visualise the results, run:

```bash
flickerprint view-output
```