# This script runs the integration test for get_skill_gap.py

#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Set env variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Run pytest for all tests in the file
python -m pytest tests/test_integration_get_skill_gap.py -v -s --capture=no --tb=short

# Deactivate the virtual environment
deactivate