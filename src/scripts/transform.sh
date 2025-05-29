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

# Optional: Set data source (defaults to text_file if not set)
export DATA_SOURCE="${DATA_SOURCE:-text_file}"

# Run the transform node
python src/nodes/transform.py

# Deactivate the virtual environment
deactivate

echo "O*NET data transformation process finished successfully." 