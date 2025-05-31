from typing import Optional
from sqlalchemy.engine import Engine
from src.config.schemas import get_sqlalchemy_engine
from src.functions.get_occupation_and_skills import get_occupation_and_skills

def get_skills_gap(from_onet_soc_code: str, to_onet_soc_code: str, engine: Optional[Engine] = None):
    """
    Identifies skills that are present in the target occupation but not in the source occupation.
    
    This function:
    1. Retrieves skills data for both occupations using get_occupation_and_skills (with API fallback)
    2. Focuses only on skills with a proficiency level > 0 (LV scale)
    3. Identifies skills present in the target occupation but not in the source occupation
    4. Returns a list of skill names for these "gap" skills
    
    Args:
        from_onet_soc_code (str): The O*NET-SOC code for the source occupation
        to_onet_soc_code (str): The O*NET-SOC code for the target occupation
        engine (Optional[Engine]): SQLAlchemy engine to use for database operations,
                                  or None to use the default engine
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "result": {
                "from_occupation_title": str,
                "to_occupation_title": str,
                "skill_gaps": list[str]  # List of skill names (not present in source occupation or level=0)
            }
        }
    """
    try:
        # If no engine is provided, get the default one
        if engine is None:
            engine = get_sqlalchemy_engine()
            
        # Retrieve skills data for both occupations (with API fallback)
        from_occupation_response = get_occupation_and_skills(from_onet_soc_code, engine=engine)
        to_occupation_response = get_occupation_and_skills(to_onet_soc_code, engine=engine)
        
        # Check if both queries were successful
        if not from_occupation_response["success"]:
            return {
                "success": False,
                "message": f"Error retrieving source occupation data: {from_occupation_response['message']}",
                "result": {
                    "from_occupation_title": "Unknown",
                    "to_occupation_title": "Unknown",
                    "skill_gaps": []
                }
            }
            
        if not to_occupation_response["success"]:
            return {
                "success": False,
                "message": f"Error retrieving target occupation data: {to_occupation_response['message']}",
                "result": {
                    "from_occupation_title": from_occupation_response["result"]["occupation_data"]["name"],
                    "to_occupation_title": "Unknown",
                    "skill_gaps": []
                }
            }
        
        # Extract occupation titles and skill data
        from_occupation_title = from_occupation_response["result"]["occupation_data"]["name"]
        to_occupation_title = to_occupation_response["result"]["occupation_data"]["name"]
        
        from_skills = from_occupation_response["result"]["occupation_data"]["skills"]
        to_skills = to_occupation_response["result"]["occupation_data"]["skills"]
        
        # Filter out skills with proficiency level 0 from both sets
        from_skills_filtered = [skill for skill in from_skills if float(skill.get("proficiency_level", 0)) > 0]
        to_skills_filtered = [skill for skill in to_skills if float(skill.get("proficiency_level", 0)) > 0]
        
        # Create a set of skill element_ids from the source occupation with proficiency > 0
        from_skill_ids = {skill["skill_element_id"] for skill in from_skills_filtered}
        
        # Identify skills in target occupation that are not in source occupation (or have level=0 in source)
        skill_gaps = []
        for skill in to_skills_filtered:
            if skill["skill_element_id"] not in from_skill_ids:
                skill_gaps.append(skill["skill_name"])
        
        return {
            "success": True,
            "message": f"Successfully identified skill gaps from '{from_occupation_title}' to '{to_occupation_title}' (excluding skills with proficiency level 0).",
            "result": {
                "from_occupation_title": from_occupation_title,
                "to_occupation_title": to_occupation_title,
                "skill_gaps": skill_gaps
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error identifying skill gap: {str(e)}",
            "result": {
                "from_occupation_title": "Error",
                "to_occupation_title": "Error",
                "skill_gaps": []
            }
        }

if __name__ == "__main__":
    print("Minimalistic happy path example for get_skills_gap:")
    print("This example assumes either a populated database with O*NET data or valid O*NET API credentials.")
    
    # Using the occupation codes identified by the user with different skill sets (after filtering level=0)
    from_occupation = "11-1011.00"  # Chief Executives (32 skills with level > 0)
    to_occupation = "11-2021.00"    # Marketing Managers (29 skills with level > 0)
    
    # Get default engine for testing
    default_engine = get_sqlalchemy_engine()
    
    # Call the function with the default engine
    print(f"\n--- Identifying skills in {to_occupation} not present in {from_occupation} ---")
    result = get_skills_gap(from_occupation, to_occupation, engine=default_engine)
    
    # Print the result
    print(f"\nFunction Call Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    if result['success']:
        print(f"\n  From: {result['result']['from_occupation_title']} ({from_occupation})")
        print(f"  To: {result['result']['to_occupation_title']} ({to_occupation})")
        print(f"  Number of skill gaps identified: {len(result['result']['skill_gaps'])}")
        
        if result['result']['skill_gaps']:
            print("\n  Skills present in target occupation but not in source:")
            for skill_name in result['result']['skill_gaps']:
                print(f"    - {skill_name}")
    
    print("\nExample finished.") 