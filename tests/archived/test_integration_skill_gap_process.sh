#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# This is required so that the script fails and the agent can commence debugging.
set -e 

# Set env variables
source env/env.env

# Activate the virtual environment
source .venv/bin/activate

# Set PYTHONPATH to include the src directory (retaining for now, but ideally not needed with `python -m pytest` and proper project structure)
export PYTHONPATH=$(pwd):$(pwd)/src:$PYTHONPATH

# Run pytest for the specific test file
# The -s flag shows print statements, -v for verbose output, --capture=no is redundant with -s, --tb=short for shorter tracebacks.
python -m pytest tests/test_integration_skill_gap_process.py -v -s --tb=short

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 