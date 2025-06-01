import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pandas as pd # For concatenating skills DataFrames
from typing import List, Optional # For type hinting

from src.functions.onet_api_extract_occupation import onet_api_extract_occupation
from src.functions.onet_api_extract_skills import onet_api_extract_skills
from src.functions.mysql_load_table import load_data_from_dataframe
import src.config.schemas as schemas

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_engine():
    """Creates and returns a SQLAlchemy engine using environment variables."""
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_port = os.getenv('MYSQL_PORT', '3306')
    db_user = os.getenv('MYSQL_USER')
    db_password = os.getenv('MYSQL_PASSWORD')
    db_name = os.getenv('MYSQL_DATABASE')

    if not all([db_user, db_password, db_name, db_host, db_port]):
        logging.error("Database connection parameters (MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, MYSQL_PORT) must be set in environment variables.")
        raise ValueError("Missing database connection parameters.")

    engine_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    try:
        engine = create_engine(engine_url)
        logging.info("Database engine created successfully.")
        return engine
    except Exception as e:
        logging.error(f"Failed to create database engine: {e}")
        raise

def run_extract_load_api_data(target_occupation_codes: Optional[List[str]] = None):
    """
    Orchestrates O*NET API data extraction and loading.
    If target_occupation_codes are provided, fetches data only for those occupations and their specific skills.
    Otherwise, performs a bulk extraction of all occupations and generic skills data.
    """
    if target_occupation_codes:
        logging.info(f"Starting TARGETED O*NET API data extraction for codes: {target_occupation_codes}")
    else:
        logging.info("Starting BULK O*NET API data extraction and load process...")

    api_username = os.getenv("ONET_USERNAME")
    api_password = os.getenv("ONET_PASSWORD")

    if not api_username or not api_password:
        logging.error("ONET_USERNAME and ONET_PASSWORD environment variables must be set.")
        return {
            "success": False, 
            "message": "API credentials (ONET_USERNAME, ONET_PASSWORD) not found in environment variables.",
            "result": {}
        }

    try:
        engine = get_db_engine()
    except ValueError as e:
        return {"success": False, "message": str(e), "result": {}}
    except Exception as e: # Catch other potential engine creation errors
        return {"success": False, "message": f"Failed to initialize database engine: {e}", "result": {}}

    overall_success = True
    operation_summary = []
    clear_tables = True # Configurable: whether to clear tables before loading

    # 1. Extract and Load Occupations API Data
    logging.info("--- Starting Occupation API Data Extraction --- ")
    occupation_filters = None
    if target_occupation_codes:
        occupation_filters = [f"onetsoc_code.eq.{code}" for code in target_occupation_codes]
    
    occ_data_result = onet_api_extract_occupation(
        username=api_username, 
        password=api_password,
        filter_params=occupation_filters
    )
    occupation_df = pd.DataFrame() # Initialize empty df

    if occ_data_result["success"] and occ_data_result["result"]:
        occupation_df = occ_data_result["result"]["occupation_df"]
        if not occupation_df.empty:
            logging.info(f"Extracted {len(occupation_df)} occupation records from API.")
            load_occ_result = load_data_from_dataframe(
                df=occupation_df, 
                model=schemas.Onet_Occupations_API_landing, 
                engine=engine, 
                clear_existing=clear_tables # Be cautious with clear_existing for targeted updates
            )
            operation_summary.append({"step": "Load Occupations API", "details": load_occ_result})
            if not load_occ_result["success"]: overall_success = False
        else:
            logging.info("No occupation data extracted (empty DataFrame).")
            operation_summary.append({"step": "Extract Occupations API", "details": "No data or empty DataFrame."})
    else:
        logging.error(f"Failed to extract occupation data: {occ_data_result['message']}")
        operation_summary.append({"step": "Extract Occupations API", "details": occ_data_result})
        overall_success = False

    # 2. Extract and Load Skills API Data
    logging.info("--- Starting Skills API Data Extraction ---")
    all_skills_dfs = []
    skills_extraction_failed = False

    if target_occupation_codes:
        # Fetch skills specifically for each targeted occupation
        if not occupation_df.empty: # Ensure we have the list of successfully fetched occupations
            actual_fetched_codes = occupation_df['onet_soc_code'].unique()
            logging.info(f"Fetching specific skills for {len(actual_fetched_codes)} occupation(s): {actual_fetched_codes}")
            for code in actual_fetched_codes:
                logging.info(f"Fetching skills for occupation: {code}")
                specific_skills_result = onet_api_extract_occupation_specific_skills(
                    onet_soc_code=code,
                    username=api_username,
                    password=api_password
                )
                if specific_skills_result["success"] and specific_skills_result["result"]:
                    skills_page_df = specific_skills_result["result"]["skills_df"]
                    if not skills_page_df.empty:
                        all_skills_dfs.append(skills_page_df)
                    else:
                        logging.info(f"No specific skills returned for occupation {code}.")
                else:
                    logging.error(f"Failed to extract specific skills for {code}: {specific_skills_result['message']}")
                    skills_extraction_failed = True # Mark failure but continue for other codes if possible
                    operation_summary.append({"step": f"Extract Specific Skills {code}", "details": specific_skills_result})
        else:
            logging.warning("Target occupation codes provided, but no occupations were successfully fetched. Skipping specific skills extraction.")
            skills_extraction_failed = True # Considered a failure in the targeted skills step
    else:
        # Bulk extract generic skills data
        skills_data_result = onet_api_extract_skills(username=api_username, password=api_password)
        if skills_data_result["success"] and skills_data_result["result"]:
            skills_page_df = skills_data_result["result"]["skills_df"]
            if not skills_page_df.empty:
                all_skills_dfs.append(skills_page_df)
        else:
            logging.error(f"Failed to extract generic skills data: {skills_data_result['message']}")
            skills_extraction_failed = True
            operation_summary.append({"step": "Extract Generic Skills API", "details": skills_data_result})

    if all_skills_dfs:
        final_skills_df = pd.concat(all_skills_dfs, ignore_index=True)
        logging.info(f"Total of {len(final_skills_df)} skills records compiled for loading.")
        # For targeted loads, if clearing table, ensure it only clears relevant skills if possible, or accept full clear.
        # Current load_data_from_dataframe clears the whole table if clear_existing=True.
        load_skills_result = load_data_from_dataframe(
            df=final_skills_df, 
            model=schemas.Onet_Skills_API_landing, 
            engine=engine, 
            clear_existing=clear_tables 
        )
        operation_summary.append({"step": "Load Skills API", "details": load_skills_result})
        if not load_skills_result["success"]: overall_success = False
    elif not skills_extraction_failed:
        logging.info("No skills data extracted or DataFrame was empty (no errors).")
        operation_summary.append({"step": "Extract Skills API", "details": "No skills data or empty DataFrame."})
    else: # skills_extraction_failed is True
        logging.error("Skills extraction failed. No skills data to load.")
        # overall_success might already be false if individual skill extractions were logged as failed ops
        overall_success = False 

    final_message = "O*NET API data extraction and load process completed."
    if not overall_success:
        final_message += " Some operations failed."
    
    logging.info(final_message)
    for summary_item in operation_summary:
        logging.info(f"  Step: {summary_item['step']}, Success: {summary_item['details'].get('success', 'N/A') if isinstance(summary_item['details'], dict) else 'N/A'}, Message: {summary_item['details'].get('message', summary_item['details']) if isinstance(summary_item['details'], dict) else summary_item['details']}")

    return {
        "success": overall_success,
        "message": final_message,
        "result": {"operations": operation_summary}
    }

