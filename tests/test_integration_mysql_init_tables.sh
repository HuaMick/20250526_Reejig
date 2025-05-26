#!/bin/bash

# Get the directory of this script
SCRIPT_DIR=$(dirname "$0")

# Calculate the project root directory (assuming tests/ is one level down from root)
PROJECT_ROOT="$SCRIPT_DIR/.."

# Define the path to the environment file
ENV_FILE="$PROJECT_ROOT/env/env.env"

# Source environment variables if the file exists
if [ -f "$ENV_FILE" ]; then
  echo "Sourcing environment variables from $ENV_FILE for the test..."
  source "$ENV_FILE"
else
  echo "Warning: Environment file not found at $ENV_FILE. The test might fail if MYSQL_USER, MYSQL_PASSWORD, etc., are not set."
fi

# Check if critical variables are set (optional, but good practice for tests)
if [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ] || [ -z "${MYSQL_DATABASE:-onet_data}" ]; then # Defaulting MYSQL_DATABASE for check if not set
  echo "Error: MYSQL_USER, MYSQL_PASSWORD, or MYSQL_DATABASE (or its default) is not set in the environment."
  echo "Please ensure they are defined in $ENV_FILE or set globally."
  exit 1
fi

# Navigate to the project root to ensure pytest can find modules correctly
cd "$PROJECT_ROOT"

# Activate the virtual environment if it exists
VENV_PATH="./.venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
  echo "Activating Python virtual environment from $VENV_PATH..."
  source "$VENV_PATH"
else
  echo "Warning: Virtual environment activation script not found at $VENV_PATH. Pytest might not find dependencies."
fi

# Run the specific integration test using pytest
# -v for verbose output
# -s to show stdout (print statements from the test)
# --capture=no to ensure stdout is not captured by pytest
# --tb=short for a shorter traceback format
echo "Running MySQL table initialization (SQLAlchemy) integration test..."
python3 -m pytest tests/test_integration_mysql_init_tables.py::test_actual_mysql_init_tables_sqlalchemy -v -s --capture=no --tb=short

# Capture the exit code of pytest
PYTEST_EXIT_CODE=$?

if [ $PYTEST_EXIT_CODE -eq 0 ]; then
  echo "MySQL table initialization (SQLAlchemy) integration test PASSED."
else
  echo "MySQL table initialization (SQLAlchemy) integration test FAILED (Exit code: $PYTEST_EXIT_CODE)."
fi

exit $PYTEST_EXIT_CODE 