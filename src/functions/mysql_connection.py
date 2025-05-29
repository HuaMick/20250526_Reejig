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
    print("Attempting to get MySQL connection...")

    # Check for essential environment variables for the example to run
    required_vars = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    if not all(os.getenv(var) for var in required_vars):
        print(f"Error: Please ensure environment variables are set for: {required_vars}")
        print("You might need to source your env/env.env file before running this example.")
    else:
        connection_details = get_mysql_connection()
        print(f"Success: {connection_details['success']}")
        print(f"Message: {connection_details['message']}")

        if connection_details["success"] and connection_details["result"]:
            connection = connection_details["result"]
            try:
                if connection.is_connected():
                    print("Connection object is valid and connected.")
                    # Example: Print server info and current database
                    print(f"Server Info: {connection.get_server_info()}")
                    cursor = connection.cursor()
                    cursor.execute("SELECT DATABASE();")
                    database_name = cursor.fetchone()
                    print(f"Connected to database: {database_name[0] if database_name else 'N/A'}")
                    cursor.close()
                else:
                    print("Connection object reported as not connected.")
            except Error as e:
                print(f"Error while interacting with the connection: {e}")
            finally:
                if connection.is_connected():
                    connection.close()
                    print("MySQL connection closed.")
        elif connection_details["result"] is None and not connection_details["success"]:
            # Already handled by printing the message, this is just for clarity
            pass 