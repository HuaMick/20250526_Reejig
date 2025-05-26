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
    print("Attempting to connect to MySQL database from local WSL environment...")
    
    # For local testing, ensure env/env.env is sourced or variables are set
    # For example, you can run: source env/env.env python src/functions/mysql_connection.py
    
    # Load environment variables from env/env.env if this script is run directly
    # This is a simple way for local testing; for Docker, env vars are passed differently.
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..')) # Add project root to path

    try:
        from dotenv import load_dotenv
        # Construct the path to env.env relative to this script
        # Script is in src/functions, env.env is in root/env/
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'env', 'env.env')
        
        # dotenv expects a .env file, not a shell script with `export`.
        # For direct testing, it's better to ensure `env/env.env` is sourced prior to running,
        # or manually set the required env vars if not using a .env file with dotenv.
        # The current `env/env.env` has `export` which `python-dotenv` won't process directly.
        
        # For this test, we'll rely on the user sourcing env/env.env or having them set globally.
        print(f"MYSQL_USER from env: {os.getenv('MYSQL_USER')}")
        print(f"MYSQL_DATABASE from env (defaulting if not set): {os.getenv('MYSQL_DATABASE', 'onet_data')}")

    except ImportError:
        print("python-dotenv is not installed. Please ensure environment variables are set or install it.")
        print("You might need to run 'source env/env.env' before running this script.")


    connection_status = get_mysql_connection()

    if connection_status["success"]:
        print(f"Successfully connected to MySQL database: {connection_status['message']}")
        if connection_status["result"]:
            db_info = connection_status["result"].get_server_info()
            print(f"Server Info: {db_info}")
            cursor = connection_status["result"].cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"You're connected to database: {record[0]}")
            cursor.close()
            connection_status["result"].close()
            print("MySQL connection closed.")
    else:
        print(f"Failed to connect to MySQL: {connection_status['message']}") 