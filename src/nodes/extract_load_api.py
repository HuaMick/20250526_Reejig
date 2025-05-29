import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv

from src.functions.onet_api_extract_occupation import onet_api_extract_occupation
from src.functions.onet_api_extract_skills import onet_api_extract_skills
from src.functions.onet_api_extract_scales import onet_api_extract_scales
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

def run_extract_load_api_data():
    """
    Orchestrates the extraction of data from O*NET APIs and loading into respective database tables.
    
    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str), 
              and 'result' (dict containing details of operations).
    """
    logging.info("Starting O*NET API data extraction and load process...")

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
    logging.info("--- Starting Occupation API Data --- ")
    occ_data_result = onet_api_extract_occupation(username=api_username, password=api_password)
    if occ_data_result["success"] and occ_data_result["result"] and not occ_data_result["result"]["occupation_df"].empty:
        occupation_df = occ_data_result["result"]["occupation_df"]
        logging.info(f"Successfully extracted {len(occupation_df)} occupation records from API.")
        load_occ_result = load_data_from_dataframe(
            df=occupation_df, 
            model=schemas.Onet_Occupations_API_landing, 
            engine=engine, 
            clear_existing=clear_tables
        )
        operation_summary.append({"step": "Load Occupations API", "details": load_occ_result})
        if not load_occ_result["success"]:
            overall_success = False
    elif not occ_data_result["success"]:
        logging.error(f"Failed to extract occupation data: {occ_data_result['message']}")
        operation_summary.append({"step": "Extract Occupations API", "details": occ_data_result})
        overall_success = False
    else:
        logging.info("No occupation data extracted or DataFrame was empty.")
        operation_summary.append({"step": "Extract Occupations API", "details": "No data or empty DataFrame."}) 

    # 2. Extract and Load Skills API Data
    logging.info("--- Starting Skills API Data --- ")
    skills_data_result = onet_api_extract_skills(username=api_username, password=api_password)
    if skills_data_result["success"] and skills_data_result["result"] and not skills_data_result["result"]["skills_df"].empty:
        skills_df = skills_data_result["result"]["skills_df"]
        logging.info(f"Successfully extracted {len(skills_df)} skills records from API.")
        load_skills_result = load_data_from_dataframe(
            df=skills_df, 
            model=schemas.Onet_Skills_API_landing, 
            engine=engine, 
            clear_existing=clear_tables
        )
        operation_summary.append({"step": "Load Skills API", "details": load_skills_result})
        if not load_skills_result["success"]:
            overall_success = False
    elif not skills_data_result["success"]:
        logging.error(f"Failed to extract skills data: {skills_data_result['message']}")
        operation_summary.append({"step": "Extract Skills API", "details": skills_data_result})
        overall_success = False
    else:
        logging.info("No skills data extracted or DataFrame was empty.")
        operation_summary.append({"step": "Extract Skills API", "details": "No data or empty DataFrame."}) 

    # 3. Extract and Load Scales API Data
    logging.info("--- Starting Scales API Data --- ")
    scales_data_result = onet_api_extract_scales(username=api_username, password=api_password)
    if scales_data_result["success"] and scales_data_result["result"] and not scales_data_result["result"]["scales_df"].empty:
        scales_df = scales_data_result["result"]["scales_df"]
        logging.info(f"Successfully extracted {len(scales_df)} scales records from API.")
        load_scales_result = load_data_from_dataframe(
            df=scales_df, 
            model=schemas.Onet_Scales_API_landing, 
            engine=engine, 
            clear_existing=clear_tables
        )
        operation_summary.append({"step": "Load Scales API", "details": load_scales_result})
        if not load_scales_result["success"]:
            overall_success = False
    elif not scales_data_result["success"]:
        logging.error(f"Failed to extract scales data: {scales_data_result['message']}")
        operation_summary.append({"step": "Extract Scales API", "details": scales_data_result})
        overall_success = False
    else:
        logging.info("No scales data extracted or DataFrame was empty.")
        operation_summary.append({"step": "Extract Scales API", "details": "No data or empty DataFrame."}) 

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

    node_result = run_extract_load_api_data()
    logging.info(f"Node execution finished. Success: {node_result['success']}. Message: {node_result['message']}")
    
    if node_result["result"] and node_result["result"].get("operations"):
        logging.info("Operation Summary:")
        for op in node_result["result"]["operations"]:
            logging.info(f"  Step: {op['step']}")
            details = op['details']
            if isinstance(details, dict):
                logging.info(f"    Success: {details.get('success')}")
                logging.info(f"    Message: {details.get('message')}")
                if details.get('result'):
                    logging.info(f"    Result Details: {details.get('result')}")
            else:
                logging.info(f"    Details: {details}")
