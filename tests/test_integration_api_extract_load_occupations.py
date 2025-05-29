import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from functions.onet_api_extract_occupation import onet_api_extract_occupation
from src.functions.mysql_load_table import load_data_from_dataframe
import src.config.schemas as schemas # To access the model and Base

# Configure logging for the test
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')

def test_extract_and_load_api_occupations():
    """
    Integration test for extracting O*NET API occupation data 
    and loading it into the Onet_Occupations_API_landing table.
    Uses an in-memory SQLite database for testing.
    """
    logger.info("Starting integration test: test_extract_and_load_api_occupations")

    # 1. Get API Credentials
    onet_username = os.getenv("ONET_USERNAME")
    onet_password = os.getenv("ONET_PASSWORD")

    assert onet_username, "ONET_USERNAME environment variable not set."
    assert onet_password, "ONET_PASSWORD environment variable not set."
    logger.info("Successfully retrieved O*NET API credentials.")

    # 2. Extract data from O*NET API
    logger.info("Attempting to extract O*NET occupation data from API...")
    api_extraction_result = onet_api_extract_occupation(username=onet_username, password=onet_password)
    
    logger.info(f"API Extraction Result: Success={api_extraction_result['success']}, Message='{api_extraction_result['message']}'")
    assert api_extraction_result["success"], f"O*NET API extraction failed: {api_extraction_result['message']}"
    
    occupations_df = api_extraction_result["result"]
    assert isinstance(occupations_df, pd.DataFrame), "API extraction did not return a DataFrame."
    
    if occupations_df.empty:
        logger.warning("API extraction returned an empty DataFrame. Test will proceed but no data will be loaded.")
        # Depending on requirements, you might assert not occupations_df.empty here.
        # For now, we'll allow it and check loading an empty DF.
    else:
        logger.info(f"Successfully extracted {len(occupations_df)} occupation records from API.")
        logger.info(f"DataFrame columns: {occupations_df.columns.tolist()}")
        logger.info(f"DataFrame head:\n{occupations_df.head().to_string()}")
        assert 'onet_soc_code' in occupations_df.columns, "DataFrame missing 'onet_soc_code' column."
        assert 'title' in occupations_df.columns, "DataFrame missing 'title' column."
        assert 'last_updated' in occupations_df.columns, "DataFrame missing 'last_updated' column."


    # 3. Setup in-memory SQLite database and create table
    logger.info("Setting up in-memory SQLite database and creating table...")
    engine = create_engine("sqlite:///:memory:")
    schemas.Base.metadata.create_all(engine) # Create all tables defined in schemas using the Base
    logger.info(f"Table '{schemas.Onet_Occupations_API_landing.__tablename__}' created in in-memory SQLite database.")

    # 4. Load data into the database
    logger.info(f"Attempting to load DataFrame into '{schemas.Onet_Occupations_API_landing.__tablename__}' table...")
    logger.info(f"DataFrame to load (first 5 rows if not empty):\n{occupations_df.head().to_string() if not occupations_df.empty else 'Empty DataFrame'}")
    
    load_result = load_data_from_dataframe(
        df=occupations_df,
        model=schemas.Onet_Occupations_API_landing,
        engine=engine,
        clear_existing=True 
    )

    logger.info(f"Load Data Result: Success={load_result['success']}, Message='{load_result['message']}', Records Loaded={load_result.get('result', {}).get('records_loaded')}")
    assert load_result["success"], f"Failed to load data into database: {load_result['message']}"

    expected_records = len(occupations_df)
    assert load_result.get("result", {}).get("records_loaded") == expected_records, \
        f"Number of records loaded ({load_result.get('result', {}).get('records_loaded')}) " \
        f"does not match expected ({expected_records})."

    # 5. Verify data in the database (optional, but good for confidence)
    if not occupations_df.empty:
        logger.info("Verifying data in the in-memory database...")
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            count_query = text(f"SELECT COUNT(*) FROM {schemas.Onet_Occupations_API_landing.__tablename__}")
            record_count = session.execute(count_query).scalar_one()
            logger.info(f"Found {record_count} records in '{schemas.Onet_Occupations_API_landing.__tablename__}' table after load.")
            assert record_count == expected_records, \
                f"Database record count ({record_count}) does not match expected ({expected_records}) after load."

            # Fetch a sample row if data exists
            first_row_df = pd.read_sql(f"SELECT * FROM {schemas.Onet_Occupations_API_landing.__tablename__} LIMIT 1", engine)
            logger.info(f"Sample row from database:\n{first_row_df.to_string()}")

        finally:
            session.close()
    else:
        logger.info("Skipping database verification as input DataFrame was empty.")
        
    logger.info("Integration test: test_extract_and_load_api_occupations finished successfully.") 