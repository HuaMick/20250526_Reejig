#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Runs the integration test for mysql_connection.py

# Set env variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Run pytest
python -m pytest tests/test_integration_mysql_connection.py::test_actual_mysql_connection -v -s --capture=no --tb=short

# Deactivate the virtual environment
deactivate 