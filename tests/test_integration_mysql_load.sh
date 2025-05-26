#!/bin/bash

# This script runs the integration test for mysql_load.py

# Exit immediately if a command exits with a non-zero status.
set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)" # Assumes tests/ is one level down from project root

# Define paths
ENV_FILE="${PROJECT_ROOT}/env/env.env"
PYTHON_VENV="${PROJECT_ROOT}/.venv/bin/activate"
TEST_SCRIPT="${PROJECT_ROOT}/tests/test_integration_mysql_load.py"

# 1. Source environment variables
if [ -f "${ENV_FILE}" ]; then
    echo "Sourcing environment variables from ${ENV_FILE}..."
    source "${ENV_FILE}"
else
    echo "Error: Environment file ${ENV_FILE} not found."
    exit 1
fi

# 2. Activate Python virtual environment
if [ -f "${PYTHON_VENV}" ]; then
    echo "Activating Python virtual environment..."
    source "${PYTHON_VENV}"
else
    echo "Error: Python virtual environment not found at ${PYTHON_VENV}."
    echo "Please create it using: python -m venv .venv"
    exit 1
fi

# 3. Run the Python integration test script
echo "Running MySQL load integration test: ${TEST_SCRIPT}"
# Ensure PYTHONPATH is set so that src modules can be found if running from tests/ directory
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
python "${TEST_SCRIPT}"

# 4. Deactivate virtual environment (optional, as script end will do this)
if command -v deactivate &> /dev/null; then
    echo "Deactivating Python virtual environment..."
    deactivate
fi


echo "MySQL load integration test script finished successfully." 