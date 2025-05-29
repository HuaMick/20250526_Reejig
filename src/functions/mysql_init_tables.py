import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from src.config.schemas import Base # Import your Base and models
# from src.functions.mysql_connection import get_mysql_connection # No longer needed directly for table creation logic

def initialize_database_tables():
    """
    Initializes the database tables using SQLAlchemy models.
    Drops all known tables first, then creates them based on the model definitions.
    Relies on environment variables for database connection.

    Environment Variables Needed:
        MYSQL_HOST: Hostname of the MySQL server (defaults to 'localhost')
        MYSQL_PORT: Port of the MySQL server (defaults to 3306)
        MYSQL_USER: Username for MySQL connection
        MYSQL_PASSWORD: Password for MySQL connection
        MYSQL_DATABASE: Database name to connect to

    Returns:
        dict: A dictionary with keys 'success' (bool) and 'message' (str).
    """
    try:
        db_host = os.getenv('MYSQL_HOST', 'localhost')
        db_port = os.getenv('MYSQL_PORT', '3306')
        db_user = os.getenv('MYSQL_USER')
        db_password = os.getenv('MYSQL_PASSWORD')
        db_name = os.getenv('MYSQL_DATABASE', 'onet_data')

        if not all([db_user, db_password, db_name]):
            return {
                "success": False,
                "message": "MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE environment variables are required.",
                "result": {}
            }

        # Construct the database URL for SQLAlchemy
        # Ensure you have 'mysql-connector-python' installed for this dialect
        engine_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(engine_url)

        with engine.connect() as connection:
            # Temporarily disable foreign key checks to allow dropping tables in any order
            connection.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
            print("Temporarily disabled foreign key checks.")

            # Drop all tables defined in Base.metadata
            print("Dropping existing tables defined in SQLAlchemy metadata...")
            Base.metadata.drop_all(connection) # Pass connection here
            print("Tables dropped.")

            # Create all tables defined in Base.metadata
            print("Creating new tables based on SQLAlchemy metadata...")
            Base.metadata.create_all(connection) # Pass connection here
            print("Tables created.")

            # Re-enable foreign key checks
            connection.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
            print("Re-enabled foreign key checks.")
            
            connection.commit() # Commit the transaction that includes DDL and SET commands

        return {"success": True, "message": "Database tables initialized successfully using SQLAlchemy models.", "result": {}}

    except Exception as e:
        return {"success": False, "message": f"Error initializing database tables with SQLAlchemy: {e}", "result": {}}

if __name__ == '__main__':
    print("Minimalistic happy path example for initialize_database_tables:")
    print("This example assumes MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, and MYSQL_PORT environment variables are correctly set.")
    print("It will attempt to drop and recreate tables based on src/config/schemas.py.")

    # 1. Call the function
    result = initialize_database_tables()
    
    # 2. Print the raw result from the function
    print(f"\nFunction Call Result:")
    print(result)

    if result["success"]:
        print("  To verify, connect to the database and check tables.")
    print("\nExample finished.")
