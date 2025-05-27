
#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# This is required so that the script fails and the agent can commence debugging.
set -e 

# Set env variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Run pytest
python -m pytest tests/example_test_integration.py::test_example_integration -v -s --capture=no --tb=short