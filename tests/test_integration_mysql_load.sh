#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Runs the integration test for mysql_load.py

# Set env variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Run pytest for all tests in the file
python -m pytest tests/test_integration_mysql_load.py -v -s --capture=no --tb=short

# Deactivate the virtual environment
deactivate

echo "MySQL load integration test script finished successfully." 