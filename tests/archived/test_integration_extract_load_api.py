import pytest
import os
from unittest import mock # For mocking get_db_engine
from sqlalchemy import inspect, text # Added text
import logging # For direct logger use
import sys # ensure sys is imported

# Ensure imports use full paths from project root
from nodes.archived.extract_load_api import run_extract_load_api_data
from src.config.schemas import Onet_Occupations_API_landing, Onet_Skills_API_landing # Removed Onet_Scales_API_landing
from tests.fixtures.db_setup_api_load import in_memory_sqlite_engine # Import the engine fixture directly

# Configure logger for this test module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr) # Assuming sys is imported if not already
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

TARGET_OCCUPATION_CODE = "15-1254.00" # Web Developers

@mock.patch('src.nodes.extract_load_api.get_db_engine') # Mock the get_db_engine function in the node
def test_extract_load_api_node_targeted(mock_get_engine, in_memory_sqlite_engine):
    """
    Tests that the extract_load_api_data node runs in targeted mode,
    fetching and loading data for a specific occupation code and its skills.
    """
    mock_get_engine.return_value = in_memory_sqlite_engine

    logger.info(f"Starting TARGETED integration test for extract_load_api_data node for OCC_CODE: {TARGET_OCCUPATION_CODE}")
    logger.info(f"Using O*NET API User: {os.getenv('ONET_USERNAME')}") # Relies on env var for real creds

    node_result = run_extract_load_api_data(target_occupation_codes=[TARGET_OCCUPATION_CODE])

    logger.info("\nNode Execution Results (Targeted):")
    logger.info(f"Success: {node_result['success']}")
    logger.info(f"Message: {node_result['message']}")
    if node_result.get("result", {}).get("operations"):
        logger.info("Operations Summary (Targeted):")
        for op in node_result["result"]["operations"]:
            details = op.get('details', {})
            log_message = details.get('message', str(details)) if isinstance(details, dict) else str(details)
            logger.info(f"  Step: {op.get('step')}, Success: {details.get('success', 'N/A') if isinstance(details, dict) else 'N/A'}, Msg: {log_message[:150]}") # Truncate long messages
    
    assert isinstance(node_result, dict), "Node result should be a dictionary."
    assert "success" in node_result, "Node result should have a 'success' key."
    # For a targeted run, we expect success if API calls for that target are okay.
    assert node_result["success"], f"Targeted node execution reported failure: {node_result['message']}"

    conn = in_memory_sqlite_engine.connect()
    try:
        inspector = inspect(conn)

        # Verify Occupations Table
        assert inspector.has_table(Onet_Occupations_API_landing.__tablename__), "Occupations landing table should exist."
        stmt_occ = text(f"SELECT * FROM {Onet_Occupations_API_landing.__tablename__} WHERE onet_soc_code = :code")
        occ_rows = conn.execute(stmt_occ, {"code": TARGET_OCCUPATION_CODE}).fetchall()
        logger.info(f"Found {len(occ_rows)} rows in Onet_Occupations_API_landing for code {TARGET_OCCUPATION_CODE}.")
        assert len(occ_rows) == 1, f"Expected 1 occupation row for {TARGET_OCCUPATION_CODE}, found {len(occ_rows)}."
        if occ_rows:
            logger.info(f"Occupation data for {TARGET_OCCUPATION_CODE}: {dict(occ_rows[0]._mapping)}")

        # Verify Skills Table
        assert inspector.has_table(Onet_Skills_API_landing.__tablename__), "Skills landing table should exist."
        stmt_skills = text(f"SELECT * FROM {Onet_Skills_API_landing.__tablename__} WHERE onetsoc_code = :code")
        skills_rows = conn.execute(stmt_skills, {"code": TARGET_OCCUPATION_CODE}).fetchall()
        logger.info(f"Found {len(skills_rows)} skill rows in Onet_Skills_API_landing for code {TARGET_OCCUPATION_CODE}.")
        # We expect skills for Web Developers. The exact number can vary, but should be > 0.
        assert len(skills_rows) > 0, f"Expected >0 skill rows for {TARGET_OCCUPATION_CODE}, found {len(skills_rows)}."
        if skills_rows:
            logger.info(f"First skill data for {TARGET_OCCUPATION_CODE}: {dict(skills_rows[0]._mapping)}")
        
        # No Scales table to check

    finally:
        conn.close()

    logger.info("Targeted integration test for node execution completed.") 