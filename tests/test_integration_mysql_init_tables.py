# Always structure imports in test files using full paths from the project root
import pytest
import os
from src.functions.mysql_init_tables import initialize_database_tables # Updated import
from src.functions.mysql_connection import get_mysql_connection # For verification
from src.config.schemas import Base # To get expected table names

# This fixture is inherited from the connection test, ensuring env vars are checked
# If running this test standalone, ensure the .sh script for it sources env.env

EXPECTED_TABLES = list(Base.metadata.tables.keys()) # Get table names from SQLAlchemy metadata

def test_actual_mysql_init_tables_sqlalchemy(): # Renamed test function for clarity
    """
    Integration test that executes the SQLAlchemy table initialization.
    It then verifies that the expected tables have been created.
    Relies on MySQL service being up and environment variables being set.
    """
    print("\nAttempting to initialize MySQL tables using SQLAlchemy for integration test...")
    init_result = initialize_database_tables() # Call the new function

    assert init_result["success"], f"SQLAlchemy table initialization failed: {init_result['message']}"
    print(f"SQLAlchemy table initialization script executed: {init_result['message']}")

    # Verify tables exist
    print("Verifying table creation...")
    conn_details = get_mysql_connection()
    assert conn_details["success"], f"Failed to get connection for verification: {conn_details['message']}"
    
    connection = conn_details["result"]
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables_in_db = sorted([row[0] for row in cursor.fetchall()]) # Sort for consistent comparison
        print(f"Tables found in database: {tables_in_db}")

        # Sort expected tables as well for consistent comparison
        sorted_expected_tables = sorted(EXPECTED_TABLES)

        for table_name in sorted_expected_tables:
            assert table_name in tables_in_db, f"Expected table '{table_name}' not found in database after initialization."
            print(f"Verified: Table '{table_name}' exists.")
        
        assert len(tables_in_db) == len(sorted_expected_tables), \
            f"Expected {len(sorted_expected_tables)} tables ({sorted_expected_tables}), but found {len(tables_in_db)} tables ({tables_in_db})."

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection for verification closed.")
    
    print("MySQL table initialization integration test (SQLAlchemy) completed successfully!") 