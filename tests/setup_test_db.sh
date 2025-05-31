#!/bin/bash
# Script to set up the test database with proper permissions

# Source environment variables
if [ -f "env/env.env" ]; then
    . env/env.env
else
    echo "Error: Environment file env/env.env not found"
    exit 1
fi

# Get database connection info
MYSQL_CONTAINER="mysql_db"  # Name of the MySQL Docker container
TEST_DB=${MYSQL_TEST_DATABASE:-onet_test_data}
TEST_USER=${MYSQL_TEST_USER:-$MYSQL_USER}
TEST_PASSWORD=${MYSQL_TEST_PASSWORD:-$MYSQL_PASSWORD}
ROOT_USER=${MYSQL_ROOT_USER:-root}
ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

# Check if the MySQL container is running
if ! docker ps | grep -q $MYSQL_CONTAINER; then
    echo "Error: MySQL container $MYSQL_CONTAINER is not running"
    echo "Start the container with: docker-compose up -d mysql_db"
    exit 1
fi

echo "Setting up test database: $TEST_DB"
echo "User to grant permissions to: $TEST_USER"

# Create database and grant privileges in one step
echo "Creating database and granting privileges..."
docker exec -i $MYSQL_CONTAINER mysql -u$ROOT_USER -p$ROOT_PASSWORD << EOF
-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS $TEST_DB;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON $TEST_DB.* TO '$TEST_USER'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Show the grants to verify
SHOW GRANTS FOR '$TEST_USER'@'%';
EOF

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to set up database. Check root credentials."
    exit 1
fi

echo "Successfully granted privileges to $TEST_USER for database $TEST_DB"

# Initialize database tables if needed
read -p "Do you want to initialize database tables? (y/n): " initialize_tables
if [[ "$initialize_tables" == "y" ]]; then
    echo "Initializing database tables..."
    
    # Temporarily override MYSQL_DATABASE to use the test database
    original_db=$MYSQL_DATABASE
    export MYSQL_DATABASE=$TEST_DB
    
    # Run the table initialization
    python -m src.functions.mysql_init_tables
    
    init_result=$?
    # Restore original database setting
    export MYSQL_DATABASE=$original_db
    
    if [ $init_result -eq 0 ]; then
        echo "Database tables initialized successfully."
    else
        echo "Failed to initialize database tables. Please check the error messages above."
        exit 1
    fi
fi

echo "Test database setup complete!" 