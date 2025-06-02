import os
from typing import Optional, Dict, Any
from sqlalchemy.engine import Engine
from src.config.schemas import get_sqlalchemy_engine
from src.functions.get_occupation_and_skills import get_occupation_and_skills

def get_skills_gap_by_lvl(from_onet_soc_code: str, to_onet_soc_code: str, engine: Optional[Engine] = None):
    """
    Identifies skills required by the target occupation that the source occupation either does not have 
    or where the proficiency level is lower than in the target occupation.
    
    This function:
    1. Retrieves detailed skills data for both occupations using get_occupation_and_skills (with API fallback)
    2. Transforms the data to match the structure expected by identify_skill_gap
    3. Uses identify_skill_gap to analyze the skill gap between the occupations
    4. Returns a comprehensive assessment of skill gaps with proficiency level details
    
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
                "skill_gaps": [
                    {
                        "element_id": str,
                        "element_name": str,
                        "scale_id": "LV",
                        "from_data_value": float/int,
                        "to_data_value": float/int
                    },
                    ...
                ]
            }
        }
    """
    try:
        # If no engine is provided, get the default one
        if engine is None:
            engine = get_sqlalchemy_engine()
            
        # Retrieve detailed data for both occupations (with API fallback)
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
        
        # Extract occupation titles
        from_occupation_title = from_occupation_response["result"]["occupation_data"]["name"]
        to_occupation_title = to_occupation_response["result"]["occupation_data"]["name"]
        
        # Transform data to match the structure expected by identify_skill_gap
        from_occupation_data = {
            "occupation_title": from_occupation_title,
            "skills": []
        }
        
        to_occupation_data = {
            "occupation_title": to_occupation_title,
            "skills": []
        }
        
        # Transform skills data for source occupation
        for skill in from_occupation_response["result"]["occupation_data"]["skills"]:
            from_occupation_data["skills"].append({
                "element_id": skill["skill_element_id"],
                "element_name": skill["skill_name"],
                "scale_id": "LV",
                "data_value": float(skill["proficiency_level"]) if skill["proficiency_level"] is not None else 0
            })
        
        # Transform skills data for target occupation
        for skill in to_occupation_response["result"]["occupation_data"]["skills"]:
            to_occupation_data["skills"].append({
                "element_id": skill["skill_element_id"],
                "element_name": skill["skill_name"],
                "scale_id": "LV",
                "data_value": float(skill["proficiency_level"]) if skill["proficiency_level"] is not None else 0
            })
        
        # Filter out skills with proficiency level 0 from both sets
        from_occupation_data["skills"] = [skill for skill in from_occupation_data["skills"] if skill["data_value"] > 0]
        to_occupation_data["skills"] = [skill for skill in to_occupation_data["skills"] if skill["data_value"] > 0]
        
        # Call identify_skill_gap to analyze the skill gap
        skill_gap_result = identify_skill_gap(from_occupation_data, to_occupation_data)
        
        # Return the result
        return skill_gap_result
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error identifying skill gap by level: {str(e)}",
            "result": {
                "from_occupation_title": "Error",
                "to_occupation_title": "Error",
                "skill_gaps": []
            }
        }

# No direct DB imports needed here anymore (Occupation, Skill, OccupationSkill, get_sqlalchemy_engine)
# We will import the new get_occupation_skills function for the __main__ example
# from src.functions.get_occupation_skills import get_occupation_skills # Not needed for the function itself, only for old example

