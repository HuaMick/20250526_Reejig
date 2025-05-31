#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Apply environment variables
source env/env.env

# Run the test with -s flag to show print statements and -v for verbose output
echo "Running integration test for mysql_init_tables function..."
python -m pytest tests/test_integration_mysql_init_tables.py -v -s

# Capture the exit code
exit_code=$?

# Deactivate the virtual environment if it was activated
if [ -d ".venv" ]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

# Exit with the test's exit code
exit $exit_code 