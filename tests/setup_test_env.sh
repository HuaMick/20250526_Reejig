#!/bin/bash
# Script to set up test environment for O*NET data pipeline tests

# Exit on error
set -e

echo "Setting up test environment..."

# Create test environment directory if it doesn't exist
mkdir -p env

# Check if env.test.env already exists
if [ -f "env/env.test.env" ]; then
    echo "Test environment file env/env.test.env already exists."
    echo "Do you want to overwrite it? (y/n)"
    read -r answer
    if [ "$answer" != "y" ]; then
        echo "Aborting test environment setup."
        exit 0
    fi
fi

# Get current database settings from env.dev.env if it exists
if [ -f "env/env.dev.env" ]; then
    echo "Loading database settings from env.dev.env..."
    source env/env.dev.env
fi

# Set default values if not already set
MYSQL_HOST=${MYSQL_HOST:-"localhost"}
MYSQL_PORT=${MYSQL_PORT:-"3306"}
MYSQL_USER=${MYSQL_USER:-"root"}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-"password"}
MYSQL_DATABASE="onet_test"  # Always use a test database for tests

# Create env.test.env file
cat > env/env.test.env << EOF
# Test environment variables
MYSQL_HOST=${MYSQL_HOST}
MYSQL_PORT=${MYSQL_PORT}
MYSQL_USER=${MYSQL_USER}
MYSQL_PASSWORD=${MYSQL_PASSWORD}
MYSQL_DATABASE=${MYSQL_DATABASE}

# O*NET API credentials (if available)
ONET_USERNAME=${ONET_USERNAME:-""}
ONET_PASSWORD=${ONET_PASSWORD:-""}
EOF

echo "Created test environment file at env/env.test.env"

# Check if we can connect to MySQL
if command -v mysql &> /dev/null; then
    echo "Checking MySQL connection..."
    if mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" &> /dev/null; then
        echo "MySQL connection successful."
        
        # Create test database if it doesn't exist
        echo "Creating test database $MYSQL_DATABASE if it doesn't exist..."
        mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;"
        
        echo "Test database $MYSQL_DATABASE is ready."
    else
        echo "Warning: Could not connect to MySQL. Make sure MySQL is running and credentials are correct."
        echo "You can update the credentials in env/env.test.env."
    fi
else
    echo "Warning: MySQL client not found. Skipping database creation."
    echo "You'll need to create the test database manually."
fi

echo "Test environment setup complete." 