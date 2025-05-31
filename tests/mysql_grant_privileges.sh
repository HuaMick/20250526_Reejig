#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Source environment variables
source env/env.env

# Initialize DB_SETUP_RESULT
DB_SETUP_RESULT=1

# Prompt for the database name to use
DB_NAME=${1:-"onet_test_db"}
echo "Using database: $DB_NAME"

# Use Docker to connect to MySQL
echo "Granting privileges to user $MYSQL_USER for database $DB_NAME..."
docker exec -i mysql_db mysql -u$MYSQL_ROOT_USER -p$MYSQL_ROOT_PASSWORD << EOF
-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS $DB_NAME;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$MYSQL_USER'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Show the grants to verify
SHOW GRANTS FOR '$MYSQL_USER'@'%';
EOF

DB_SETUP_RESULT=$?

# Check if the command was successful
if [ $DB_SETUP_RESULT -eq 0 ]; then
    echo "Privileges granted successfully."
    
    # Update the test environment file with the database name
    cat > env/env.test.env << EOL
# MySQL Database Configuration
MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_PORT=${MYSQL_PORT:-3306}
MYSQL_USER=${MYSQL_USER}
MYSQL_PASSWORD=${MYSQL_PASSWORD}
MYSQL_DATABASE=$DB_NAME
MYSQL_ROOT_USER=${MYSQL_ROOT_USER}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

# O*NET API Configuration
ONET_API_USERNAME=${ONET_API_USERNAME:-$ONET_USERNAME}
ONET_API_PASSWORD=${ONET_API_PASSWORD:-$ONET_PASSWORD}

# Gemini API Configuration 
GEMINI_API_KEY=${GEMINI_API_KEY}
EOL
    
    echo "Created test environment file at env/env.test.env"
    
    # Initialize the tables
    echo "Initializing database tables..."
    source env/env.test.env
    python -m src.functions.mysql_init_tables
    
    if [ $? -eq 0 ]; then
        echo "Database setup complete. The test database $DB_NAME is ready for use."
    else
        echo "Failed to initialize database tables. Please check the error messages above."
    fi
else
    echo "Error: Failed to grant privileges. Please check your root password and MySQL connection settings."
fi

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 