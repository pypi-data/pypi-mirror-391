# Corpus of Place Representations (COPR) / COPR.py

COPR [ˈkɒp.əʳ] is the Corpus of Place Representations, a collection of semantically annotated place representations that are made available for research. It is run by the Space & Place LAB, currently located at the University of Salzburg.

The COPR.py as part of the COPR API is an easy-to-use library to access data from the [Corpus of Place Representations (COPR)](https://copr.space-and-place.net).

Website: [https://copr.space-and-place.net](https://copr.space-and-place.net)

## Installation

To install the library, you will need [Node.js](https://nodejs.org) and [Yarn](https://yarnpkg.com) as well as [Python3](https://www.python.org) and [pip](https://pip.pypa.io).  To install the production version, run
```bash
pip3 install copr.py # install package from PyPI
```

Alternatively, you can install the local version included in this repository.  To do this, you have to first build some files using the [copr-orchestration repository](https://gitea.franz-benjamin.net/copr/copr-orchestration):
```bash
cd ..
git clone https://gitea.franz-benjamin.net/copr/copr-orchestration.git
cd copr-orchestration
yarn run build:info
cd ../copr-api
```      
Then, you can run:
```bash
cd copr.py
yarn install # install for production
yarn run install:dev # install for development (with tests)
```
or alternatively
```bash
cd copr.py
pip3 install . # install for production
pip3 install -e . # install for development
```

## Usage

For further information about the usage, see [https://copr.space-and-place.net](https://copr.space-and-place.net).

## Testing

You can test the package by installing the corresponding dependencies
```bash
pip3 install .[test] # local
pip3 install copr[test] # from PyPI
```
and then running
```bash
pytest --verbose
```

## Publishing

You can publish the library by executing the following steps:
```bash
cd copr.py
yarn run publish
```

## Authorship and License

This application is written and maintained by Franz-Benjamin Mocnik, <mail@space-and-place.net>.

The code is licensed under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
