#!/bin/bash

# Integration test for generate_skill_proficiency_prompt function

# Exit immediately if a command exits with a non-zero status
set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

# Ensure virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

# Run the tests
echo "Running integration test for generate_skill_proficiency_prompt..."
python -m pytest tests/test_integration_generate_skill_proficiency_prompt.py::test_generate_skill_proficiency_prompt -v -s

# Print success message if all tests passed
echo "All integration tests for generate_skill_proficiency_prompt completed successfully!" 