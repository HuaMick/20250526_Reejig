#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Starting integration test suite by running individual .sh scripts..."

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Apply environment variables
echo "Sourcing environment variables..."
source env/env.env

# Define the base directory for test scripts
# Assuming .sh scripts are in the same directory as .py test files, e.g. tests/
TEST_SCRIPT_DIR="tests" # Modify if .sh scripts are elsewhere, e.g., "tests/scripts"

# List of Python test files (derived from run_test_suite.sh)
# The script will derive the .sh script name from these
PYTHON_TEST_FILES=(
    "test_integration_mysql_create_db.py"
    "test_integration_mysql_init_tables.py"
    "test_integration_mysql_connection.py"
    "test_integration_mysql_load.py"
    "test_integration_transform.py"
    "test_integration_api_extract_load_skills.py"
    "test_integration_api_extract_load_occupations.py"
    "test_integration_get_occupation_and_skills_api_fallback.py"
    "test_integration_get_occupation_skills.py"
    "test_integration_get_skills_gap.py"
    "test_integration_get_skills_gap_by_lvl.py"
)

# Get the project root directory to ensure scripts are called from there
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "Changing to project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

echo "Executing test scripts..."
for py_test_file in "${PYTHON_TEST_FILES[@]}"; do
    sh_test_file="${py_test_file%.py}.sh" # Replace .py with .sh
    full_sh_path="$TEST_SCRIPT_DIR/$sh_test_file"

    if [ -f "$full_sh_path" ]; then
        echo "----------------------------------------------------------------------"
        echo "Executing: $full_sh_path"
        echo "----------------------------------------------------------------------"
        # Ensure the .sh script itself is executable if it's not already
        # chmod +x "$full_sh_path" # Uncomment if you're sure you want to do this here
        
        # Execute the shell script.
        # If the scripts already handle venv and env vars, those parts above are redundant for each script
        # but keeping them for the overall suite script is good practice.
        "$full_sh_path"
        echo "----------------------------------------------------------------------"
        echo "Finished: $full_sh_path"
        echo "----------------------------------------------------------------------"
        echo # Add a blank line for readability

        echo "Waiting for 2 seconds..."
        sleep 2
    else
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "WARNING: Shell script not found: $full_sh_path"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    fi
done

echo "All specified integration test scripts have been attempted."

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Deactivating virtual environment..."
    deactivate
fi

echo "Integration test suite (using individual .sh scripts) completed."
