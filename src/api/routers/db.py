import os
from fastapi import APIRouter, HTTPException, status
from src.functions.mysql_connection import get_mysql_connection
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/db-diagnostics", tags=["diagnostics"])
async def db_diagnostics():
    """
    Diagnose database connection and list tables with row counts.
    """
    connection_details = get_mysql_connection()

    if not connection_details["success"]:
        logger.error(f"Database connection failed: {connection_details['message']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {connection_details['message']}",
        )

    connection = connection_details["result"]
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        table_info = []
        if tables:
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`;")
                row_count = cursor.fetchone()[0]
                table_info.append({"name": table_name, "rows": row_count})
        
        logger.info("Database diagnostics successful.")
        return {
            "status": "success",
            "message": "Database connection successful and tables listed.",
            "tables": table_info,
        }

    except Exception as e:
        logger.error(f"Error during database diagnostics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during database diagnostics: {str(e)}",
        )
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
