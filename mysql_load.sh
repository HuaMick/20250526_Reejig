#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# mysql_load.sh - Load O*NET data files into MySQL database

echo "=== MySQL Data Loading Script ==="
echo "This script loads data from database/occupations.txt and database/skills.txt into MySQL"

# Set env variables
echo "Sourcing environment variables..."
source ./env/env.env

# Activate the virtual environment
echo "Activating virtual environment..."
source ./.venv/bin/activate

# Verify data files exist
echo "Checking for required data files..."
if [ ! -f "database/occupations.txt" ]; then
    echo "ERROR: database/occupations.txt not found"
    deactivate
    exit 1
fi

if [ ! -f "database/skills.txt" ]; then
    echo "ERROR: database/skills.txt not found"
    deactivate
    exit 1
fi

echo "✓ Found database/occupations.txt"
echo "✓ Found database/skills.txt"

# Initialize database tables first (optional but recommended for clean load)
echo ""
echo "=== Initializing Database Tables ==="
python src/functions/mysql_init_tables.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to initialize database tables"
    deactivate
    exit 1
fi

# Load data using the mysql_load.py script
echo ""
echo "=== Loading Data into MySQL ==="
python src/functions/mysql_load.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to load data into MySQL"
    deactivate
    exit 1
fi

# Verify the data was loaded by running a quick connection test
echo ""
echo "=== Verifying Data Load ==="
python -c "
from src.functions.mysql_connection import get_mysql_connection

print('Connecting to MySQL to verify data load...')
conn_result = get_mysql_connection()
if not conn_result['success']:
    print(f'ERROR: Could not connect to MySQL: {conn_result[\"message\"]}')
    exit(1)

connection = conn_result['result']
cursor = connection.cursor()

tables = ['Occupations', 'Skills', 'Occupation_Skills']
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'{table}: {count} rows')

cursor.close()
connection.close()
print('✓ Data verification complete')
"

if [ $? -ne 0 ]; then
    echo "ERROR: Data verification failed"
    deactivate
    exit 1
fi

# Deactivate the virtual environment
deactivate

echo ""
echo "=== MySQL Data Loading Complete ==="
echo "✓ Database tables initialized"
echo "✓ Data loaded from database/occupations.txt and database/skills.txt"
echo "✓ Data verification successful"
echo ""
echo "You can now run integration tests or use the get_skill_gap function." 