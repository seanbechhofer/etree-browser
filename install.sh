#!/bin/sh

# Install virtual environment and dependencies.

python3 -venv env
. env/bin/activate
pip3 install -r requirements.txt
deactivate
