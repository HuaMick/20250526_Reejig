#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Apply environment variables
source env/env.env

# Run the test with -s flag to show print statements and -v for verbose output
python -m pytest tests/test_integration_mysql_query.py::test_mysql_query -v -s --capture=no --tb=short

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 