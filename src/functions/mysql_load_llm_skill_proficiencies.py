"""
Function to load LLM skill proficiency request and reply data into the database.
"""
import pandas as pd
from sqlalchemy.engine import Engine
from typing import Dict, Any
import logging

# Assuming schemas and load_data_from_dataframe are in accessible paths
# Adjust imports based on your project structure if necessary
import src.config.schemas as schemas
from src.functions.mysql_load_table import load_data_from_dataframe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def mysql_load_llm_skill_proficiencies(
    llm_assessment_output: Dict[str, Any], 
    engine: Engine,
    clear_requests_table: bool = False,
    clear_replies_table: bool = False
) -> Dict[str, Any]:
    """
    Loads the structured request and reply data from the gemini_llm_request function
    into their respective database tables.

    Args:
        llm_assessment_output (Dict[str, Any]): The dictionary returned by the 
                                                 gemini_llm_request function, containing 
                                                 'request_data' and 'reply_data' lists.
        engine (Engine): SQLAlchemy engine for database connection.
        clear_requests_table (bool): Whether to clear LLM_Skill_Proficiency_Requests
                                     before loading. Defaults to False.
        clear_replies_table (bool): Whether to clear LLM_Skill_Proficiency_Replies
                                    before loading. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary summarizing the loading operation, with keys:
                        'success' (bool), 
                        'message' (str),
                        'requests_loaded' (int | None),
                        'replies_loaded' (int | None),
                        'request_load_message' (str | None),
                        'reply_load_message' (str | None)
    """
    if not llm_assessment_output or not isinstance(llm_assessment_output, dict):
        return {
            "success": False, 
            "message": "Invalid llm_assessment_output provided. Expected a dictionary.",
            "requests_loaded": None, "replies_loaded": None,
            "request_load_message": "Input was invalid.",
            "reply_load_message": "Input was invalid."
        }

    request_data_list = llm_assessment_output.get("request_data")
    reply_data_list = llm_assessment_output.get("reply_data")

    overall_success = True
    messages = []
    requests_loaded_count = None
    replies_loaded_count = None
    req_load_msg = "No request data provided or data was empty."
    rep_load_msg = "No reply data provided or data was empty."

    # Load Request Data
    if request_data_list and isinstance(request_data_list, list) and len(request_data_list) > 0:
        try:
            request_df = pd.DataFrame(request_data_list)
            logging.info(f"Attempting to load {len(request_df)} records into LLM_Skill_Proficiency_Requests.")
            
            # Convert timestamp to datetime objects if they are not already (e.g. if coming from JSON)
            if 'request_timestamp' in request_df.columns:
                 request_df['request_timestamp'] = pd.to_datetime(request_df['request_timestamp'])

            load_req_result = load_data_from_dataframe(
                df=request_df,
                model=schemas.LLM_Skill_Proficiency_Requests,
                engine=engine,
                clear_existing=clear_requests_table
            )
            if load_req_result["success"]:
                requests_loaded_count = load_req_result["result"].get("records_loaded", 0)
                req_load_msg = f"Successfully loaded {requests_loaded_count} request records."
                messages.append(req_load_msg)
                logging.info(req_load_msg)
                if requests_loaded_count < len(request_df) and not clear_requests_table :
                    pk_warning = " Warning: Not all request records may have been loaded. This could be due to existing records violating the composite primary key (request_id, request_onet_soc_code, request_skill_element_id) or other database constraints. Check logs."
                    req_load_msg += pk_warning
                    messages.append(pk_warning)
                    logging.warning(pk_warning)
            else:
                overall_success = False
                req_load_msg = f"Failed to load request data: {load_req_result['message']}"
                messages.append(req_load_msg)
                logging.error(req_load_msg)
        except Exception as e:
            overall_success = False
            req_load_msg = f"Error preparing or loading request data: {str(e)}"
            messages.append(req_load_msg)
            logging.error(req_load_msg)
    elif request_data_list is None: # Explicitly None
         req_load_msg = "request_data was None."
    elif not request_data_list: # Empty list
         req_load_msg = "request_data list was empty."


    # Load Reply Data
    if reply_data_list and isinstance(reply_data_list, list) and len(reply_data_list) > 0:
        try:
            reply_df = pd.DataFrame(reply_data_list)
            logging.info(f"Attempting to load {len(reply_df)} records into LLM_Skill_Proficiency_Replies.")

            if 'assessment_timestamp' in reply_df.columns:
                reply_df['assessment_timestamp'] = pd.to_datetime(reply_df['assessment_timestamp'])
            
            # Convert potential numeric string representations for level to int, handling None/NaN
            if 'llm_assigned_proficiency_level' in reply_df.columns:
                reply_df['llm_assigned_proficiency_level'] = pd.to_numeric(
                    reply_df['llm_assigned_proficiency_level'], errors='coerce'
                ).astype('Int64') # Use Int64 to allow for NA


            load_rep_result = load_data_from_dataframe(
                df=reply_df,
                model=schemas.LLM_Skill_Proficiency_Replies,
                engine=engine,
                clear_existing=clear_replies_table
            )
            if load_rep_result["success"]:
                replies_loaded_count = load_rep_result["result"].get("records_loaded", 0)
                rep_load_msg = f"Successfully loaded {replies_loaded_count} reply records."
                messages.append(rep_load_msg)
                logging.info(rep_load_msg)
                if replies_loaded_count < len(reply_df) and not clear_replies_table:
                    pk_warning = " Warning: Not all reply records may have been loaded. This could be due to existing records violating the composite primary key (request_id, llm_onet_soc_code, llm_skill_name) or other database constraints. Check logs."
                    rep_load_msg += pk_warning
                    messages.append(pk_warning)
                    logging.warning(pk_warning)
            else:
                overall_success = False
                rep_load_msg = f"Failed to load reply data: {load_rep_result['message']}"
                messages.append(rep_load_msg)
                logging.error(rep_load_msg)
        except Exception as e:
            overall_success = False
            rep_load_msg = f"Error preparing or loading reply data: {str(e)}"
            messages.append(rep_load_msg)
            logging.error(rep_load_msg)
    elif reply_data_list is None: # Explicitly None
         rep_load_msg = "reply_data was None."
    elif not reply_data_list: # Empty list
         rep_load_msg = "reply_data list was empty."


    final_message = "LLM data loading process completed. " + " | ".join(filter(None, messages))
    if not messages: # if both lists were empty/None
        final_message = req_load_msg + " " + rep_load_msg
        
    return {
        "success": overall_success,
        "message": final_message.strip(),
        "requests_loaded": requests_loaded_count,
        "replies_loaded": replies_loaded_count,
        "request_load_message": req_load_msg.strip(),
        "reply_load_message": rep_load_msg.strip()
    }

