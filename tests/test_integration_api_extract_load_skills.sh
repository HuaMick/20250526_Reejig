#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment .venv not found. Please ensure it is created and dependencies are installed."
fi

# Apply environment variables from env/env.env if it exists
if [ -f "env/env.env" ]; then
    echo "Loading environment variables from env/env.env..."
    source env/env.env
else
    echo "Warning: Environment file env/env.env not found. API credentials might be missing."
fi

# Make sure we're using the test database
echo "Setting up test database environment..."
export MYSQL_TEST_DATABASE=${MYSQL_TEST_DATABASE:-"onet_test_db"}
echo "Using test database: $MYSQL_TEST_DATABASE"

# Add project src to PYTHONPATH to ensure modules are found
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
echo "PYTHONPATH set to: $PYTHONPATH"

# Define the test file and function
TEST_FILE="tests/test_integration_api_extract_load_skills.py"
TEST_FUNCTION="test_extract_and_load_filtered_api_skills"

echo "Running integration test: ${TEST_FILE}::${TEST_FUNCTION}"

# Always use `python -m pytest` when running tests to ensure proper module resolution
# Run the test with -s flag to show print statements (and logs) and -v for verbose output
python -m pytest "${TEST_FILE}::${TEST_FUNCTION}" -v -s

EXIT_CODE=$?

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo "Integration test completed successfully."
else
    echo "Integration test failed with exit code $EXIT_CODE."
fi

exit $EXIT_CODE 