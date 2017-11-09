#!/bin/sh

# Run the server

. env/bin/activate
python3 python/server.py "$@"