if __name__ == '__main__':
    from sqlalchemy import create_engine
    from datetime import datetime

    print("Minimalistic happy path example for mysql_load_llm_skill_proficiencies.")
    print("This example uses an in-memory SQLite database and mock data.")

    example_engine = create_engine("sqlite:///:memory:")
    schemas.Base.metadata.create_all(example_engine)

    # 1. Prepare Mock LLM Assessment Output (as if from gemini_llm_request)
    mock_request_id = "test-req-001"
    mock_timestamp = datetime.utcnow()

    mock_llm_output = {
        "request_data": [
            {
                "request_id": mock_request_id,
                "request_model": "gemini-pro",
                "request_onet_soc_code": "11-1011.00",
                "request_skill_element_id": "1.A.1",
                "request_skill_name": "Skill A",
                "request_timestamp": mock_timestamp
            },
            # Due to the composite primary key (request_id, request_onet_soc_code, request_skill_element_id),
            # this second item with a *different* skill_element_id *will* load, even with the same request_id.
            # If all three PK components were identical to the first, it would not load if clear_requests_table=False.
            {
                "request_id": mock_request_id, # Same request_id
                "request_model": "gemini-pro",
                "request_onet_soc_code": "11-1011.00",
                "request_skill_element_id": "1.A.2", 
                "request_skill_name": "Skill B",
                "request_timestamp": mock_timestamp
            }
        ],
        "reply_data": [
            {
                "request_id": mock_request_id,
                "llm_onet_soc_code": "11-1011.00",
                "llm_occupation_name": "Test Occupation",
                "llm_skill_name": "Skill A",
                "llm_assigned_proficiency_description": "Expert",
                "llm_assigned_proficiency_level": 7, # Integer
                "llm_explanation": "Explanation for Skill A",
                "assessment_timestamp": mock_timestamp
            },
            # Similarly, for replies, the composite PK is (request_id, llm_onet_soc_code, llm_skill_name).
            # This second item with a *different* llm_skill_name *will* load.
            {
                "request_id": mock_request_id, # Same request_id
                "llm_onet_soc_code": "11-1011.00",
                "llm_occupation_name": "Test Occupation",
                "llm_skill_name": "Skill B",
                "llm_assigned_proficiency_description": "Advanced",
                "llm_assigned_proficiency_level": "6", # String representation of integer
                "llm_explanation": "Explanation for Skill B",
                "assessment_timestamp": mock_timestamp
            }
        ]
    }

    # 2. Call the loading function (clear_existing=True to ensure idempotency for example)
    print("\n--- Attempting to load mock LLM data (clear_existing=True for both tables) ---")
    load_result_clear = mysql_load_llm_skill_proficiencies(
        llm_assessment_output=mock_llm_output,
        engine=example_engine,
        clear_requests_table=True,
        clear_replies_table=True
    )
    print("Load Result (clear_existing=True):")
    print(json.dumps(load_result_clear, indent=2, default=str))

    # 3. Call again with clear_existing=False to demonstrate PK issue if schema not changed
    print("\n--- Attempting to load same mock LLM data again (clear_existing=False) ---")
    # This will attempt to load the same records again.
    # If clear_existing is False, records that would violate the composite primary key constraints
    # (i.e., duplicates based on the combination of PK fields) will not be inserted.
    # The warning messages in the function's output should indicate if fewer records than expected were loaded.
    load_result_append = mysql_load_llm_skill_proficiencies(
        llm_assessment_output=mock_llm_output, # Using the same data
        engine=example_engine,
        clear_requests_table=False, 
        clear_replies_table=False
    )
    print("Load Result (clear_existing=False):")
    # Using json.dumps with default=str for datetime, though not strictly necessary here
    # as we are printing the function's return dict which should already be JSON-serializable.
    import json # ensure json is imported for the print
    print(json.dumps(load_result_append, indent=2, default=str))


    # Example with empty data
    print("\n--- Attempting to load empty LLM data ---")
    empty_output = {"request_data": [], "reply_data": []}
    load_result_empty = mysql_load_llm_skill_proficiencies(
        llm_assessment_output=empty_output,
        engine=example_engine
    )
    print("Load Result (empty data):")
    print(json.dumps(load_result_empty, indent=2, default=str))
    
    print("\nExample finished.") 