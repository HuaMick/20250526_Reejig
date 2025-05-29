import os
# import sys # Removed sys.path modification
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List

# Add project root to sys.path - This line is removed
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config.schemas import get_sqlalchemy_engine, Occupation, OccupationSkill, SkillReference

def get_occupation_skills(occupation_code: str) -> Dict[str, Any]:
    """
    Retrieves skills data for a specific occupation code using the downstream tables.
    
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
            
        # Get skills data from the OccupationSkills and SkillsReference tables
        skills_query_result = session.query(
            OccupationSkill.element_id,
            SkillReference.element_name,
            OccupationSkill.proficiency_level
        ).join(
            SkillReference,
            OccupationSkill.element_id == SkillReference.element_id
        ).filter(
            OccupationSkill.onet_soc_code == occupation_code
        ).all()
        
        skills_list: List[Dict[str, Any]] = []
        if skills_query_result:
            for skill_data in skills_query_result:
                skills_list.append({
                    "element_id": skill_data.element_id,
                    "element_name": skill_data.element_name,
                    "scale_id": "LV",  # This is now implicit as we only store LV scale in OccupationSkills
                    "data_value": skill_data.proficiency_level
                })
        
        return {
            "success": True,
            "message": f"Successfully retrieved skills for {occupation.title}" if skills_list else f"Occupation {occupation.title} found, but no skills data available.",
            "result": {
                "occupation_title": occupation.title,
                "skills": skills_list
            }
        }
        
    except Exception as e:
        # Log the error for debugging - Removed commented out traceback
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
    print("Minimalistic happy path example for get_occupation_skills:")
    print("This example assumes a populated database with O*NET data and configured environment variables.")
    print("It attempts to retrieve skills for a known occupation code.")

    # 1. Define a known occupation code for the happy path
    # For this example to work, "15-1252.00" (Software Developers) should exist and have LV skills.
    occupation_code = "15-1252.00"

    # 2. Call the function
    print(f"\n--- Attempting to get skills for occupation: {occupation_code} ---")
    result = get_occupation_skills(occupation_code)
    
    # 3. Print the raw result from the function
    print(f"\nFunction Call Result:")
    print(result) # Prints the full success/message/result dictionary

    # Optionally, print a summary if successful and skills are found
    if result['success'] and result['result'] and result['result']['skills']:
        print(f"  Successfully found {len(result['result']['skills'])} skills for {result['result']['occupation_title']}.")
        print(f"  Sample skill: {result['result']['skills'][0]}")
    elif result['success']:
        print(f"  Call was successful, but no skills found for {result.get('result', {}).get('occupation_title', occupation_code)} or occupation not found as per message.")

    print("\nExample finished.")
