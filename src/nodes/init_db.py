import os
import sys
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.functions.mysql_create_db import mysql_create_db
from src.functions.mysql_connection import get_mysql_connection
from src.functions.mysql_init_tables import initialize_database_tables

def init_db_mysql() -> Dict[str, Any]:
    """
    Node that initializes the database and all database tables.
    
    This function:
    1. Creates the MySQL database if it doesn't exist
    2. Establishes a connection to the MySQL database
    3. Initializes all tables defined in the SQLAlchemy models
    
    Returns:
        Dict[str, Any]: A dictionary with keys:
            - 'success' (bool): Whether the operation was successful
            - 'message' (str): A message describing the result
            - 'result' (Dict): Empty dict or error details
    """
    print("=== Starting database initialization node ===")
    
    # Step 1: Create database if it doesn't exist
    print("Ensuring database exists...")
    db_create_result = mysql_create_db()
    
    if not db_create_result["success"]:
        # If we couldn't create the database, let's see if we can connect to it anyway
        # It might already exist, but the user might not have CREATE privileges
        print(f"Warning: {db_create_result['message']}")
        print("Attempting to continue with database connection...")
    else:
        print(db_create_result["message"])
    
    # Step 2: Establish database connection
    print("Establishing database connection...")
    connection_result = get_mysql_connection()
    
    if not connection_result["success"]:
        return {
            "success": False,
            "message": f"Failed to connect to MySQL database: {connection_result['message']}",
            "result": {}
        }
    
    print("Database connection established successfully.")
    
    # Close the connection as we don't need it directly (SQLAlchemy will create its own)
    if connection_result["result"] and connection_result["result"].is_connected():
        connection_result["result"].close()
    
    # Step 3: Initialize all database tables
    print("Initializing database tables...")
    init_result = initialize_database_tables()
    
    if not init_result["success"]:
        return {
            "success": False,
            "message": f"Failed to initialize database tables: {init_result['message']}",
            "result": {}
        }
    
    print("Database tables initialized successfully.")
    
    return {
        "success": True,
        "message": "Database initialized successfully with all required tables.",
        "result": {}
    }

if __name__ == "__main__":
    result = init_db_mysql()
    print(f"\nNode Execution Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    if result["success"]:
        print("Database is now ready for use.")
    else:
        print("Database initialization failed. Please check the error message above.")
        sys.exit(1)  # Exit with error code if initialization failed
