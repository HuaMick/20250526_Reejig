import os
import sys
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config.schemas import get_sqlalchemy_engine, Occupation, Skill

def get_occupation_skills(occupation_code: str) -> Dict[str, Any]:
    """
    Retrieves skills data for a specific occupation code using SQLAlchemy ORM.
    
    Args:
        occupation_code (str): The O*NET occupation code (e.g. "15-1252.00")
        
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "result": {
                "occupation_title": str,
                "skills": [{
                    "element_id": str,
                    "element_name": str, 
                    "data_value": float
                }]
            }
        }
    """
    engine = get_sqlalchemy_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get occupation title
        occupation = session.query(Occupation).filter(
            Occupation.onet_soc_code == occupation_code
        ).first()
        
        if not occupation:
            return {
                "success": False,
                "message": f"Occupation code {occupation_code} not found",
                "result": {}
            }
            
        # Get skills data directly from Skills table
        skills_data = session.query(
            Skill.element_id,
            Skill.element_name
        ).all()
        
        if not skills_data:
            return {
                "success": False,
                "message": f"No skills found in the database",
                "result": {}
            }
            
        skills = [
            {
                "element_id": skill[0],
                "element_name": skill[1],
                "data_value": 1.0  # Default value since we're not using Occupation_Skills
            }
            for skill in skills_data
        ]
            
        return {
            "success": True,
            "message": "Successfully retrieved occupation skills",
            "result": {
                "occupation_title": occupation.title,
                "skills": skills
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Database error: {str(e)}",
            "result": {}
        }
    finally:
        session.close()

if __name__ == "__main__":
    # Example usage
    result = get_occupation_skills("15-1252.00")  # Software Developers
    print(result)
