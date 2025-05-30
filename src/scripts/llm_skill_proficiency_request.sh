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

OCCUPATION_CODE="11-1011.00"

echo "Executing LLM Skill Proficiency Request Node for occupation code: ${OCCUPATION_CODE}..."

# Run the node script, passing the occupation code as an argument
python src/nodes/llm_skill_proficiency_request.py "${OCCUPATION_CODE}"

# Deactivate the virtual environment
deactivate

echo "LLM Skill Proficiency Request Node finished successfully for occupation code: ${OCCUPATION_CODE}." 