import pytest
import mysql.connector
from mysql.connector import Error
import os
from tests.fixtures.db_config import test_db_config


def test_mysql_create_db(test_db_config):
    """Integration test to verify MySQL database creation."""
    # Get database credentials from environment variables
    host = test_db_config['host']
    user = test_db_config['user']
    password = test_db_config['password']
    db_name = test_db_config['database']
    
    # Connect to MySQL server
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Drop database if it exists
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            
            # Create database
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully")
            
            # Verify database was created
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            assert (db_name,) in databases, f"Database '{db_name}' was not created"
            
    except Error as e:
        pytest.fail(f"MySQL connection failed: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed") 