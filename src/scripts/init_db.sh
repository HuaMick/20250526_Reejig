#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Change to the project root directory using git
cd "$(git rev-parse --show-toplevel)" || exit 1

# Set env variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Initializing database tables..."
python -m src.nodes.init_db

# Check the exit code
if [ $? -eq 0 ]; then
    echo "Database initialization completed successfully!"
else
    echo "Database initialization failed!"
    exit 1
fi

# Deactivate the virtual environment
deactivate

echo "Database initialization process finished." 