import os
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, Optional
from sqlalchemy.engine import Engine

from src.config.schemas import get_sqlalchemy_engine, Onet_Occupations_Landing

def get_occupation(occupation_code: str, engine: Optional[Engine] = None) -> Dict[str, Any]:
    """
    Retrieves basic information about an occupation using its O*NET SOC code.
    
    Args:
        occupation_code (str): The O*NET occupation code (e.g. "15-1252.00")
        engine (Optional[Engine]): SQLAlchemy engine to use for database operations,
                                  or None to use the default engine
        
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "result": {
                "onet_soc_code": str,
                "title": str,
                "description": str
            }
        }
    """
    if engine is None:
        engine = get_sqlalchemy_engine()
        
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query the occupation data
        occupation = session.query(Onet_Occupations_Landing).filter(
            Onet_Occupations_Landing.onet_soc_code == occupation_code
        ).first()
        
        if not occupation:
            return {
                "success": False,
                "message": f"Occupation code {occupation_code} not found",
                "result": {}
            }
            
        # Return the occupation data
        return {
            "success": True,
            "message": f"Successfully retrieved occupation data for {occupation.title}",
            "result": {
                "onet_soc_code": occupation.onet_soc_code,
                "title": occupation.title,
                "description": occupation.description
            }
        }
        
    except Exception as e:
        error_message = f"Database error while retrieving occupation data for {occupation_code}: {str(e)}"
        print(error_message)
        return {
            "success": False,
            "message": error_message,
            "result": {}
        }
    finally:
        session.close()

if __name__ == "__main__":
    print("Minimalistic happy path example for get_occupation:")
    print("This example assumes a populated database with O*NET data and configured environment variables.")
    print("It attempts to retrieve data for a known occupation code.")

    # Define a known occupation code for the happy path
    # For this example to work, "15-1252.00" (Software Developers) should exist in the Occupations table
    occupation_code = "15-1252.00"

    # Call the function
    print(f"\n--- Attempting to get occupation data for: {occupation_code} ---")
    result = get_occupation(occupation_code)
    
    # Print the result
    print(f"\nFunction Call Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    if result['success']:
        print(f"  Occupation Data:")
        print(f"    - SOC Code: {result['result']['onet_soc_code']}")
        print(f"    - Title: {result['result']['title']}")
        description = result['result'].get('description', '')
        print(f"    - Description: {description[:100]}..." if description else "    - Description: None")
    
    print("\nExample finished.") 