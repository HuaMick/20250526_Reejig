#!/bin/bash

# Integration test for the full LLM skill assessment pipeline

# Exit immediately if a command exits with a non-zero status
set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

# Ensure virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

# Run the test
echo "Running integration test for LLM skill assessment pipeline..."
python -m pytest tests/test_integration_llm_skill_assessment_pipeline.py::test_llm_skill_assessment_pipeline_happy_path -v -s

# Print success message if all tests passed
echo "LLM skill assessment pipeline integration test completed successfully!" 