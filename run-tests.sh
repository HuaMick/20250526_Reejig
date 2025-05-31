#!/bin/bash
# Script to run pytest with test database configuration

# Check if env.env exists
if [ ! -f "env/env.env" ]; then
    echo "Error: Environment file env/env.env not found"
    exit 1
fi

# Source environment variables
. env/env.env

# Store original database setting
ORIGINAL_DB=$MYSQL_DATABASE

# Use test database for tests
export MYSQL_DATABASE=${MYSQL_TEST_DATABASE:-onet_test_data}
echo "Using test database: $MYSQL_DATABASE"

# Check if test database exists
if command -v docker &> /dev/null; then
    echo "Checking if test database exists..."
    if ! docker exec mysql_db mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -e "USE $MYSQL_DATABASE" 2>/dev/null; then
        echo "Test database does not exist or user lacks permissions."
        echo "Please run tests/setup_test_db.sh to set up the test database."
        echo "Continue anyway? (y/n)"
        read -r answer
        if [ "$answer" != "y" ]; then
            echo "Aborting."
            # Restore original database setting
            export MYSQL_DATABASE=$ORIGINAL_DB
            exit 1
        fi
    else
        echo "Test database exists and user has access."
    fi
else
    echo "Warning: Docker not found. Skipping database check."
fi

# Run pytest with any passed arguments
echo "Running tests with test database ($MYSQL_DATABASE)..."
pytest "$@"
TEST_RESULT=$?

# Restore original database setting
export MYSQL_DATABASE=$ORIGINAL_DB

exit $TEST_RESULT 