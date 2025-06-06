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

# Run the example node script
python src/nodes/example_node.py

# Deactivate the virtual environment
deactivate

echo "Example node process finished successfully."
