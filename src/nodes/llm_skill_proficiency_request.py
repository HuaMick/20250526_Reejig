"""
This node accepts a from_onet_soc_code and a to_onet_soc_code.
It will get the skills of each occupation from the database.
It then generates a prompt for the llm to assess skill gaps.
It will then store the LLM response in the database.

This file also contains a function to assess skills for a single occupation.
"""

import logging
from typing import Dict, Any, List

from src.functions.gemini_llm_request import gemini_llm_request
from functions.generate_skill_gap_analysis_prompt import gemini_llm_prompt
from src.functions.get_occupation_and_skills import get_occupation_and_skills
from src.functions.mysql_load_llm_skill_proficiencies import mysql_load_llm_skill_proficiencies
from src.config.schemas import get_sqlalchemy_engine # For real DB access

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


def assess_skills_for_occupation(occupation_code: str) -> Dict[str, Any]:
    """
    Processes a single occupation code to:
    1. Fetch its details and associated skills from the database.
    2. Generate a prompt for an LLM to assess these skills.
    3. Send the prompt to the Gemini LLM.
    4. Load the LLM's request and reply data into the MySQL database.

    Args:
        occupation_code (str): The O*NET SOC code for the occupation to assess.

    Returns:
        Dict[str, Any]: A dictionary containing the results of each step:
            - success (bool): Overall success of the operation.
            - message (str): A summary message.
            - details (Dict[str, Any]): Detailed results from each step:
                - get_occupation_data_result (Dict | None)
                - generate_prompt_result (Dict | None)
                - llm_request_result (Dict | None)
                - db_load_result (Dict | None)
                - error (str | None): Error message if any step failed.
    """
    overall_success = False
    summary_message = ""
    step_details = {
        "get_occupation_data_result": None,
        "generate_prompt_result": None,
        "llm_request_result": None,
        "db_load_result": None,
        "error": None
    }

    logging.info(f"Starting skill assessment for occupation_code: {occupation_code}")

    # 1. Get occupation data and skills
    logging.info(f"Step 1: Fetching occupation data for {occupation_code}")
    data_result = get_occupation_and_skills(occupation_code=occupation_code)
    step_details["get_occupation_data_result"] = data_result

    if not data_result["success"]:
        summary_message = f"Failed to get occupation data for {occupation_code}: {data_result['message']}"
        step_details["error"] = summary_message
        logging.error(summary_message)
        return {"success": overall_success, "message": summary_message, "details": step_details}

    occupation_data = data_result["result"].get("occupation_data")
    if not occupation_data or not occupation_data.get("skills"):
        summary_message = f"No occupation data or no skills found for {occupation_code}."
        step_details["error"] = summary_message
        logging.warning(summary_message) # Warning, as we might proceed if occupation exists but has no skills (though LLM req might be odd)
        # Decide if this is a hard fail or if we can proceed (e.g., LLM request for an occupation with no listed skills)
        # For now, if no skills, the prompt and LLM request might not be meaningful.
        if not occupation_data.get("skills"):
            summary_message = f"No skills listed for occupation {occupation_code}. Cannot proceed with LLM assessment."
            step_details["error"] = summary_message
            logging.error(summary_message)
            return {"success": overall_success, "message": summary_message, "details": step_details}

    logging.info(f"Successfully fetched data for {occupation_data.get('name')}")

    # 2. Generate LLM prompt
    logging.info(f"Step 2: Generating LLM prompt for {occupation_data.get('name')}")
    prompt_result = gemini_llm_prompt(occupation_data=occupation_data)
    step_details["generate_prompt_result"] = prompt_result

    if not prompt_result["success"]:
        summary_message = f"Failed to generate LLM prompt: {prompt_result['message']}"
        step_details["error"] = summary_message
        logging.error(summary_message)
        return {"success": overall_success, "message": summary_message, "details": step_details}

    generated_prompt = prompt_result["result"]["prompt"]
    logging.info("Successfully generated LLM prompt.")

    # 3. Prepare prompt_skills_data for gemini_llm_request
    prompt_skills_for_request: List[Dict[str, str]] = []
    if occupation_data.get("skills"):
        for skill_item in occupation_data["skills"]:
            prompt_skills_for_request.append({
                "skill_element_id": skill_item.get("skill_element_id"),
                "skill_name": skill_item.get("skill_name")
            })
    
    if not prompt_skills_for_request:
        summary_message = f"No skills data could be prepared for the LLM request for occupation {occupation_code}."
        step_details["error"] = summary_message
        logging.error(summary_message)
        # This case should ideally be caught earlier if skills list is empty and deemed critical.
        return {"success": overall_success, "message": summary_message, "details": step_details}


    # 4. Call Gemini LLM API
    logging.info(f"Step 3: Requesting LLM assessment for {occupation_data.get('name')}")
    # Using default model, temperature. max_tokens can be adjusted if needed.
    llm_request_result = gemini_llm_request(
        prompt=generated_prompt,
        request_onet_soc_code=occupation_code,
        prompt_skills_data=prompt_skills_for_request,
        max_tokens=4096 # As used in integration test, consider making this configurable
    )
    step_details["llm_request_result"] = llm_request_result

    if not llm_request_result["success"]:
        summary_message = f"LLM request failed: {llm_request_result['message']}"
        step_details["error"] = summary_message
        logging.error(summary_message)
        # Even if LLM fails, request_data might be present in llm_request_result['result']
        # and could potentially be logged. For now, we treat LLM failure as a blocker for DB load of replies.
        # However, the request part could still be logged.
        # The mysql_load_llm_skill_proficiencies function can handle empty reply_data.
        # Let's try to load whatever we have.
        # No, if gemini_llm_request returns success:False, its 'result' might be shaped differently or error-focused.
        # We should only proceed to load if llm_request_result['result'] contains 'request_data' and 'reply_data'.
        # gemini_llm_request aims to always provide request_data if possible.
        # For now, let's stick to: if LLM call `success` is false, we stop and report.
        return {"success": overall_success, "message": summary_message, "details": step_details}

    llm_assessment_output_for_db = llm_request_result.get("result")
    if not llm_assessment_output_for_db or \
       "request_data" not in llm_assessment_output_for_db or \
       "reply_data" not in llm_assessment_output_for_db:
        summary_message = "LLM request result is missing expected 'request_data' or 'reply_data'."
        step_details["error"] = summary_message
        logging.error(summary_message)
        return {"success": overall_success, "message": summary_message, "details": step_details}
        
    logging.info(f"Successfully received LLM assessment. Message: {llm_request_result['message']}")

    # 5. Load data into MySQL database
    logging.info(f"Step 4: Loading LLM assessment data into MySQL database for {occupation_data.get('name')}")
    try:
        engine = get_sqlalchemy_engine()
    except ValueError as e:
        summary_message = f"Failed to create SQLAlchemy engine: {str(e)}"
        step_details["error"] = summary_message
        logging.error(summary_message)
        return {"success": overall_success, "message": summary_message, "details": step_details}

    # Using clear_existing=False for a typical run, so we append data.
    # For testing or specific scenarios, this might be True.
    db_load_result = mysql_load_llm_skill_proficiencies(
        llm_assessment_output=llm_assessment_output_for_db,
        engine=engine,
        clear_requests_table=False, 
        clear_replies_table=False   
    )
    step_details["db_load_result"] = db_load_result

    if not db_load_result["success"]:
        summary_message = f"Failed to load LLM data into database: {db_load_result['message']}"
        step_details["error"] = summary_message
        logging.error(summary_message)
        # overall_success remains False
    else:
        overall_success = True
        summary_message = f"Successfully assessed skills for {occupation_data.get('name')} ({occupation_code}) and loaded to DB."
        logging.info(summary_message)
        logging.info(f"DB Load: Requests loaded: {db_load_result.get('requests_loaded')}, Replies loaded: {db_load_result.get('replies_loaded')}")


    return {"success": overall_success, "message": summary_message, "details": step_details}


