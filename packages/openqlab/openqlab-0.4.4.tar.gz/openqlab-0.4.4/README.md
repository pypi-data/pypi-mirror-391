# openqlab

[![pipeline status](https://gitlab.com/las-nq/openqlab/badges/master/pipeline.svg)](https://gitlab.com/las-nq/openqlab/commits/master)
[![coverage report](https://gitlab.com/las-nq/openqlab/badges/master/coverage.svg)](https://gitlab.com/las-nq/openqlab/commits/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


`openqlab` provides a collection of useful tools and helpers for the
analysis of lab data in the Nonlinear Quantum Optics Group at the University
of Hamburg.

Part of the content in this package was written during the PhD theses of
Sebastian Steinlechner and Tobias Gehring. It is currently maintained by
Sebastian Steinlechner, Christian Darsow-Fromm, Jan Petermann and is looking for more
volunteers who would like to contribute.

Read the latest changes in our [changelog](CHANGELOG.md).

## Documentation

* Current documentation of the [latest release](https://las-nq-serv.physnet.uni-hamburg.de/python/openqlab)
* Current documentation of the [latest development version](https://las-nq-serv.physnet.uni-hamburg.de/python/openqlab-stage)

## Features

* Importers for various file formats:
  * Agilent/Keysight scopes (binary and CSV)
  * Rohde & Schwarz spectrum analyzers
  * Tektronix spectrum analyzer
  * plain ascii
  * and a few more...
* easily create standard plots from measurement data
* design control loops
* analyze beam profiler data
* generate covariance matrices for N partite systems
* several postprocessing functions for entanglement data
* analyse and automatically plot squeezing data
* tools for working with dB units

## Installation

For a detailed installation instruction see the main [documentation](https://las-nq-serv.physnet.uni-hamburg.de/python/openqlab/).

## Usage

You will need an up-to-date Python 3 environment to use this package, e.g.
the Anaconda Python distribution will work just fine. Please refer to the
`requirements.txt` for a list of prerequisites (although these should be
installed automatically, if necessary).

For examples and details on how to use this package, please refer to the
documentation.

## Contributing
All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

A detailed overview on how to contribute can be found in the [contributing guide](CONTRIBUTING.md).

## License
The code is licensed under the [GNU GENERAL PUBLIC LICENSE](https://www.gnu.org/licenses/gpl-3.0.html). See [LICENSE](LICENSE).

## Changelog
Changes to the code are documented in the [changelog](CHANGELOG.md).
