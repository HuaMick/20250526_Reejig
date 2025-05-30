#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Set env variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the extract and load script
python src/nodes/extract_load_txt.py

# Deactivate the virtual environment
deactivate

echo "O*NET data extraction and loading process finished successfully."
