#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Set env variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# echo "Initializing database..."
# python src/nodes/init_db.py

echo "Extracting and loading data..."
python src/nodes/extract_load_txt.py

echo "Transforming data..."
python src/nodes/transform.py

# Deactivate the virtual environment
deactivate

echo "etl process finished successfully."
