#!/bin/bash

# Navigate to project root
cd "$(dirname "$0")/../.."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Load environment variables
source env/env.env

# Set PYTHONPATH for imports
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the API server
echo "Starting O*NET Skills Gap API server..."
python -m src.api.main

# Deactivate virtual environment when done
if [ -d ".venv" ]; then
    deactivate
fi 