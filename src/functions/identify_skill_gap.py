import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# No direct DB imports needed here anymore (Occupation, Skill, OccupationSkill, get_sqlalchemy_engine)
# We will import the new get_occupation_skills function for the __main__ example
from src.functions.get_occupation_skills import get_occupation_skills

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
                                 Each skill_dict: {"element_id": str, "element_name": str, "scale_id": "LV", "data_value": Decimal}
        occupation2_data (dict): The result dictionary from get_occupation_skills for the 'to' occupation.
                                 (Same structure as occupation1_data)

    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str),
              and 'result' (dict containing 'skill_gaps' as a list of dicts
              e.g., {"element_id": "...", "element_name": "...", "scale_id": "LV", "from_data_value": Decimal, "to_data_value": Decimal}).
              'from_data_value' will be 0 if the skill is not in occupation1_data's skills list (with scale 'LV').
    """
    try:
        occ1_title = occupation1_data.get("occupation_title", "Occupation 1")
        occ2_title = occupation2_data.get("occupation_title", "Occupation 2")
        
        occ1_skills_list = occupation1_data.get("skills", [])
        occ2_skills_list = occupation2_data.get("skills", [])

        # Check if either occupation has no 'LV' skills provided
        if not occ1_skills_list:
            return {
                "success": False,
                "message": f"No 'LV' scale skills data provided for the 'from' occupation: {occ1_title}. Cannot calculate skill gap.",
                "result": {"skill_gaps": [], "from_occupation_title": occ1_title, "to_occupation_title": occ2_title}
            }
        if not occ2_skills_list:
            return {
                "success": False,
                "message": f"No 'LV' scale skills data provided for the 'to' occupation: {occ2_title}. Cannot calculate skill gap.",
                "result": {"skill_gaps": [], "from_occupation_title": occ1_title, "to_occupation_title": occ2_title}
            }

        occ1_skills_map = {skill['element_id']: skill for skill in occ1_skills_list}
        occ2_skills_map = {skill['element_id']: skill for skill in occ2_skills_list}

        gap_skill_details_lv = []
        all_relevant_skill_ids = set(occ1_skills_map.keys()) | set(occ2_skills_map.keys())

        for skill_id in all_relevant_skill_ids:
            skill_info1 = occ1_skills_map.get(skill_id)
            skill_info2 = occ2_skills_map.get(skill_id)

            occ1_data_value = skill_info1['data_value'] if skill_info1 and skill_info1['data_value'] is not None else 0
            occ2_data_value = skill_info2['data_value'] if skill_info2 and skill_info2['data_value'] is not None else 0
            
            # A gap exists if occ2 requires the skill (present in occ2_skills) and either:
            # 1. occ1 does not have it (skill_info1 is None, so occ1_data_value is 0)
            # 2. occ1 has it but its value is lower than occ2's value
            if skill_info2: # Skill must be relevant to occ2
                if not skill_info1 or (occ2_data_value > occ1_data_value):
                    gap_skill_details_lv.append({
                        "element_id": skill_id,
                        # Get element_name from occ2_skills as it's guaranteed to be there if skill_info2 exists
                        "element_name": skill_info2.get('element_name', "Unknown Skill"), 
                        "from_data_value": occ1_data_value, # This is the 'LV' data value from occ1 or 0
                        "to_data_value": occ2_data_value    # This is the 'LV' data value from occ2
                    })
        
        skill_gaps_result = []
        for gap_detail in gap_skill_details_lv:
            skill_gaps_result.append({
                "element_id": gap_detail["element_id"],
                "element_name": gap_detail["element_name"],
                "scale_id": "LV", # Explicitly state that this gap is for 'LV' scale
                "from_data_value": gap_detail["from_data_value"],
                "to_data_value": gap_detail["to_data_value"]
            })

        return {
            "success": True,
            "message": f"Successfully identified skill gap from '{occ1_title}' to '{occ2_title}' based on 'LV' scale.",
            "result": {"skill_gaps": skill_gaps_result, "from_occupation_title": occ1_title, "to_occupation_title": occ2_title}
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in identify_skill_gap: {e}\n{error_details}")
        # Try to get titles for a more informative error if possible
        occ1_title_err = occupation1_data.get("occupation_title", "Unknown Occupation 1")
        occ2_title_err = occupation2_data.get("occupation_title", "Unknown Occupation 2")
        return {"success": False, "message": f"Error identifying skill gap from '{occ1_title_err}' to '{occ2_title_err}': {e}", "result": {"skill_gaps": [], "from_occupation_title": occ1_title_err, "to_occupation_title": occ2_title_err}}

if __name__ == '__main__':
    print("Running identify_skill_gap example using get_occupation_skills...")

    # Example O*NET codes
    example_occ_code1 = "15-1252.00" # Software Developers
    example_occ_code2 = "19-2031.00" # Chemists (Example: Software Developer to Chemist)
    
    print(f"\n--- Getting skills for Occupation 1: {example_occ_code1} ---")
    occ1_skill_data_response = get_occupation_skills(example_occ_code1)
    if occ1_skill_data_response["success"]:
        print(f"Successfully got skills for {occ1_skill_data_response['result']['occupation_title']}")
        if not occ1_skill_data_response["result"]["skills"]:
            print(f"Note: No 'LV' skills returned for {example_occ_code1}")
    else:
        print(f"Failed to get skills for {example_occ_code1}: {occ1_skill_data_response['message']}")
        exit()

    print(f"\n--- Getting skills for Occupation 2: {example_occ_code2} ---")
    occ2_skill_data_response = get_occupation_skills(example_occ_code2)
    if occ2_skill_data_response["success"]:
        print(f"Successfully got skills for {occ2_skill_data_response['result']['occupation_title']}")
        if not occ2_skill_data_response["result"]["skills"]:
            print(f"Note: No 'LV' skills returned for {example_occ_code2}")
    else:
        print(f"Failed to get skills for {example_occ_code2}: {occ2_skill_data_response['message']}")
        exit()

    # Proceed to identify_skill_gap only if get_occupation_skills was successful for both
    # (even if skills list is empty, get_occupation_skills returns success:True if occupation is found)
    if occ1_skill_data_response["success"] and occ2_skill_data_response["success"]:
        print("\n--- Identifying skill gap --- ")
        gap_result = identify_skill_gap(occ1_skill_data_response["result"], occ2_skill_data_response["result"])

        if gap_result["success"]:
            print(f"Message: {gap_result['message']}")
            from_title = gap_result['result'].get('from_occupation_title')
            to_title = gap_result['result'].get('to_occupation_title')
            print(f"Skill gap from '{from_title}' to '{to_title}' (Scale: LV):")
            
            if gap_result["result"]["skill_gaps"]:
                for skill in gap_result["result"]["skill_gaps"]:
                    print(f"  - Skill ID: {skill['element_id']}, Name: {skill['element_name']}")
                    print(f"    Scale: {skill.get('scale_id', 'N/A')}, From Value: {skill.get('from_data_value', 'N/A')}, To Value: {skill.get('to_data_value', 'N/A')}")
            else:
                print("  No 'LV' scale skill gaps found (or one/both occupations had no LV skills to compare).")
        else:
            print(f"Identify Skill Gap Failed: {gap_result['message']}")
    else:
        print("\nSkipped identifying skill gap due to failure in retrieving skills for one or both occupations.")

    print("\n--- Example simulating one occupation with no LV skills (direct input to identify_skill_gap) ---")
    simulated_occ_with_skills_data = {"occupation_title": "Hypothetical Role With Skills", "skills": [{"element_id": "1.A.1", "element_name": "Test Skill", "scale_id": "LV", "data_value": 5.0}]}
    simulated_occ_no_lv_data = {"occupation_title": "Hypothetical Non-LV Role", "skills": []}
    
    print(f"Identifying gap from '{simulated_occ_with_skills_data['occupation_title']}' to '{simulated_occ_no_lv_data['occupation_title']}'...")
    gap_result_sim_to_empty = identify_skill_gap(simulated_occ_with_skills_data, simulated_occ_no_lv_data)
    print(f"Simulated Gap (to empty) - Success: {gap_result_sim_to_empty['success']}, Message: {gap_result_sim_to_empty['message']}")

    print(f"\nIdentifying gap from '{simulated_occ_no_lv_data['occupation_title']}' to '{simulated_occ_with_skills_data['occupation_title']}'...")
    gap_result_sim_from_empty = identify_skill_gap(simulated_occ_no_lv_data, simulated_occ_with_skills_data)
    print(f"Simulated Gap (from empty) - Success: {gap_result_sim_from_empty['success']}, Message: {gap_result_sim_from_empty['message']}") 