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

# Make sure we're using the test database
echo "Setting up test database environment..."
export MYSQL_TEST_DATABASE=${MYSQL_TEST_DATABASE:-"onet_test_db"}
echo "Using test database: $MYSQL_TEST_DATABASE"

# Run the test with -s flag to show print statements and -v for verbose output
echo "Running integration test for transform node..."
python -m pytest tests/test_integration_transform.py -v -s

# Capture the exit code
exit_code=$?

# Deactivate the virtual environment if it was activated
if [ -d ".venv" ]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

# Exit with the test's exit code
exit $exit_code 