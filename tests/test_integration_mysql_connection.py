# Always structure imports in test files using full paths from the project root
import pytest
import os
from src.functions.mysql_connection import get_mysql_connection
from tests.fixtures.db_config import test_db_config

def test_actual_mysql_connection(test_db_config):
    """
    Integration test that attempts a real connection to the MySQL test database,
    and executes a simple query to verify.
    Uses the test database configuration from conftest.py to ensure tests run in isolation.
    """
    print("\nAttempting MySQL connection for integration test...")
    
    # Pass test database configuration to the connection function
    connection_result = get_mysql_connection(connection_params=test_db_config)

    assert connection_result["success"], f"MySQL connection failed: {connection_result['message']}"
    assert connection_result["result"] is not None, "Connection object should not be None on success."

    print(f"Connection successful: {connection_result['message']}")

    connection = connection_result["result"]
    try:
        cursor = connection.cursor()
        
        print("Executing 'SELECT DATABASE();' to confirm database context...")
        cursor.execute("SELECT DATABASE();")
        current_db = cursor.fetchone()
        assert current_db is not None, "Failed to get current database."
        print(f"Connected to database: {current_db[0]}")
        
        # Assert that we are connected to the test database
        expected_db = test_db_config['database']
        assert current_db[0] == expected_db, f"Expected to connect to database '{expected_db}', but connected to '{current_db[0]}'"

        print("Executing 'SHOW TABLES;'...")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        print("Tables in the database:")
        if tables:
            for table in tables:
                table_name = table[0]
                # Get row count for each table
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`;")
                row_count = cursor.fetchone()[0]
                print(f"- {table_name} ({row_count} rows)")
        else:
            print("- No tables found.")
            # This is not necessarily a failure, could be an empty DB, but good to note.

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
    print("MySQL connection integration test completed successfully!")