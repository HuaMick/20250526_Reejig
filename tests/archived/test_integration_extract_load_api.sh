#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Activate the virtual environment if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
  echo "Activating virtual environment..."
  source "$PROJECT_ROOT/.venv/bin/activate"
else
  echo "Virtual environment not found at $PROJECT_ROOT/.venv"
fi

# Source environment variables if env/env.env exists
if [ -f "$PROJECT_ROOT/env/env.env" ]; then
  echo "Sourcing environment variables from env/env.env..."
  source "$PROJECT_ROOT/env/env.env"
else
  echo "env/env.env not found, ensure necessary environment variables (e.g., for API) are set."
fi

# Set PYTHONPATH to include the project root (which contains src, tests, etc.)
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "Running integration test for extract_load_api node..."

# Run the specific pytest test file and function
# -s: show print statements, -v: verbose output
python -m pytest "$PROJECT_ROOT/tests/test_integration_extract_load_api.py::test_extract_load_api_node_targeted" -v -s

TEST_EXIT_CODE=$?

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
  echo "Deactivating virtual environment..."
  deactivate
fi

if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "Integration test completed successfully."
else
  echo "Integration test failed with exit code $TEST_EXIT_CODE."
fi

exit $TEST_EXIT_CODE 