import os
import sys
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config.schemas import get_sqlalchemy_engine, Occupation, Skill

def get_occupation_skills(occupation_code: str) -> Dict[str, Any]:
    """
    Retrieves 'LV' (Level) scale skills data for a specific occupation code using SQLAlchemy ORM.
    
    Args:
        occupation_code (str): The O*NET occupation code (e.g. "15-1252.00")
        
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "result": {
                "occupation_title": str,
                "skills": List[Dict[str, Any]]
            }
        }
    """
    engine = get_sqlalchemy_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get occupation title first to ensure occupation exists
        occupation = session.query(Occupation).filter(
            Occupation.onet_soc_code == occupation_code
        ).first()
        
        if not occupation:
            return {
                "success": False,
                "message": f"Occupation code {occupation_code} not found",
                "result": {"occupation_title": "Unknown", "skills": []}
            }
            
        # Get 'LV' scale skills data from the Skill table directly
        skills_query_result = session.query(
            Skill.element_id,
            Skill.element_name,
            Skill.scale_id,
            Skill.data_value
        ).filter(
            Skill.onet_soc_code == occupation_code,
            Skill.scale_id == 'LV' # Filter for 'LV' scale skills
        ).all()
        
        skills_list: List[Dict[str, Any]] = []
        if skills_query_result:
            for skill_data in skills_query_result:
                skills_list.append({
                    "element_id": skill_data.element_id,
                    "element_name": skill_data.element_name,
                    "scale_id": skill_data.scale_id, # Should be 'LV'
                    "data_value": skill_data.data_value # Actual data value from Skill table
                })
        
        # It's possible an occupation exists but has no 'LV' skills listed in the Skills table.
        # In this case, we return success True, with an empty skills list for this occupation.
        # The original PRD requirement was: "Compares two occupations and returns the skills required by the second occupation that are not present in the first"
        # identify_skill_gap handles missing skills by treating their data_value as 0.
        
        return {
            "success": True,
            "message": f"Successfully retrieved 'LV' scale skills for {occupation.title}" if skills_list else f"Occupation {occupation.title} found, but no 'LV' scale skills data available in the Skills table.",
            "result": {
                "occupation_title": occupation.title,
                "skills": skills_list
            }
        }
        
    except Exception as e:
        # Log the error for debugging
        # import traceback
        # print(f"Error in get_occupation_skills for {occupation_code}: {e}\n{traceback.format_exc()}")
        return {
            "success": False,
            "message": f"Database error while retrieving skills for {occupation_code}: {str(e)}",
            "result": {"occupation_title": "Error", "skills": []}
        }
    finally:
        session.close()

if __name__ == "__main__":
    # Example usage - Ensure your database is populated, especially Occupation_Skills with 'LV' scale data.
    print("--- Testing with Software Developers (15-1252.00) ---")
    result_dev = get_occupation_skills("15-1252.00") 
    print(result_dev)
    if result_dev['success'] and result_dev['result']['skills']:
        print(f"First skill for Software Developers: {result_dev['result']['skills'][0]}")

    print("\n--- Testing with Chemists (19-2031.00) ---")
    result_chem = get_occupation_skills("19-2031.00")
    print(result_chem)

    print("\n--- Testing with a known occupation that might have few/no LV skills in source (e.g., Chief Executives 11-1011.00) ---")
    result_ceo = get_occupation_skills("11-1011.00") # Chief Executives
    print(result_ceo)

    print("\n--- Testing with a non-existent occupation code (99-9999.99) ---")
    result_fake = get_occupation_skills("99-9999.99")
    print(result_fake)
