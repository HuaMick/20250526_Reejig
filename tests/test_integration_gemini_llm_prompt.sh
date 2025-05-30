#!/bin/bash

# Integration test for gemini_llm_prompt function

# Exit immediately if a command exits with a non-zero status
set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

# Ensure virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

# Run the tests
echo "Running integration test for gemini_llm_prompt..."
python -m pytest tests/test_integration_gemini_llm_prompt.py::test_gemini_llm_prompt_to_only -v -s
python -m pytest tests/test_integration_gemini_llm_prompt.py::test_gemini_llm_prompt_with_from -v -s
python -m pytest tests/test_integration_gemini_llm_prompt.py::test_gemini_llm_prompt_invalid_to -v -s
python -m pytest tests/test_integration_gemini_llm_prompt.py::test_gemini_llm_prompt_invalid_from -v -s

# Print success message if all tests passed
echo "All integration tests for gemini_llm_prompt completed successfully!" 