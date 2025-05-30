import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys

# Ensure imports use full paths from project root
from src.functions.onet_api_extract_skills import onet_api_extract_skills
from src.functions.mysql_load_table import load_data_from_dataframe
import src.config.schemas as schemas

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

def test_extract_and_load_filtered_api_skills():
    """
    Integration test for extracting O*NET API skills data for a specific onet_soc_code
    (using the generic /ws/database/rows/skills endpoint with filters)
    and loading it into the Onet_Skills_API_landing table.
    Uses an in-memory SQLite database for testing.
    """
    logger.info(f"Starting integration test for filtered skills: {TEST_ONET_SOC_CODE}")

    onet_username = os.getenv("ONET_USERNAME")
    onet_password = os.getenv("ONET_PASSWORD")

    assert onet_username, "ONET_USERNAME environment variable not set."
    assert onet_password, "ONET_PASSWORD environment variable not set."
    logger.info("Successfully retrieved O*NET API credentials.")

    # Define filter for the specific occupation code
    filter_list = [f"onetsoc_code.eq.{TEST_ONET_SOC_CODE}"]
    logger.info(f"Attempting to extract O*NET skills data from generic API with filter: {filter_list}...")
    
    api_extraction_result = onet_api_extract_skills(
        username=onet_username, 
        password=onet_password,
        filter_params=filter_list
    )
    
    logger.info(f"API Skills Extraction Result: Success={api_extraction_result['success']}, Message='{api_extraction_result['message']}'")
    assert api_extraction_result["success"], f"O*NET API skills extraction failed: {api_extraction_result['message']}"
    
    skills_df = api_extraction_result["result"]["skills_df"]
    assert isinstance(skills_df, pd.DataFrame), "API skills extraction did not return a DataFrame."
    
    logger.info(f"Extracted skills DataFrame shape: {skills_df.shape}")
    if not skills_df.empty:
        logger.info(f"Extracted skills DataFrame content (first 5 rows):\n{skills_df.head().to_string()}")
        assert not skills_df[skills_df['onetsoc_code'] == TEST_ONET_SOC_CODE].empty, f"Expected skills for {TEST_ONET_SOC_CODE}"
    else:
        # This might be acceptable if an occupation truly has no skills listed via this endpoint, 
        # but for Web Developers, we expect skills.
        logger.warning(f"API skills extraction returned an empty DataFrame for {TEST_ONET_SOC_CODE}. This might be unexpected.")

    # We expect at least one skill for Web Developers
    assert not skills_df.empty, f"Expected skills for {TEST_ONET_SOC_CODE}, but got an empty DataFrame."
    assert len(skills_df) > 0, f"Expected >0 skill records for {TEST_ONET_SOC_CODE}, got {len(skills_df)}."

    logger.info("Setting up in-memory SQLite database and creating table...")
    engine = create_engine("sqlite:///:memory:")
    schemas.Base.metadata.create_all(engine) # Create all tables defined in schemas
    logger.info(f"Table '{schemas.Onet_Skills_API_landing.__tablename__}' created in in-memory SQLite database.")

    logger.info(f"Attempting to load skills DataFrame into '{schemas.Onet_Skills_API_landing.__tablename__}' table...")
    
    load_result = load_data_from_dataframe(
        df=skills_df,
        model=schemas.Onet_Skills_API_landing,
        engine=engine,
        clear_existing=True 
    )

    records_loaded = load_result.get("result", {}).get("records_loaded", 0)
    logger.info(f"Load Skills Data Result: Success={load_result['success']}, Message='{load_result['message']}', Records Loaded={records_loaded}")
    assert load_result["success"], f"Failed to load skills data into database: {load_result['message']}"
    assert records_loaded == len(skills_df), f"Number of skills records loaded ({records_loaded}) does not match expected ({len(skills_df)})."

    logger.info("Verifying skills data in the in-memory database...")
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Verify count of loaded skills for the specific onet_soc_code
        stmt_skills_count = text(f"SELECT COUNT(*) FROM {schemas.Onet_Skills_API_landing.__tablename__} WHERE onetsoc_code = :code")
        record_count = session.execute(stmt_skills_count, {"code": TEST_ONET_SOC_CODE}).scalar_one()
        logger.info(f"Found {record_count} skill records in DB for {TEST_ONET_SOC_CODE}.")
        assert record_count == len(skills_df), f"Database skill record count ({record_count}) for {TEST_ONET_SOC_CODE} does not match expected ({len(skills_df)})."

        if not skills_df.empty:
            # Fetch a sample row to check some values
            stmt_sample_skill = text(f"SELECT onetsoc_code, element_id, element_name, scale_id, data_value FROM {schemas.Onet_Skills_API_landing.__tablename__} WHERE onetsoc_code = :code LIMIT 1")
            sample_skill_from_db = pd.read_sql(stmt_sample_skill, engine, params={"code": TEST_ONET_SOC_CODE})
            logger.info(f"Sample skill row from database for {TEST_ONET_SOC_CODE}:\n{sample_skill_from_db.to_string()}")
            assert not sample_skill_from_db.empty, f"No skill record found in DB for {TEST_ONET_SOC_CODE} during sample fetch."
            assert sample_skill_from_db.iloc[0]['onetsoc_code'] == TEST_ONET_SOC_CODE
            assert sample_skill_from_db.iloc[0]['element_id'] is not None # Basic check

    finally:
        session.close()
        
    logger.info(f"SUMMARY: Successfully extracted and loaded {len(skills_df)} skills for {TEST_ONET_SOC_CODE} into '{schemas.Onet_Skills_API_landing.__tablename__}'.")
    logger.info("Integration test for filtered skills finished successfully.") 