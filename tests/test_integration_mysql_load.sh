#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Runs the integration test for mysql_load.py using the test database

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Apply environment variables
source env/env.env

# Activate the virtual environment
source .venv/bin/activate

python -m pytest tests/test_integration_mysql_load.py -v -s --capture=no --tb=short

# Deactivate virtual environment
deactivate

echo "MySQL load integration test completed successfully." 