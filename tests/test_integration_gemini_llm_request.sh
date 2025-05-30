#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e 

# Apply environment variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Run the integration test with verbose output and showing print statements
python -m pytest tests/test_integration_gemini_llm_request.py::test_gemini_llm_request -v -s

# Run the test with custom parameters
python -m pytest tests/test_integration_gemini_llm_request.py::test_gemini_llm_request_with_params -v -s

# Deactivate the virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 