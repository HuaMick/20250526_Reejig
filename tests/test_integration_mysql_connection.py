# Always structure imports in test files using full paths from the project root
import pytest
import os
from src.functions.mysql_connection import get_mysql_connection
from tests.test_adapter import ensure_test_env

# No need to define ensure_env_vars_loaded fixture since we're using ensure_test_env from test_adapter

def test_actual_mysql_connection():
    """
    Integration test that attempts a real connection to the MySQL database,
    and executes a simple query to verify.
    Relies on the MySQL service from docker-compose.yml being up and accessible,
    and environment variables (MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE) being set.
    """
    print("\nAttempting MySQL connection for integration test...")
    connection_result = get_mysql_connection()

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
        # Assert that we are connected to the expected database if MYSQL_DATABASE is set
        expected_db = os.getenv("MYSQL_DATABASE", "onet_data")
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