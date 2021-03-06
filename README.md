# Web application for browsing the etree linked data resource.

## Installation

The easiest way to install and run the application is via a virtual environment

```
$ python3 -venv env
$ . env/bin/activate
$ pip3 install -r requirements.txt
$ deactivate
```

This will set up a virtual environment and install the dependencies.

## Run

The application can then be run using:

```
$ . env/bin/activate
$ python3 python/server.py
```

Scripts `install.sh` and `server.sh` can also be used. 

## Usage

Usage information:

```
usage: server.py [-h] [-p PORT] [-e ENDPOINT] [-d]

Browser for the etree linked data/RDF repository. This web application
provides a human readable view on the data held in the etree metadata
collection.

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port. Defaults to 4444
  -e ENDPOINT, --endpoint ENDPOINT
                        SPARQL endpoint for the data. Defaults to
                        http://etree.linkedmusic.org/sparql
  -d, --debug           debug
```

## Docker

There is a `Dockerfile` in the repository that can be used to build a
Docker image that will run the browser.



