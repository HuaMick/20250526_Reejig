import os
import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import sys
import pytest

# Ensure imports use full paths from project root
from src.functions.onet_api_extract_occupation import onet_api_extract_occupation
from src.functions.mysql_load_table import load_data_from_dataframe
import src.config.schemas as schemas

from src.config.schemas import get_sqlalchemy_engine
from tests.fixtures.db_config import test_db_config

# Configure specific logger for this test module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Define constants for the test
TEST_ONET_SOC_CODE = "15-1254.00"  # Web Developers
EXPECTED_TITLE_CONTAINS = "Web Developers"

def test_extract_and_load_filtered_api_occupation(test_db_config):
    """
    Integration test for extracting a single O*NET API occupation by onet_soc_code
    and loading it into the Onet_Occupations_API_landing table in the MySQL test database.
    
    This test:
    1. Extracts occupation data for Web Developers from the O*NET API
    2. Loads the data into the Onet_Occupations_API_landing table in the test database
    3. Verifies the loaded data with SQL queries
    """
    logger.info(f"Starting integration test for filtered occupation: {TEST_ONET_SOC_CODE}")
    logger.info(f"Using test database: {test_db_config['database']}")

    onet_username = os.getenv("ONET_USERNAME")
    onet_password = os.getenv("ONET_PASSWORD")

    assert onet_username, "ONET_USERNAME environment variable not set."
    assert onet_password, "ONET_PASSWORD environment variable not set."
    logger.info("Successfully retrieved O*NET API credentials.")

    # Define filter for the specific occupation code
    filter_list = [f"onetsoc_code.eq.{TEST_ONET_SOC_CODE}"]
    logger.info(f"Attempting to extract O*NET occupation data from API with filter: {filter_list}...")
    
    api_extraction_result = onet_api_extract_occupation(
        username=onet_username, 
        password=onet_password,
        filter_params=filter_list
    )
    
    logger.info(f"API Extraction Result: Success={api_extraction_result['success']}, Message='{api_extraction_result['message']}'")
    assert api_extraction_result["success"], f"O*NET API extraction failed: {api_extraction_result['message']}"
    
    occupations_df = api_extraction_result["result"]["occupation_df"]
    assert isinstance(occupations_df, pd.DataFrame), "API extraction did not return a DataFrame."
    
    logger.info(f"Extracted DataFrame shape: {occupations_df.shape}")
    logger.info(f"Extracted DataFrame content:\n{occupations_df.to_string()}")

    assert len(occupations_df) == 1, f"Expected 1 record for {TEST_ONET_SOC_CODE}, but got {len(occupations_df)}."
    
    # Verify content of the fetched record
    if not occupations_df.empty:
        # Use .get with a default for safety, though an error here would mean API response changed or parsing failed
        actual_soc_code = occupations_df.iloc[0].get('onet_soc_code', 'MISSING_onet_soc_code') 
        actual_title = occupations_df.iloc[0].get('title', 'MISSING_title')
        logger.info(f"Found onet_soc_code: {actual_soc_code}, title: {actual_title}")
        assert actual_soc_code == TEST_ONET_SOC_CODE, f"Fetched onet_soc_code '{actual_soc_code}' does not match expected '{TEST_ONET_SOC_CODE}'."
        assert EXPECTED_TITLE_CONTAINS.lower() in actual_title.lower(), f"Fetched title '{actual_title}' does not contain expected text '{EXPECTED_TITLE_CONTAINS}'."
        assert 'last_updated' in occupations_df.columns, "DataFrame missing 'last_updated' column."
    else:
        assert False, "API extraction returned an unexpectedly empty DataFrame for a specific code."

    # Create engine for test database
    engine = get_sqlalchemy_engine(
        db_name=test_db_config['database'],
        db_user=test_db_config['user'],
        db_password=test_db_config['password'],
        db_host=test_db_config['host'],
        db_port=test_db_config['port']
    )

    # Get the table name for logging clarity
    table_name = schemas.Onet_Occupations_API_landing.__tablename__
    logger.info(f"Attempting to load occupation DataFrame into '{table_name}' table in {test_db_config['database']}...")
    
    # Optional: Clear existing data for this occupation code before loading
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        clear_stmt = text(f"DELETE FROM {table_name} WHERE onet_soc_code = :code")
        result = session.execute(clear_stmt, {"code": TEST_ONET_SOC_CODE})
        session.commit()
        logger.info(f"Cleared existing data for {TEST_ONET_SOC_CODE} from {table_name}")
    except Exception as e:
        logger.warning(f"Could not clear existing data: {str(e)}")
        session.rollback()
    finally:
        session.close()
    
    # Load the data into the test database
    load_result = load_data_from_dataframe(
        df=occupations_df,
        model=schemas.Onet_Occupations_API_landing,
        engine=engine,
        clear_existing=False  # We already cleared specific data for this occupation
    )

    records_loaded = load_result.get("result", {}).get("records_loaded", 0)
    logger.info(f"Load Occupation Data Result: Success={load_result['success']}, Message='{load_result['message']}', Records Loaded={records_loaded}")
    assert load_result["success"], f"Failed to load occupation data into database: {load_result['message']}"
    assert records_loaded == 1, f"Expected 1 record to be loaded, but {records_loaded} were."

    # Verify the loaded data
    logger.info(f"Verifying occupation data in {test_db_config['database']} database...")
    session = Session()
    try:
        # Verify count of loaded occupation for the specific onet_soc_code
        stmt_occ_count = text(f"SELECT COUNT(*) FROM {table_name} WHERE onet_soc_code = :code")
        record_count = session.execute(stmt_occ_count, {"code": TEST_ONET_SOC_CODE}).scalar_one()
        logger.info(f"Found {record_count} occupation record(s) in DB for {TEST_ONET_SOC_CODE}.")
        assert record_count == 1, f"Database occupation record count ({record_count}) for {TEST_ONET_SOC_CODE} does not match expected (1)."

        # Using text() for parameterization in read_sql is safer
        stmt = text(f"SELECT title FROM {table_name} WHERE onet_soc_code = :code")
        first_row_df = pd.read_sql(stmt, engine, params={"code": TEST_ONET_SOC_CODE})
        logger.info(f"Row from database for {TEST_ONET_SOC_CODE}:\n{first_row_df.to_string()}")
        assert not first_row_df.empty, f"No record found in DB for {TEST_ONET_SOC_CODE}"
        # Ensure title column exists before trying to access it
        assert 'title' in first_row_df.columns, "'title' column not found in DataFrame loaded from DB."
        assert EXPECTED_TITLE_CONTAINS.lower() in first_row_df.iloc[0]['title'].lower(), f"Title in DB does not contain '{EXPECTED_TITLE_CONTAINS}'"

        # Show table statistics
        stmt_table_stats = text(f"SELECT COUNT(*) as total_records FROM {table_name}")
        total_records = session.execute(stmt_table_stats).scalar_one()
        logger.info(f"Total records in {table_name}: {total_records}")

    finally:
        session.close()
        
    logger.info(f"SUMMARY: Successfully extracted and loaded 1 occupation record for {TEST_ONET_SOC_CODE} ('{EXPECTED_TITLE_CONTAINS}') into '{table_name}' in {test_db_config['database']}.")
    logger.info("Integration test for filtered occupation finished successfully.") 