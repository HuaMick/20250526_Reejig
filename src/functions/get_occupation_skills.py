from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List

from src.config.schemas import get_sqlalchemy_engine, Onet_Occupations_Landing, Occupation_Skills, Skills

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
        occupation = session.query(Onet_Occupations_Landing).filter(
            Onet_Occupations_Landing.onet_soc_code == occupation_code
        ).first()
        
        if not occupation:
            return {
                "success": False,
                "message": f"Occupation code {occupation_code} not found",
                "result": {"occupation_title": "Unknown", "skills": []}
            }
            
        # Get skills data from the OccupationSkills and SkillsReference tables
        skills_query_result = session.query(
            Occupation_Skills.element_id,
            Skills.element_name,
            Occupation_Skills.proficiency_level
        ).join(
            Skills,
            Occupation_Skills.element_id == Skills.element_id
        ).filter(
            Occupation_Skills.onet_soc_code == occupation_code
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
    
    # 3. Print the result summary
    print(f"\nFunction Call Result for {occupation_code}:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")

    if result['success'] and result.get('result'):
        res_data = result['result']
        print(f"  Occupation Title: {res_data.get('occupation_title')}")
        print(f"  Number of skills found: {len(res_data.get('skills', []))}")
        if res_data.get('skills'):
            print(f"  First skill: {res_data['skills'][0]}")
    
    print("\nExample finished.")
