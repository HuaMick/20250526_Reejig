import os
import mysql.connector
from typing import Dict, Any, List

def mysql_query(query: str) -> Dict[str, Any]:
    """
    Execute a MySQL query and return results in a standardized format.
    
    Args:
        query (str): The SQL query to execute
        
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "result": {
                "columns": List[str],
                "rows": List[tuple]
            }
        }
    """
    try:
        # Get database connection details from environment variables
        db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': os.getenv('MYSQL_PORT', '3306'),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE'),
        }
        
        # Validate required environment variables
        if not all([db_config['user'], db_config['password'], db_config['database']]):
            return {
                "success": False,
                "message": "Missing required database environment variables",
                "result": {}
            }
            
        # Create connection
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        return {
            "success": True,
            "message": "Query executed successfully",
            "result": {
                "columns": columns,
                "rows": rows
            }
        }
        
    except mysql.connector.Error as e:
        return {
            "success": False,
            "message": f"Database error: {str(e)}",
            "result": {}
        }
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Minimalistic happy path example for mysql_query:")
    print("This example assumes MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, and MYSQL_PORT environment variables are correctly set.")
    print("It also assumes the 'Occupations' table exists and has data.")

    # 1. Define a simple query for the happy path
    # This query should successfully execute if the database and table exist.
    test_query = "SELECT onet_soc_code, title FROM Occupations LIMIT 2;"

    # 2. Call the function
    print(f"\nExecuting query: \"{test_query}\"...")
    query_result = mysql_query(test_query)
    
    # 3. Print the result summary
    print(f"\nFunction Call Result for query '{test_query}':")
    print(f"  Success: {query_result['success']}")
    print(f"  Message: {query_result['message']}")

    if query_result['success'] and query_result.get('result'):
        print(f"  Columns: {query_result['result'].get('columns')}")
        rows = query_result['result'].get('rows', [])
        print(f"  Rows returned: {len(rows)}")
        if rows:
            print(f"  First row example: {rows[0]}")
            
    print("\nExample finished.")
