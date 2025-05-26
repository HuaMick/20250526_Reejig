#!/bin/bash

# Get the directory of the script
SCRIPT_DIR=$(dirname "$0")

# Source environment variables from env/env.env relative to the script's location
ENV_FILE="$SCRIPT_DIR/../env/env.env"

if [ -f "$ENV_FILE" ]; then
  echo "Sourcing environment variables from $ENV_FILE..."
  source "$ENV_FILE"
else
  echo "Error: Environment file not found at $ENV_FILE"
  exit 1
fi

# Check if critical variables are set (optional, but good practice)
if [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ]; then
  echo "Error: MYSQL_USER or MYSQL_PASSWORD is not set in the environment."
  echo "Please ensure they are defined in $ENV_FILE"
  exit 1
fi

echo "Running docker-compose up..."
# Navigate to the project root (where docker-compose.yml is located)
cd "$SCRIPT_DIR/.."

# Run docker-compose up. Add -d to run in detached mode if preferred.
# Use "docker compose" for V2, not "docker-compose"
docker compose up
