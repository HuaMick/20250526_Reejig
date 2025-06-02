"""
Function to retrieve and structure occupation and skills data for LLM prompt generation.
"""
import os
import logging
import re  # Added for occupation code validation
from typing import Dict, Any, Optional, List
from sqlalchemy.engine import Engine

from src.functions.get_occupation import get_occupation
from src.functions.get_occupation_skills import get_occupation_skills
from src.functions.onet_api_extract_occupation import onet_api_extract_occupation
from src.functions.onet_api_extract_skills import onet_api_extract_skills
from src.functions.mysql_load_table import load_data_from_dataframe
from src.config.schemas import get_sqlalchemy_engine, Onet_Occupations_API_landing, Onet_Skills_API_landing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

def get_occupation_and_skills(
    occupation_code: str,
    engine: Optional[Engine] = None
) -> Dict[str, Any]:
    """
    Retrieves and structures occupation and skills data for a single occupation.
    If data is not found locally, it attempts to fetch from O*NET API and load it.

    This data is formatted to be directly usable by `gemini_llm_prompt`.

    Args:
        occupation_code (str): The O*NET SOC code for the occupation.
        engine (Optional[Engine]): SQLAlchemy engine to use for database operations,
                                  or None to use the default engine

    Returns:
        Dict[str, Any]: Standard response format with keys:
            - success (bool): Whether all data retrieval and structuring was successful.
            - message (str): Status message or error description.
            - result (dict): When successful, contains:
                - occupation_data (dict): Structured data for the occupation.
    """
    # Validate occupation code format
    if not occupation_code or not re.match(r'^\d{2}-\d{4}\.\d{2}$', occupation_code):
        return {
            "success": False,
            "message": f"Invalid occupation code format: {occupation_code}. Expected format: xx-xxxx.xx (e.g., 11-1011.00)",
            "result": {}
        }
    
    # If no engine is provided, get the default one
    if engine is None:
        engine = get_sqlalchemy_engine()
        
    occupation_details_result: Optional[Dict[str, Any]] = None
    skills_details_result: Optional[Dict[str, Any]] = None
    
    # Attempt to get occupation details from local DB
    logging.info(f"Attempting to fetch occupation details for {occupation_code} from local DB.")
    occupation_details_local = get_occupation(occupation_code, engine=engine)
    
    api_sourced_occupation = False
    api_sourced_skills = False

    if not occupation_details_local["success"]:
        logging.warning(f"Occupation {occupation_code} not found in local DB. Attempting API pull.")
        onet_username = os.getenv("ONET_USERNAME")
        onet_password = os.getenv("ONET_PASSWORD")

        if not onet_username or not onet_password:
            return {"success": False, "message": "O*NET API credentials (ONET_USERNAME, ONET_PASSWORD) not found in environment.", "result": {}}

        api_occ_result = onet_api_extract_occupation(
            username=onet_username, 
            password=onet_password, 
            filter_params=[f"onetsoc_code.eq.{occupation_code}"]
        )

        if api_occ_result["success"] and api_occ_result["result"]["occupation_df"] is not None and not api_occ_result["result"]["occupation_df"].empty:
            occupation_df = api_occ_result["result"]["occupation_df"]
            # Ensure we only take the first row if multiple are returned (should not happen with specific code filter)
            if len(occupation_df) > 1:
                logging.warning(f"API returned multiple occupations for code {occupation_code}, using the first one.")
                occupation_df = occupation_df.head(1)
            
            try:
                load_api_occ = load_data_from_dataframe(
                    df=occupation_df, 
                    model=Onet_Occupations_API_landing, 
                    engine=engine, 
                    clear_existing=False # Append, as primary key should prevent duplicates if called again
                )
                if load_api_occ["success"]:
                    logging.info(f"Successfully loaded occupation {occupation_code} from API to Onet_Occupations_API_landing.")
                else:
                    logging.warning(f"Failed to load occupation {occupation_code} from API to DB: {load_api_occ['message']}")
            except Exception as e:
                logging.error(f"Error getting engine or loading API occupation data for {occupation_code}: {str(e)}")

            # Construct occupation_details_result similar to get_occupation's output
            # The onet_api_extract_occupation already renames columns via OnetMappings.API_OCCUPATIONS_COLUMN_RENAME_MAP
            # to onet_soc_code, title, description.
            api_occ_row = occupation_df.iloc[0]
            occupation_details_result = {
                "success": True,
                "message": f"Successfully retrieved occupation data for {api_occ_row.get('title')} from API.",
                "result": {
                    "onet_soc_code": api_occ_row.get("onet_soc_code"),
                    "title": api_occ_row.get("title"),
                    "description": api_occ_row.get("description")
                }
            }
            api_sourced_occupation = True
        else:
            msg = f"Failed to get details for occupation {occupation_code} from local DB and API: {api_occ_result.get('message', 'API data was empty or failed.')}"
            logging.error(msg)
            return {"success": False, "message": msg, "result": {}}
    else:
        occupation_details_result = occupation_details_local

    # Attempt to get skills details from local DB
    logging.info(f"Attempting to fetch skills for {occupation_code} from local DB.")
    skills_details_local = get_occupation_skills(occupation_code, engine=engine)

    # Check if skills list is empty, even if get_occupation_skills call was successful (e.g. occupation exists but no skills linked)
    if not skills_details_local["success"] or (skills_details_local["success"] and not skills_details_local.get("result", {}).get("skills")):
        log_msg = f"Skills for occupation {occupation_code} not found or empty in local DB (get_occupation_skills success: {skills_details_local['success']}). Attempting API pull for skills."
        logging.warning(log_msg)
        onet_username = os.getenv("ONET_USERNAME")
        onet_password = os.getenv("ONET_PASSWORD")

        if not onet_username or not onet_password:
            # If occupation was from API, we might still proceed with it, but skills will be missing.
            # If occupation was local, this means API creds are now an issue for skills part.
            # For simplicity, if creds are missing here, we can't fetch skills.
             return {"success": False, "message": "O*NET API credentials not found for skills fetch.", "result": {}}

        api_skills_result = onet_api_extract_skills(
            username=onet_username, 
            password=onet_password, 
            filter_params=[f"onetsoc_code.eq.{occupation_code}"]
        )

        if api_skills_result["success"] and api_skills_result["result"]["skills_df"] is not None and not api_skills_result["result"]["skills_df"].empty:
            skills_df = api_skills_result["result"]["skills_df"]
            try:
                load_api_skills = load_data_from_dataframe(
                    df=skills_df, 
                    model=Onet_Skills_API_landing, 
                    engine=engine, 
                    clear_existing=False # Append, Onet_Skills_API_landing has auto PK
                )
                if load_api_skills["success"]:
                    logging.info(f"Successfully loaded skills for {occupation_code} from API to Onet_Skills_API_landing.")
                else:
                    logging.warning(f"Failed to load skills for {occupation_code} from API to DB: {load_api_skills['message']}")
            except Exception as e:
                logging.error(f"Error getting engine or loading API skills data for {occupation_code}: {str(e)}")

            # Construct skills_details_result from the API skills_df
            # onet_api_extract_skills directly parses element_id, element_name, data_value (for LV scale)
            api_skills_list: List[Dict[str, Any]] = []
            for _, row in skills_df.iterrows():
                # We are interested in LV scale for proficiency_level for this function's output context
                if row.get('scale_id') == 'LV': 
                    api_skills_list.append({
                        "element_id": row.get("element_id"),
                        "element_name": row.get("element_name"),
                        "proficiency_level": row.get("data_value")
                    })
            
            current_occupation_title = occupation_details_result["result"].get("title") if occupation_details_result and occupation_details_result.get("result") else "Unknown"
            skills_details_result = {
                "success": True,
                "message": f"Successfully retrieved skills for {current_occupation_title} from API.",
                "result": {
                    "occupation_title": current_occupation_title,
                    "skills": api_skills_list
                }
            }
            api_sourced_skills = True
        else:
            # If API call for skills fails or returns empty, use the (potentially empty) local skills result.
            # If occupation was found locally, this means no skills from API either.
            logging.warning(f"Failed to get skills for {occupation_code} from API or API returned no skills. Using local skills result (if any). API Message: {api_skills_result.get('message')}")
            skills_details_result = skills_details_local # Fallback to local result (which might indicate no skills)
    else:
        skills_details_result = skills_details_local

    # Final structuring based on gathered occupation_details_result and skills_details_result
    if not occupation_details_result or not occupation_details_result["success"]:
        # This case should have been handled by the initial occupation check and API fallback
        return {"success": False, "message": occupation_details_result.get("message", "Unknown error fetching occupation details."), "result": {}}

    structured_skills: List[Dict[str, Any]] = []
    if skills_details_result and skills_details_result.get("success") and skills_details_result.get("result", {}).get("skills"):
        # Determine if skills came from API or local get_occupation_skills structure
        source_skills_list = skills_details_result["result"]["skills"]
        for skill in source_skills_list:
            # The structure for API sourced skills is already: {"element_id", "skill_name", "proficiency_level"}
            # The structure from local get_occupation_skills is: {"element_id", "element_name", "data_value" (as proficiency)}
            structured_skills.append({
                "skill_element_id": skill.get("element_id"),
                "skill_name": skill.get("element_name") if api_sourced_skills else skill.get("element_name"), # skill_name vs element_name
                "proficiency_level": skill.get("proficiency_level") if api_sourced_skills else skill.get("data_value")
            })
    elif skills_details_result and not skills_details_result.get("success"):
        # If getting skills failed (even after API attempt for skills), log it but proceed with occupation data only if it exists
        logging.warning(f"Could not retrieve skills for {occupation_code}. Proceeding without skills data. Message: {skills_details_result.get('message')}")
    
    # else: skills_details_result was successful but skills list was empty, structured_skills remains [] which is correct.

    final_message = f"Successfully processed {occupation_code}. Occupation data sourced from API: {api_sourced_occupation}. Skills data sourced from API: {api_sourced_skills}."
    if not structured_skills:
        final_message += " No skills data available or found for this occupation."
        
    return {
        "success": True, # Overall success is true if we have occupation data, even if skills are missing
        "message": final_message,
        "result": {
            "occupation_data": {
                "onet_id": occupation_details_result["result"].get("onet_soc_code"),
                "name": occupation_details_result["result"].get("title"),
                "skills": structured_skills
            }
        }
    }

if __name__ == "__main__":
    # Minimalistic happy path example for get_occupation_and_skills.
    # This example demonstrates calling the function for an occupation code.
    # It assumes that O*NET API credentials (ONET_USERNAME, ONET_PASSWORD) are set
    # in the environment, as the function might need to call the API if data
    # is not found locally.

    # Replace with a relevant occupation code for testing.
    # "11-2021.00" (Marketing Managers) is used here as an example that might trigger API fallback.
    test_occupation_code = "11-2021.00"
    
    print(f"Attempting to get occupation and skills data for: {test_occupation_code}")
    result = get_occupation_and_skills(occupation_code=test_occupation_code)

    print(f"\nFunction Call Result for {test_occupation_code}:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")

    if result['success'] and result.get('result') and result['result'].get('occupation_data'):
        occupation_data = result['result']['occupation_data']
        print(f"  Occupation Name: {occupation_data.get('name')}")
        print(f"  O*NET ID: {occupation_data.get('onet_id')}")
        print(f"  Number of skills retrieved: {len(occupation_data.get('skills', []))}")
        if occupation_data.get('skills'):
            print(f"  First skill example: {occupation_data['skills'][0]}")
    else:
        print("  No occupation data was retrieved or an error occurred.")

    print("\nExample finished.") 