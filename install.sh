#!/bin/sh

# Install virtual environment and dependencies.

python3 -m venv env
. env/bin/activate
pip3 install -r requirements.txt
deactivate
