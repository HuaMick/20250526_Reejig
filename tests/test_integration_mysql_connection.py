# Always structure imports in test files using full paths from the project root
import pytest
import os
from src.functions.mysql_connection import get_mysql_connection

@pytest.fixture(scope="module", autouse=True)
def ensure_env_vars_loaded():
    """
    Fixture to simulate sourcing env.env for test environment.
    This is a simplified approach for pytest. 
    For more robust CI/CD, environment variables should be managed by the execution environment.
    It assumes that running the test_integration_mysql_connection.sh script (which sources env.env)
    will make these available to the pytest process.
    This fixture primarily serves as a reminder and a place for potential future enhancements
    if direct pytest execution (without the .sh script) is desired.
    """
    # Check if critical env vars are present, print a message if not
    # The .sh script should handle the actual sourcing.
    required_vars = ["MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
    for var in required_vars:
        if not os.getenv(var):
            print(f"\nWarning: Environment variable {var} not found. \nEnsure env/env.env is sourced before running tests, or that the test runner script handles this.")
            # In a CI environment, you might want to `pytest.fail` here
            # For local testing, we allow it to proceed, relying on the .sh script or manual sourcing.
            break # Only print one warning

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