if __name__ == '__main__':
    logging.info("Executing O*NET API Extract and Load Node directly.")
    
    # Ensure environment variables are loaded (e.g., from a .env file if running locally)
    # You would typically set ONET_API_USERNAME, ONET_API_PASSWORD, and MYSQL_* vars in your environment or .env
    
    # Example: Create a .env file in your project root with lines like:
    # ONET_API_USERNAME="your_onet_username"
    # ONET_API_PASSWORD="your_onet_password"
    # MYSQL_HOST="localhost"
    # MYSQL_PORT="3306"
    # MYSQL_USER="your_db_user"
    # MYSQL_PASSWORD="your_db_password"
    # MYSQL_DATABASE="your_db_name"

    # This check is to prevent running without guidance if credentials are not set
    if not os.getenv("ONET_USERNAME") or not os.getenv("MYSQL_USER"):
        logging.warning("-------------------------------------------------------------------------------------")
        logging.warning("MISSING CREDENTIALS: This script requires O*NET API and MySQL credentials.")
        logging.warning("Please ensure ONET_USERNAME, ONET_PASSWORD, and all MYSQL_ environment")
        logging.warning("variables (MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)")
        logging.warning("are set in your environment or in a .env file in the project root.")
        logging.warning("Node execution will proceed but likely fail if credentials are not available.")
        logging.warning("-------------------------------------------------------------------------------------")

    target_codes_input = input("Enter O*NET SOC codes to target (comma-separated, or leave blank for bulk): ")
    target_codes = [code.strip() for code in target_codes_input.split(',') if code.strip()] if target_codes_input else None

    node_result = run_extract_load_api_data(target_occupation_codes=target_codes)
    logging.info(f"Node execution finished. Success: {node_result['success']}. Message: {node_result['message']}")
    
    if node_result["result"] and node_result["result"].get("operations"):
        logging.info("Detailed Operation Summary:")
        for op in node_result["result"]["operations"]:
            details = op['details']
            message = details.get('message', str(details)) if isinstance(details, dict) else str(details)
            logging.info(f"  Step: {op['step']}, Success: {details.get('success', 'N/A') if isinstance(details, dict) else 'N/A'}, Msg: {message[:100]}") # Truncate long messages
