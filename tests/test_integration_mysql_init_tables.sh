#!/bin/bash

# Runs the integration test for mysql_init_tables.py (SQLAlchemy version)

# Set env variables
source ./env/env.env

# Activate the virtual environment
source ./.venv/bin/activate

# Run pytest
python -m pytest tests/test_integration_mysql_init_tables.py::test_actual_mysql_init_tables_sqlalchemy -v -s --capture=no --tb=short

# Deactivate the virtual environment
deactivate

echo "MySQL table initialization integration test script finished successfully." 