"""
Function to retrieve and structure occupation and skills data for LLM prompt generation.
"""
from typing import Dict, Any, Optional, List

from src.functions.get_occupation import get_occupation
from src.functions.get_occupation_skills import get_occupation_skills

def get_occupation_and_skills(
    occupation_code: str,
) -> Dict[str, Any]:
    """
    Retrieves and structures occupation and skills data for a single occupation.

    This data is formatted to be directly usable by `gemini_llm_prompt`.

    Args:
        occupation_code (str): The O*NET SOC code for the occupation.

    Returns:
        Dict[str, Any]: Standard response format with keys:
            - success (bool): Whether all data retrieval and structuring was successful.
            - message (str): Status message or error description.
            - result (dict): When successful, contains:
                - occupation_data (dict): Structured data for the occupation.
    """

    def _fetch_and_structure_single_occupation(code: str) -> Dict[str, Any]: # Renamed internal var for clarity
        """Helper function to fetch and structure data for a single occupation."""
        occupation_details = get_occupation(code)
        if not occupation_details["success"]:
            return {"success": False, "message": f"Failed to get details for occupation {code}: {occupation_details['message']}"}

        skills_details = get_occupation_skills(code)
        if not skills_details["success"]:
            if "not found" in skills_details["message"].lower():
                 return {"success": False, "message": f"Failed to get skills for occupation {code}: {skills_details['message']}"}
            # Occupation found but no skills, treat as success with empty skills list

        structured_skills: List[Dict[str, Any]] = []
        # Ensure skills_details["result"] and skills_details["result"]["skills"] exist and are not None
        if skills_details.get("result") and skills_details["result"].get("skills"):
            for skill in skills_details["result"]["skills"]:
                structured_skills.append({
                    "skill_element_id": skill.get("element_id"),
                    "skill_name": skill.get("element_name"),
                    "proficiency_level": skill.get("data_value") 
                })
        
        return {
            "success": True,
            "message": f"Successfully fetched and structured data for {code}",
            "data": {
                "onet_id": occupation_details["result"].get("onet_soc_code"),
                "name": occupation_details["result"].get("title"),
                "skills": structured_skills
            }
        }

    # Directly fetch and structure the single occupation
    data_result = _fetch_and_structure_single_occupation(occupation_code)
    
    if not data_result["success"]:
        return {"success": False, "message": data_result["message"], "result": {}}

    return {
        "success": True,
        "message": "Successfully retrieved and structured occupation data.",
        "result": {
            "occupation_data": data_result["data"],
        }
    }

if __name__ == "__main__":
    print("Minimalistic happy path example for get_occupation_and_skills:")
    print("This example assumes a populated database and configured environment variables.")

    example_code = "11-1011.00"  # Chief Executives (assuming this has skills in your DB for a good demo)
    print(f"\n--- Example: Fetching data for occupation ({example_code}) ---")
    result = get_occupation_and_skills(occupation_code=example_code)
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print("Occupation Data:")
        retrieved_data = result['result']['occupation_data']
        print(f"  ONET ID: {retrieved_data.get('onet_id')}")
        print(f"  Name: {retrieved_data.get('name')}")
        skills = retrieved_data.get('skills', [])
        print(f"  Skills found: {len(skills)}")
        if skills:
            print(f"  Sample skill: {skills[0]}")

    # Example: Invalid occupation_code
    invalid_code_example = "INVALID-CODE"
    print(f"\n--- Example: Invalid occupation code ({invalid_code_example}) ---")
    result_invalid = get_occupation_and_skills(occupation_code=invalid_code_example)
    print(f"Success: {result_invalid['success']}")
    print(f"Message: {result_invalid['message']}")
    assert not result_invalid['success'], "Call with invalid code should fail"

    print("\nExample finished.") 