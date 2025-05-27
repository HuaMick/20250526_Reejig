#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Source environment variables (assuming env/env.env exists)
if [ -f "env/env.env" ]; then
    source env/env.env
else
    echo "Warning: env/env.env not found. Database credentials might be missing."
    # Optionally, exit here if env.env is critical and not found
    # exit 1 
fi

# Activate the virtual environment (assuming .venv exists)
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Warning: .venv directory not found. Virtual environment not activated."
fi

# Set PYTHONPATH to include the src directory
export PYTHONPATH=$(pwd):$(pwd)/src:$PYTHONPATH

# Run pytest
python -m pytest tests/test_integration_skill_gap_process.py -v -s --capture=no --tb=short

# Deactivate virtual environment if it was sourced and deactivate command exists
if type deactivate > /dev/null 2>&1 && [ -n "$VIRTUAL_ENV" ] && [ -f ".venv/bin/activate" ]; then
    deactivate
fi 