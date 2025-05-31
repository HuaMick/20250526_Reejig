#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Runs the integration test for mysql_load.py using the test database

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Activate the virtual environment
source .venv/bin/activate

# Run the test using run-tests.sh which handles test database configuration
./run-tests.sh tests/test_integration_mysql_load.py -v -s --capture=no --tb=short

# Deactivate virtual environment
deactivate

echo "MySQL load integration test completed successfully." 