def identify_skill_gap(occupation1_data: dict, occupation2_data: dict):
    """
    Identifies the skill gap between two occupations based on pre-fetched 'LV' scale skill data.
    
    A skill gap includes:
    1. Skills (element_id) with scale_id 'LV' present in occupation2_data but not in occupation1_data.
    2. Skills (element_id) with scale_id 'LV' present in both, but where the proficiency level (data_value)
       for occupation2_data is higher than for occupation1_data.
    Assumes input data_values are for 'LV' scale; if a skill is missing, its data_value is treated as 0.

    Args:
        occupation1_data (dict): The result dictionary from get_occupation_skills for the 'from' occupation.
                                 Expected keys: {"occupation_title": str, "skills": list_of_skill_dicts}
                                 Each skill_dict: {"element_id": str, "element_name": str, "scale_id": "LV", "data_value": Decimal/float/int}
        occupation2_data (dict): The result dictionary from get_occupation_skills for the 'to' occupation.
                                 (Same structure as occupation1_data)

    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str),
              and 'result' (dict containing 'skill_gaps' as a list of dicts,
              'from_occupation_title', and 'to_occupation_title').
              Each skill_gap dict: {"element_id": "...", "element_name": "...", "scale_id": "LV", "from_data_value": Decimal/float/int, "to_data_value": Decimal/float/int}).
              'from_data_value' will be 0 if the skill is not in occupation1_data's skills list (with scale 'LV').
    """
    try:
        occ1_title = occupation1_data.get("occupation_title", "Occupation 1")
        occ2_title = occupation2_data.get("occupation_title", "Occupation 2")
        
        occ1_skills_list = occupation1_data.get("skills", [])
        occ2_skills_list = occupation2_data.get("skills", [])

        # Validate input structure a bit more (optional, but good practice)
        if not isinstance(occ1_skills_list, list) or not isinstance(occ2_skills_list, list):
            return {
                "success": False,
                "message": "Invalid input: 'skills' must be a list.",
                "result": {"skill_gaps": [], "from_occupation_title": occ1_title, "to_occupation_title": occ2_title}
            }

        if not occ2_skills_list: # If target occupation has no skills, there's no gap *towards* it in terms of proficiency needs.
             # This condition also implies that if occ1_skills_list is empty, and occ2_skills_list is also empty, this will be the message.
            return {
                "success": True, # Technically successful, no gap identified as target has no skills
                "message": f"No 'LV' scale skills data provided for the 'to' occupation: {occ2_title}. Cannot identify skill gaps towards it.",
                "result": {"skill_gaps": [], "from_occupation_title": occ1_title, "to_occupation_title": occ2_title}
            }
        
        # If occ1_skills_list is empty but occ2_skills_list is not, all of occ2_skills are gaps.
        # This is handled by the main loop where occ1_data_value defaults to 0.

        occ1_skills_map = {skill['element_id']: skill for skill in occ1_skills_list if isinstance(skill, dict) and 'element_id' in skill}
        occ2_skills_map = {skill['element_id']: skill for skill in occ2_skills_list if isinstance(skill, dict) and 'element_id' in skill}

        skill_gaps_result = []
        # Iterate through skills of the target occupation (occ2)
        for skill_id, skill_info2 in occ2_skills_map.items():
            skill_info1 = occ1_skills_map.get(skill_id)

            occ1_data_value = skill_info1['data_value'] if skill_info1 and skill_info1.get('data_value') is not None else 0
            occ2_data_value = skill_info2.get('data_value') # Should always exist in skill_info2 from occ2_skills_map
            if occ2_data_value is None: # If target skill has no data_value, skip (or treat as 0 if that's desired)
                continue # Or handle as a specific case, for now, skip if target proficiency is unknown
            
            if not skill_info1 or (occ2_data_value > occ1_data_value):
                skill_gaps_result.append({
                    "element_id": skill_id,
                    "element_name": skill_info2.get('element_name', "Unknown Skill"), 
                    "scale_id": "LV",
                    "from_data_value": occ1_data_value,
                    "to_data_value": occ2_data_value
                })

        return {
            "success": True,
            "message": f"Successfully identified skill gap from '{occ1_title}' to '{occ2_title}' based on 'LV' scale.",
            "result": {"skill_gaps": skill_gaps_result, "from_occupation_title": occ1_title, "to_occupation_title": occ2_title}
        }

    except Exception as e:
        # import traceback # Removed
        # error_details = traceback.format_exc() # Removed
        # print(f"Error in identify_skill_gap: {e}\n{error_details}") # Removed
        occ1_title_err = occupation1_data.get("occupation_title", "Input Occupation 1") if isinstance(occupation1_data, dict) else "Input Occupation 1"
        occ2_title_err = occupation2_data.get("occupation_title", "Input Occupation 2") if isinstance(occupation2_data, dict) else "Input Occupation 2"
        return {"success": False, "message": f"Error identifying skill gap from '{occ1_title_err}' to '{occ2_title_err}': {str(e)}", "result": {"skill_gaps": [], "from_occupation_title": occ1_title_err, "to_occupation_title": occ2_title_err}}

if __name__ == '__main__':
    print("Testing get_skills_gap_by_lvl function with real occupation codes:")
    print("This example assumes either a populated database with O*NET data or valid O*NET API credentials.")
    
    # Using the occupation codes identified as having different skills (after filtering level=0)
    from_occupation = "11-1011.00"  # Chief Executives
    to_occupation = "11-2021.00"    # Marketing Managers
    
    # Get default engine for testing
    default_engine = get_sqlalchemy_engine()
    
    # Call the function with default engine
    print(f"\n--- Identifying skill gap with proficiency levels from '{from_occupation}' to '{to_occupation}' ---")
    result = get_skills_gap_by_lvl(from_occupation, to_occupation, engine=default_engine)
    
    # Print the results
    print("\nFunction Call Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    if result['success']:
        print(f"\n  From: {result['result']['from_occupation_title']} ({from_occupation})")
        print(f"  To: {result['result']['to_occupation_title']} ({to_occupation})")
        print(f"  Number of skill gaps identified: {len(result['result']['skill_gaps'])}")
        
        if result['result']['skill_gaps']:
            print("\n  Skill Gaps with Proficiency Levels:")
            for gap in result['result']['skill_gaps']:
                print(f"    - Skill: {gap['element_name']} (ID: {gap['element_id']})")
                print(f"      From Level: {gap['from_data_value']}, To Level: {gap['to_data_value']}")
    
    print("\nExample finished.") 