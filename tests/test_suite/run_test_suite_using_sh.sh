#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "Starting integration test suite within Docker container..."

# Environment variables should be injected by Docker Compose.
# If env/env.env is copied into the image and needed explicitly by this script:
# ENV_FILE="env/env.env"
# if [ -f "$ENV_FILE" ]; then
#   echo "Sourcing environment variables from $ENV_FILE..."
#   source "$ENV_FILE"
# else
#   echo "Warning: Environment file $ENV_FILE not found inside the container."
# fi

# The Python environment is managed by the Docker container, so venv activation is not needed.
# # Activate the virtual environment
# echo "Activating virtual environment..."
# source .venv/bin/activate

# Define the base directory for test scripts
TEST_SCRIPT_DIR="tests" 

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
    # Add "test_integration_llm_skill_assessment_pipeline.py" etc. when ready
)

# The script should already be in the project root (/app by default in Dockerfile.test_runner)
# PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# echo "Changing to project root: $PROJECT_ROOT"
# cd "$PROJECT_ROOT"

echo "Executing test scripts..."
for py_test_file in "${PYTHON_TEST_FILES[@]}"; do
    sh_test_file="${py_test_file%.py}.sh" 
    full_sh_path="$TEST_SCRIPT_DIR/$sh_test_file"

    if [ -f "$full_sh_path" ]; then
        echo "----------------------------------------------------------------------"
        echo "Executing: $full_sh_path"
        echo "----------------------------------------------------------------------"
        # Ensure the individual .sh test scripts are executable (Dockerfile.test_runner helps with the main one)
        # If these are not executable, they might need `bash $full_sh_path` or `chmod +x` in Dockerfile
        # For now, assuming they are executable or will be run with bash/sh explicitly if needed.
        if [ -x "$full_sh_path" ]; then
            "$full_sh_path"
        else
            bash "$full_sh_path"
        fi
        echo "----------------------------------------------------------------------"
        echo "Finished: $full_sh_path"
        echo "----------------------------------------------------------------------"
        echo 

        echo "Waiting for 2 seconds..."
        sleep 2
    else
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "WARNING: Shell script not found: $full_sh_path"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    fi
done

echo "All specified integration test scripts have been attempted."

# Deactivation of venv is not needed in Docker.
# if [ -n "$VIRTUAL_ENV" ]; then
#     echo "Deactivating virtual environment..."
#     deactivate
# fi

echo "Integration test suite (using individual .sh scripts) completed within Docker."
