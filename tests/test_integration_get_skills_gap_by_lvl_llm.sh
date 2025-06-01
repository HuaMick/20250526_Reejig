#!/bin/bash

# Integration test script for get_skills_gap_by_lvl_llm function
# This script tests the LLM-enhanced skill gap analysis functionality

echo "=== Integration Test: LLM-Enhanced Skill Gap Analysis ==="
echo "Note: This test requires GEMINI_API_KEY environment variable"
echo "and may take time due to multiple LLM API calls."

# Activate the virtual environment
source .venv/bin/activate

# Apply environment variables
source env/env.env

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "WARNING: GEMINI_API_KEY is not set. Test may fail."
    echo "Please set your Gemini API key in env/env.env"
else
    echo "✓ GEMINI_API_KEY is configured"
fi

# Always use `python -m pytest` when running tests to ensure proper module resolution
# Run the test with -s flag to show print statements and -v for verbose output
echo "Running LLM-enhanced skill gap analysis integration tests..."
python -m pytest tests/test_integration_get_skills_gap_by_lvl_llm.py::test_get_skills_gap_by_lvl_llm_successful -v -s

echo ""
echo "Running error handling tests..."
python -m pytest tests/test_integration_get_skills_gap_by_lvl_llm.py::test_get_skills_gap_by_lvl_llm_invalid_occupation -v -s

echo ""
echo "Running same occupation tests..."
python -m pytest tests/test_integration_get_skills_gap_by_lvl_llm.py::test_get_skills_gap_by_lvl_llm_same_occupation -v -s

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

echo ""
echo "=== Integration Test Complete ===" 