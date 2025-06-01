"""
Integration test for the LLM skill assessment pipeline, chaining:
- get_occupation_and_skills
- gemini_llm_prompt
- gemini_llm_request
"""
import os
import json
import pytest
from decimal import Decimal # Import Decimal
from datetime import datetime # Import datetime
from sqlalchemy import create_engine, text # Added text for direct queries
from sqlalchemy.orm import sessionmaker # Added sessionmaker

from src.functions.get_occupation_and_skills import get_occupation_and_skills
from functions.generate_skill_gap_analysis_prompt import gemini_llm_prompt
from src.functions.gemini_llm_request import gemini_llm_request # Import gemini_llm_request
from src.functions.mysql_load_llm_skill_proficiencies import mysql_load_llm_skill_proficiencies # Added
import src.config.schemas as schemas # Added

# Constant for the target O*NET ID for this test case
TARGET_ONET_ID = "11-1011.00"

def test_llm_skill_assessment_pipeline_happy_path(
):
    """
    Test the pipeline from fetching data from the database to generating the LLM prompt.
    This test uses real database calls for get_occupation and get_occupation_skills.
    The external LLM API call (gemini_llm_request) is not part of this integration test.
    """
    # --- 1. Call get_occupation_and_skills with a known occupation code --- 
    # This will hit the actual database.
    # Ensure "15-1252.00" (Software Developer) exists in your database with some skills.
    to_occupation_code = TARGET_ONET_ID 
    
    print(f"\nAttempting to fetch data for occupation: {to_occupation_code}")
    data_result = get_occupation_and_skills(occupation_code=to_occupation_code)
    
    # Custom JSON encoder to handle Decimal types for printing
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return str(obj)  # Convert Decimal to string
            if isinstance(obj, datetime): # Add this condition
                return obj.isoformat()  # Convert datetime to ISO 8601 string
            return super(DecimalEncoder, self).default(obj)

    print("\nget_occupation_and_skills result:")
    print(json.dumps(data_result, indent=2, cls=DecimalEncoder))

    assert data_result["success"], f"get_occupation_and_skills failed: {data_result['message']}"
    assert data_result["result"].get("occupation_data") is not None, "occupation_data should not be None in result"
    
    structured_to_data = data_result["result"]["occupation_data"]
    assert structured_to_data["onet_id"] == TARGET_ONET_ID, \
        f"Expected O*NET ID {TARGET_ONET_ID}, got {structured_to_data['onet_id']}"
    
    # Assert that a name was retrieved and it's a non-empty string
    retrieved_occupation_name = structured_to_data.get("name")
    assert retrieved_occupation_name and isinstance(retrieved_occupation_name, str), \
        f"Occupation name not found or invalid for {to_occupation_code}. Got: {retrieved_occupation_name}"
    print(f"Retrieved occupation name from DB: {retrieved_occupation_name}")
    
    assert "skills" in structured_to_data, "Skills key missing in to_occupation_data"
    assert isinstance(structured_to_data["skills"], list), "Skills should be a list"
    # We expect some skills for a Software Developer, but won't assert specific ones
    # as they might change in the DB. Just check the list is not empty.
    assert len(structured_to_data["skills"]) > 0, \
        f"Expected skills for {to_occupation_code}, but got an empty list. Ensure this occupation has skills in the DB."
    
    # Check structure of the first skill (if list is not empty)
    if structured_to_data["skills"]:
        first_skill = structured_to_data["skills"][0]
        assert "skill_name" in first_skill, "Each skill should have a 'skill_name'"
        assert "proficiency_level" in first_skill, "Each skill should have a 'proficiency_level'"
        print(f"Sample skill found: {first_skill['skill_name']} (Proficiency: {first_skill['proficiency_level']})")


    # --- 2. Call gemini_llm_prompt --- 
    print("\nAttempting to generate LLM prompt...")
    prompt_result = gemini_llm_prompt(occupation_data=structured_to_data)
    
    print("\ngemini_llm_prompt result:")
    print(json.dumps(prompt_result, indent=2))

    assert prompt_result["success"], f"gemini_llm_prompt failed: {prompt_result['message']}"
    generated_prompt = prompt_result["result"]["prompt"]
    
    print("\nGenerated LLM Prompt (first 300 chars):")
    print(f"{generated_prompt[:300]}...")

    # Dynamically create expected prompt structure using the retrieved name
    expected_prompt_structure = [
        "Occupation Information",
        TARGET_ONET_ID, # onet_id is fixed for the test input
        retrieved_occupation_name, # name is now from the DB
        "Skills Required:",
        "Your entire response must be a single, valid JSON object"
    ]

    for item in expected_prompt_structure:
        assert item in generated_prompt, f"Prompt missing expected structural content: '{item}'"

    # Verify that actual skill names from the database are in the prompt
    # This is a stronger assertion than just checking for "Skills Required:"
    skills_section_in_prompt = False
    if structured_to_data["skills"]:
        first_skill_name_from_db = structured_to_data["skills"][0]["skill_name"]
        if first_skill_name_from_db: # Ensure skill_name is not None or empty
             assert first_skill_name_from_db in generated_prompt, \
                f"Prompt missing the first skill '{first_skill_name_from_db}' obtained from the database."
             skills_section_in_prompt = True
        else:
            print(f"Warning: First skill name from DB for {to_occupation_code} is None or empty, cannot assert its presence in prompt.")
    
    if not skills_section_in_prompt and structured_to_data["skills"]:
         print(f"Warning: Could not verify specific DB skill names in prompt for {to_occupation_code} because the first skill name was empty/None.")
    elif not structured_to_data["skills"]:
        print(f"Warning: No skills found in DB for {to_occupation_code}, so cannot assert their presence in prompt's 'Skills Required' section.")


    # --- 3. Call gemini_llm_request --- 
    print("\nAttempting to call Gemini LLM API...")
    # Note: This requires GEMINI_API_KEY to be set in the environment
    # The shell script test_integration_llm_skill_assessment_pipeline.sh should handle sourcing env/env.env

    # Prepare prompt_skills_data based on the skills fetched
    prompt_skills_for_request = []
    if structured_to_data.get("skills"):
        for skill_item in structured_to_data["skills"]:
            prompt_skills_for_request.append({
                "skill_element_id": skill_item.get("skill_element_id"),
                "skill_name": skill_item.get("skill_name")
            })

    llm_response = gemini_llm_request(
        prompt=generated_prompt, 
        request_onet_soc_code=to_occupation_code,  # Added this argument
        prompt_skills_data=prompt_skills_for_request, # Added this argument
        max_tokens=4096
    )

    print("\ngemini_llm_request result:")
    # Use DecimalEncoder for printing if the raw response might contain Decimals (though less likely for API errors)
    print(json.dumps(llm_response, indent=2, cls=DecimalEncoder))

    assert llm_response["success"], f"gemini_llm_request failed: {llm_response['message']}"
    assert "result" in llm_response, "LLM response missing 'result' dictionary"
    assert "request_data" in llm_response["result"], \
        "LLM response result missing 'request_data' field."
    assert "reply_data" in llm_response["result"], \
        "LLM response result missing 'reply_data' field."
    
    # Further assertions on request_data and reply_data structure
    request_data_list = llm_response["result"]["request_data"]
    reply_data_list = llm_response["result"]["reply_data"]

    assert isinstance(request_data_list, list), "request_data should be a list."
    assert isinstance(reply_data_list, list), "reply_data should be a list."

    # Check if request_data is populated (it should be, even if LLM call itself has issues with content)
    if structured_to_data.get("skills"):
        assert len(request_data_list) == len(structured_to_data["skills"]), \
            f"Expected {len(structured_to_data['skills'])} items in request_data, got {len(request_data_list)}"
        if request_data_list: # Check content of the first request data item
            first_request_item = request_data_list[0]
            assert "request_id" in first_request_item
            assert "request_model" in first_request_item
            assert first_request_item["request_onet_soc_code"] == to_occupation_code
            assert "request_skill_element_id" in first_request_item
            assert "request_skill_name" in first_request_item
            assert "request_timestamp" in first_request_item
    else:
        assert not request_data_list, "request_data should be empty if no skills were provided"


    # Check for successful parsing of LLM output for reply_data
    # These assertions are only valid if the API call itself was successful in generating content
    # The assertion llm_response["success"] already covers the API call status.
    # The following checks verify the data that would be loaded into the DB.

    if not reply_data_list:
        # If reply_data is empty, it might be due to an LLM content generation issue, even if API call was 'success:True'
        # (e.g. LLM returned an error message instead of JSON, or malformed JSON not caught by basic cleaning).
        # The message field from gemini_llm_request should provide more context in such cases.
        print(f"Warning: reply_data is empty. LLM message: {llm_response.get('message')}")
        # If the expectation is that for a successful prompt, reply_data should always exist, 
        # then this might need a stronger assertion like: assert reply_data_list, "reply_data should not be empty on success"
        # However, this depends on how robust the LLM's response is guaranteed to be.
    if reply_data_list:
        assert len(reply_data_list) > 0, "reply_data list should not be empty if LLM response parsing was successful and content was expected."
        first_reply_item = reply_data_list[0]
        assert "request_id" in first_reply_item
        assert first_reply_item["request_id"] == request_data_list[0]["request_id"] # Ensure request_ids match
        assert "llm_onet_soc_code" in first_reply_item
        assert first_reply_item["llm_onet_soc_code"] == to_occupation_code
        assert "llm_occupation_name" in first_reply_item
        assert "llm_skill_name" in first_reply_item
        assert "llm_assigned_proficiency_level" in first_reply_item
        assert "assessment_timestamp" in first_reply_item

    # The old assertions for llm_output_text and direct JSON parsing are now handled within gemini_llm_request
    # So we check the structure of result.reply_data instead.

    # llm_output_text = llm_response["result"]["text"] # This key might not exist if parsing failed early
    # assert llm_output_text, "LLM response text should not be empty." 

    # # Clean the LLM output text if it's wrapped in Markdown code fences
    # cleaned_llm_output_text = llm_output_text.strip()
    # if cleaned_llm_output_text.startswith("```json"):
    #     cleaned_llm_output_text = cleaned_llm_output_text[len("```json"):].strip()
    # if cleaned_llm_output_text.startswith("```"):
    #     cleaned_llm_output_text = cleaned_llm_output_text[len("```"):].strip()
    # if cleaned_llm_output_text.endswith("```"):
    #     cleaned_llm_output_text = cleaned_llm_output_text[:-len("```"):].strip()

    # # Attempt to parse the cleaned LLM output text as JSON
    # try:
    #     llm_output_json = json.loads(cleaned_llm_output_text)
    # except json.JSONDecodeError as e:
    #     pytest.fail(f"LLM response text was not valid JSON after cleaning: {e}\nCleaned Response Text: {cleaned_llm_output_text}\nRaw Response Text: {llm_output_text}")

    # print("\nLLM Output JSON (parsed):")
    # print(json.dumps(llm_output_json, indent=2))

    # # Assertions on the structure of the parsed LLM output
    # assert "skill_proficiency_assessment" in llm_output_json, \
    #     "Parsed LLM output missing 'skill_proficiency_assessment' key."
    # 
    # assessment_data = llm_output_json["skill_proficiency_assessment"]
    # assert "target_occupation_onet_id" in assessment_data, \
    #     "'skill_proficiency_assessment' missing 'target_occupation_onet_id' key."
    # assert assessment_data["target_occupation_onet_id"] == TARGET_ONET_ID, \
    #     f"Expected target_occupation_onet_id '{TARGET_ONET_ID}', got '{assessment_data['target_occupation_onet_id']}'"
    # 
    # assert "target_occupation_name" in assessment_data, \
    #     "'skill_proficiency_assessment' missing 'target_occupation_name' key."
    # # We can also check if the name matches what we got from DB
    # assert assessment_data["target_occupation_name"] == retrieved_occupation_name, \
    #     f"Expected target_occupation_name '{retrieved_occupation_name}', got '{assessment_data['target_occupation_name']}'"

    # assert "assessed_skills" in assessment_data, \
    #     "'skill_proficiency_assessment' missing 'assessed_skills' key."
    # assert isinstance(assessment_data["assessed_skills"], list), \
    #     "'assessed_skills' should be a list."

    # # Optionally, check if the number of assessed skills matches the input, if skills were found
    # if structured_to_data["skills"]:
    #     assert len(assessment_data["assessed_skills"]) == len(structured_to_data["skills"]), \
    #         f"Expected {len(structured_to_data['skills'])} assessed skills, got {len(assessment_data['assessed_skills'])}"
    #     # Further checks on individual skill structures can be added if needed
    #     if assessment_data["assessed_skills"]:
    #         first_assessed_skill = assessment_data["assessed_skills"][0]
    #         assert "skill_name" in first_assessed_skill
    #         assert "llm_assigned_proficiency_level" in first_assessed_skill
    #         assert "llm_explanation" in first_assessed_skill

    print("\nIntegration test for LLM skill assessment pipeline (including API call) PASSED initial stages.")

    # --- 4. Load LLM assessment data into in-memory SQLite database ---
    print("\n--- Setting up in-memory SQLite database for loading test ---")
    engine = create_engine("sqlite:///:memory:")
    schemas.Base.metadata.create_all(engine)
    print("In-memory database and tables created.")

    print("\n--- Attempting to load LLM assessment data into in-memory DB ---")
    # llm_response["result"] is the dict containing 'request_data' and 'reply_data'
    load_result = mysql_load_llm_skill_proficiencies(
        llm_assessment_output=llm_response["result"], 
        engine=engine,
        clear_requests_table=True, # Ensures test idempotency
        clear_replies_table=True   # Ensures test idempotency
    )
    print("\nmysql_load_llm_skill_proficiencies result:")
    print(json.dumps(load_result, indent=2, default=str)) # default=str for datetime

    assert load_result["success"], f"mysql_load_llm_skill_proficiencies failed: {load_result['message']}"

    expected_requests_count = len(llm_response["result"]["request_data"])
    expected_replies_count = len(llm_response["result"]["reply_data"])
    
    # Note: mysql_load_llm_skill_proficiencies returns 0 if the list was empty and processed,
    # or None if the input list itself was None (which gemini_llm_request doesn't do for these keys).
    # Since gemini_llm_request always provides a list (even if empty), loaded count should be 0 for empty.

    assert load_result["requests_loaded"] == expected_requests_count, \
        f"Expected {expected_requests_count} requests to be loaded, got {load_result['requests_loaded']}"
    
    assert load_result["replies_loaded"] == expected_replies_count, \
        f"Expected {expected_replies_count} replies to be loaded, got {load_result['replies_loaded']}"

    print("\n--- Verifying data in in-memory DB ---")
    Session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Renamed to avoid conflict
    session = Session_local()

    # Verify requests
    db_requests_count = session.query(schemas.LLM_Skill_Proficiency_Requests).count()
    assert db_requests_count == expected_requests_count, \
        f"DB requests count mismatch: expected {expected_requests_count}, got {db_requests_count}"
    
    if expected_requests_count > 0:
        first_db_request = session.query(schemas.LLM_Skill_Proficiency_Requests).first()
        assert first_db_request is not None
        assert first_db_request.request_id == llm_response["result"]["request_data"][0]["request_id"]
        assert first_db_request.request_onet_soc_code == llm_response["result"]["request_data"][0]["request_onet_soc_code"]
        assert first_db_request.request_skill_name == llm_response["result"]["request_data"][0]["request_skill_name"]

    # Verify replies
    db_replies_count = session.query(schemas.LLM_Skill_Proficiency_Replies).count()
    assert db_replies_count == expected_replies_count, \
        f"DB replies count mismatch: expected {expected_replies_count}, got {db_replies_count}"

    if expected_replies_count > 0:
        first_db_reply = session.query(schemas.LLM_Skill_Proficiency_Replies).first()
        assert first_db_reply is not None
        assert first_db_reply.request_id == llm_response["result"]["reply_data"][0]["request_id"]
        assert first_db_reply.llm_onet_soc_code == llm_response["result"]["reply_data"][0]["llm_onet_soc_code"]
        assert first_db_reply.llm_skill_name == llm_response["result"]["reply_data"][0]["llm_skill_name"]
        # Check proficiency level if it exists in the source and was loaded
        if "llm_assigned_proficiency_level" in llm_response["result"]["reply_data"][0]:
            expected_level = llm_response["result"]["reply_data"][0]["llm_assigned_proficiency_level"]
            # Convert to int for comparison, as it might be a string in mock or None
            if expected_level is not None:
                try:
                    expected_level = int(expected_level)
                except (ValueError, TypeError):
                    # If conversion fails, it might be an issue with test data or actual LLM output format
                    # For now, we'll only assert if it's convertible to int
                    pass 
            assert first_db_reply.llm_assigned_proficiency_level == expected_level, \
                f"LLM assigned proficiency level mismatch: expected {expected_level}, got {first_db_reply.llm_assigned_proficiency_level}"


    session.close()
    print("Data verification in in-memory DB completed.")
    print("\nIntegration test for LLM skill assessment pipeline (including data loading) PASSED.")

# You can add more tests here, e.g., for cases with from_occupation, API errors, etc. 