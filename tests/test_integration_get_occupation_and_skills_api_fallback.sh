#!/bin/bash

# Integration test for get_occupation_and_skills function with API fallback logic

# Exit immediately if a command exits with a non-zero status
set -e

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Error: Virtual environment .venv not found in project root."
    exit 1
fi

# Apply environment variables
if [ -f "env/env.env" ]; then
    echo "Loading environment variables from env/env.env..."
    source env/env.env
else
    echo "Error: Environment file not found at env/env.env"
    exit 1
fi

# Make sure we're using the test database
echo "Setting up test database environment..."
export MYSQL_TEST_DATABASE=${MYSQL_TEST_DATABASE:-"onet_test_db"}
echo "Using test database: $MYSQL_TEST_DATABASE"

# Check if critical environment variables for this test are set
if [ -z "$ONET_USERNAME" ] || [ -z "$ONET_PASSWORD" ]; then
    echo "Error: Required environment variables (ONET_USERNAME, ONET_PASSWORD) are not set."
    echo "Please ensure they are defined in env/env.env"
    exit 1
fi

# Run the test with -s flag to show print statements and -v for verbose output
echo "Running integration test for get_occupation_and_skills API fallback function..."
python -m pytest tests/test_integration_get_occupation_and_skills_api_fallback.py -v -s

# Capture the exit code
exit_code=$?

# Deactivate the virtual environment if it was activated
if [ -d ".venv" ]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

echo "Integration test script finished."

# Exit with the test's exit code
exit $exit_code 