import os
# import sys # Removed sys.path modification

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
                "success": True, # Technically successful, no gap identified as target has no skills listed
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
    print("Running identify_skill_gap minimalistic example...")

    # Example 1: Clear gap
    occ1_data_ex1 = {
        "occupation_title": "Junior Developer",
        "skills": [
            {"element_id": "S1", "element_name": "Programming", "scale_id": "LV", "data_value": 3},
            {"element_id": "S2", "element_name": "Communication", "scale_id": "LV", "data_value": 4}
        ]
    }
    occ2_data_ex1 = {
        "occupation_title": "Senior Developer",
        "skills": [
            {"element_id": "S1", "element_name": "Programming", "scale_id": "LV", "data_value": 5}, # Higher proficiency
            {"element_id": "S2", "element_name": "Communication", "scale_id": "LV", "data_value": 4}, # Same proficiency
            {"element_id": "S3", "element_name": "Architecture", "scale_id": "LV", "data_value": 4}  # New skill
        ]
    }
    print("\n--- Example 1: Junior to Senior Developer ---")
    gap_result_ex1 = identify_skill_gap(occ1_data_ex1, occ2_data_ex1)
    print(f"Success: {gap_result_ex1['success']}")
    print(f"Message: {gap_result_ex1['message']}")
    if gap_result_ex1['success']:
        print("Skill Gaps:")
        for gap in gap_result_ex1['result']['skill_gaps']:
            print(f"  - {gap}")

    # Example 2: No gap (target has lower or equal skills)
    occ1_data_ex2 = {
        "occupation_title": "Expert Coder",
        "skills": [
            {"element_id": "S1", "element_name": "Coding Fast", "scale_id": "LV", "data_value": 7}
        ]
    }
    occ2_data_ex2 = {
        "occupation_title": "Regular Coder",
        "skills": [
            {"element_id": "S1", "element_name": "Coding Fast", "scale_id": "LV", "data_value": 5}
        ]
    }
    print("\n--- Example 2: Expert to Regular Coder (expect no gap towards regular) ---")
    gap_result_ex2 = identify_skill_gap(occ1_data_ex2, occ2_data_ex2)
    print(f"Success: {gap_result_ex2['success']}")
    print(f"Message: {gap_result_ex2['message']}")
    if gap_result_ex2['success']:
        print("Skill Gaps:")
        for gap in gap_result_ex2['result']['skill_gaps']:
            print(f"  - {gap}")
        if not gap_result_ex2['result']['skill_gaps']:
            print("  (No gaps found as expected)")

    # Example 3: Target occupation has no LV skills
    occ1_data_ex3 = occ1_data_ex1 # Use Junior Developer data
    occ2_data_ex3 = {"occupation_title": "Role With No LV Skills", "skills": []}
    print("\n--- Example 3: To Role With No LV Skills ---")
    gap_result_ex3 = identify_skill_gap(occ1_data_ex3, occ2_data_ex3)
    print(f"Success: {gap_result_ex3['success']}") # Should be True
    print(f"Message: {gap_result_ex3['message']}") # Message indicates no target skills
    if gap_result_ex3['success']:
        print("Skill Gaps:")
        for gap in gap_result_ex3['result']['skill_gaps']:
            print(f"  - {gap}")
        if not gap_result_ex3['result']['skill_gaps']:
            print("  (No gaps found as expected)")

    # Example 4: Source occupation has no LV skills
    occ1_data_ex4 = {"occupation_title": "Newbie (No LV Skills)", "skills": []}
    occ2_data_ex4 = occ2_data_ex1 # Use Senior Developer data
    print("\n--- Example 4: From Newbie (No LV Skills) to Senior Developer ---")
    gap_result_ex4 = identify_skill_gap(occ1_data_ex4, occ2_data_ex4)
    print(f"Success: {gap_result_ex4['success']}") # Should be True
    print(f"Message: {gap_result_ex4['message']}")
    if gap_result_ex4['success']:
        print("Skill Gaps (all of Senior Developer's skills should be gaps):")
        for gap in gap_result_ex4['result']['skill_gaps']:
            print(f"  - {gap}")

    # Example 5: Invalid input type for skills
    occ1_data_ex5 = {"occupation_title": "Valid Input", "skills": [{"element_id": "S1", "element_name": "Test", "scale_id": "LV", "data_value": 1}]}
    occ2_data_ex5 = {"occupation_title": "Invalid Input", "skills": "not a list"}
    print("\n--- Example 5: Invalid skills input type ---")
    gap_result_ex5 = identify_skill_gap(occ1_data_ex5, occ2_data_ex5)
    print(f"Success: {gap_result_ex5['success']}") # Should be False
    print(f"Message: {gap_result_ex5['message']}") 