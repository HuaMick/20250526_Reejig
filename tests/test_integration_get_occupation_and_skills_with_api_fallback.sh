#!/bin/bash

# Integration test for get_occupation_and_skills function with API fallback logic

# Exit immediately if a command exits with a non-zero status
set -e

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to the project root
# If script is in tests/, project root is one level up.
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT" || exit 1

# Activate the virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment .venv not found in project root ${PWD}."
    exit 1
fi

# Apply environment variables
ENV_FILE="./env/env.env"
if [ -f "$ENV_FILE" ]; then
  source "$ENV_FILE"
else
  echo "Error: Environment file not found at $PWD/$ENV_FILE"
  exit 1
fi

# Check if critical environment variables for this test are set
if [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ] || [ -z "$MYSQL_DATABASE" ] || [ -z "$ONET_USERNAME" ] || [ -z "$ONET_PASSWORD" ]; then
  echo "Error: Required environment variables (MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, ONET_USERNAME, ONET_PASSWORD) are not set."
  echo "Please ensure they are defined in $ENV_FILE"
  exit 1
fi

# Define test file and function if needed, or run all tests in the file
TEST_FILE="tests/test_integration_get_occupation_and_skills_with_api_fallback.py"
# To run a specific function: TEST_TARGET="${TEST_FILE}::test_get_occupation_and_skills_api_fallback"
# To run all tests in the file: 
TEST_TARGET="${TEST_FILE}"


echo "\nRunning integration test: ${TEST_TARGET}..."
# Always use `python -m pytest` when running tests to ensure proper module resolution
# Run the test with -s flag to show print statements and -v for verbose output
python -m pytest "${TEST_TARGET}" -v -s

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    if command -v deactivate &> /dev/null; then # Check if deactivate command exists
        deactivate
    fi
fi

echo "\nIntegration test script finished." 