def llm_skill_gap_analysis(llm_response: dict, to_occupation: dict, from_occupation: dict = None) -> dict:
    """
    """
    # Placeholder for the existing function's logic if it was defined.
    # If this function is not yet implemented or is from the original template, 
    # this part can be adjusted or removed if assess_skills_for_occupation is the primary entry point.
    logging.warning("llm_skill_gap_analysis is not fully implemented.")
    return {"success": False, "message": "llm_skill_gap_analysis not implemented"}

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python -m src.nodes.llm_skill_proficiency_request <occupation_code>")
        print("Or using the shell script: ./src/scripts/assess_occupation_skills.sh <occupation_code>")
        sys.exit(1)
    
    target_occupation_code = sys.argv[1]
    
    print(f"--- Running LLM Skill Proficiency Assessment for Occupation: {target_occupation_code} ---")
    result = assess_skills_for_occupation(occupation_code=target_occupation_code)
    
    print("\n--- Node Execution Summary ---")
    print(f"Overall Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    print("\n--- Detailed Steps Output (JSON) ---")
    # Pretty print the details part of the result
    if result.get("details"):
        print(json.dumps(result["details"], indent=2, default=str))
    else:
        print("No detailed step information available.")

    if not result.get('success'):
        print("\nNode execution failed.")
        sys.exit(1)
    else:
        print("\nNode execution completed successfully.")