#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to the project root (assuming scripts are in src/scripts)
PROJECT_ROOT="$SCRIPT_DIR/../../"

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT.venv" ]; then
  echo "Activating virtual environment..."
  source "$PROJECT_ROOT.venv/bin/activate"
fi

# Set PYTHONPATH to include the src directory
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Define the path to the node script
NODE_SCRIPT="$PROJECT_ROOT/src/nodes/extract_load_api.py"

echo "Executing O*NET API Extract and Load Node..."

# Execute the Python node script
python "$NODE_SCRIPT"

# Deactivate virtual environment if it was activated
if [ -d "$PROJECT_ROOT.venv" ] && [ -n "$VIRTUAL_ENV" ]; then
  echo "Deactivating virtual environment..."
  deactivate
fi

echo "Node execution finished." 