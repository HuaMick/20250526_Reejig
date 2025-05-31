import os
import mysql.connector
from mysql.connector import Error
from typing import Dict, Any, Optional
from sqlalchemy.engine import Engine

def mysql_create_db(db_name=None, connection_params=None):
    """
    Creates a MySQL database if it doesn't already exist.
    If the user doesn't have CREATE DATABASE privileges, 
    checks if the database exists and can be connected to.
    
    Args:
        db_name (str, optional): Name of the database to create. 
                                If None, uses MYSQL_DATABASE environment variable.
        connection_params (dict, optional): Dictionary containing connection parameters
                                          (host, port, user, password).
                                          If None, uses environment variables.
    
    Returns:
        dict: A dictionary with keys:
            - 'success' (bool): Whether the operation was successful
            - 'message' (str): A message describing the result
            - 'result' (dict): Empty dict or error details
    """
    # Get database connection parameters from environment variables or connection_params
    if connection_params:
        db_host = connection_params.get('host', 'localhost')
        db_port = connection_params.get('port', '3306')
        db_user = connection_params.get('user')
        db_password = connection_params.get('password')
    else:
        db_host = os.getenv('MYSQL_HOST', 'localhost')
        db_port = os.getenv('MYSQL_PORT', '3306')
        db_user = os.getenv('MYSQL_USER')
        db_password = os.getenv('MYSQL_PASSWORD')
    
    # If db_name wasn't provided, get it from environment variable
    if db_name is None:
        db_name = os.getenv('MYSQL_DATABASE', 'onet_data')
    
    # Validate required parameters
    if not all([db_user, db_password]):
        return {
            "success": False,
            "message": "User and password are required for database connection.",
            "result": {}
        }
    
    try:
        # First try to connect directly to the database to see if it exists
        try:
            direct_connection = mysql.connector.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name
            )
            
            if direct_connection.is_connected():
                direct_connection.close()
                return {
                    "success": True,
                    "message": f"Database '{db_name}' already exists and is accessible.",
                    "result": {}
                }
        except Error as e:
            # If the error is "Unknown database", we need to create it
            # Any other error means we have connection issues or other problems
            if "Unknown database" not in str(e):
                return {
                    "success": False,
                    "message": f"Error connecting to database '{db_name}': {e}",
                    "result": {}
                }
        
        # Connect to MySQL server without specifying a database to create it
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if database exists (this might be redundant after our first check)
            cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
            database_exists = cursor.fetchone() is not None
            
            if not database_exists:
                try:
                    # Create database if it doesn't exist
                    cursor.execute(f"CREATE DATABASE {db_name}")
                    connection.commit()
                    message = f"Database '{db_name}' created successfully."
                except Error as e:
                    # Check if the error is about privileges
                    if "Access denied" in str(e) and ("CREATE" in str(e) or "create" in str(e)):
                        # User doesn't have create privileges, but that's okay if the DB exists
                        return {
                            "success": False,
                            "message": f"User lacks CREATE DATABASE privileges: {e}",
                            "result": {}
                        }
                    else:
                        # Some other error occurred
                        return {
                            "success": False,
                            "message": f"Error creating database: {e}",
                            "result": {}
                        }
            else:
                message = f"Database '{db_name}' already exists."
            
            cursor.close()
            connection.close()
            
            return {
                "success": True,
                "message": message,
                "result": {}
            }
        else:
            return {
                "success": False,
                "message": "MySQL connection failed (not connected).",
                "result": {}
            }
    except Error as e:
        return {
            "success": False,
            "message": f"Error creating database: {e}",
            "result": {}
        }

if __name__ == '__main__':
    print("Minimalistic happy path example for mysql_create_db:")
    print("This example assumes MYSQL_USER and MYSQL_PASSWORD environment variables are correctly set.")
    
    # 1. Call the function with default parameters
    result = mysql_create_db()
    
    # 2. Print the raw result from the function
    print("\nFunction Call Result:")
    print(result)
    
    print("\nExample finished.")
