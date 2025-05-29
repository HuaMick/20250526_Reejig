import os
import mysql.connector
from mysql.connector import Error

def get_mysql_connection():
    """
    Establishes a connection to the MySQL database using environment variables.

    Environment Variables Needed:
        MYSQL_HOST: Hostname of the MySQL server (defaults to 'localhost')
        MYSQL_PORT: Port of the MySQL server (defaults to 3306)
        MYSQL_USER: Username for MySQL connection
        MYSQL_PASSWORD: Password for MySQL connection
        MYSQL_DATABASE: Database name to connect to

    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str), 
              and 'result' (mysql.connector.connection_cext.CMySQLConnection or None).
    """
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_port = os.getenv('MYSQL_PORT', '3306')
    db_user = os.getenv('MYSQL_USER')
    db_password = os.getenv('MYSQL_PASSWORD')
    db_name = os.getenv('MYSQL_DATABASE', 'onet_data') # Default from docker-compose

    if not all([db_user, db_password]):
        return {
            "success": False,
            "message": "MYSQL_USER and MYSQL_PASSWORD environment variables are required.",
            "result": None
        }

    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        if connection.is_connected():
            return {
                "success": True,
                "message": "MySQL connection successful.",
                "result": connection
            }
        else:
            return {
                "success": False,
                "message": "MySQL connection failed (not connected).",
                "result": None
            }
    except Error as e:
        return {
            "success": False,
            "message": f"Error connecting to MySQL: {e}",
            "result": None
        }

if __name__ == '__main__':
    print("Minimalistic happy path example for get_mysql_connection:")
    print("This example assumes MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, and MYSQL_PORT environment variables are correctly set.")

    # 1. Call the function
    connection_details = get_mysql_connection()

    # 2. Print the raw result from the function
    print("\nFunction Call Result:")
    print(connection_details)

    # 3. If a connection was made, perform a minimal action and ensure it's closed (as per function's responsibility if not auto-closed)
    if connection_details["success"] and connection_details["result"]:
        connection = connection_details["result"]
        # The function get_mysql_connection returns an active connection that the caller is responsible for closing.
        if hasattr(connection, 'is_connected') and connection.is_connected():
            print("Connection was successful, closing it now as part of the example cleanup.")
            connection.close()
    print("\nExample finished.") 