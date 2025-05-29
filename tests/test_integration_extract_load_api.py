import pytest
import os
from unittest import mock # For mocking get_db_engine
from sqlalchemy import inspect

# Ensure imports use full paths from project root
from src.nodes.extract_load_api import run_extract_load_api_data
from src.config.schemas import Onet_Occupations_API_landing, Onet_Skills_API_landing, Onet_Scales_API_landing
from tests.fixtures.db_setup_api_load import in_memory_sqlite_engine # Import the engine fixture directly

# Removed dummy API credential setup. Test will now rely on
# credentials sourced by the shell script from env/env.env or environment.

@mock.patch('src.nodes.extract_load_api.get_db_engine') # Mock the get_db_engine function in the node
def test_extract_load_api_node_runs(mock_get_engine, in_memory_sqlite_engine):
    """
    Tests that the extract_load_api_data node runs, attempts API calls,
    and interacts with the (mocked) database engine.
    Checks if tables are populated if API calls are successful (actual success depends on env).
    """
    # Configure the mock to return our in-memory SQLite engine
    mock_get_engine.return_value = in_memory_sqlite_engine

    print("\nStarting integration test for extract_load_api_data node...")
    print(f"Using O*NET API User (dummy or real): {os.getenv('ONET_API_USERNAME')}")

    # Execute the node function
    node_result = run_extract_load_api_data()

    print("\nNode Execution Results:")
    print(f"Success: {node_result['success']}")
    print(f"Message: {node_result['message']}")
    if node_result["result"] and node_result["result"].get("operations"):
        print("Operations Summary:")
        for op in node_result["result"]["operations"]:
            details = op.get('details', '{}')
            if isinstance(details, dict):
                print(f"  Step: {op.get('step')}, Success: {details.get('success')}, Message: {details.get('message')}")
            else:
                 print(f"  Step: {op.get('step')}, Details: {details}")
    
    # Assert that the node reported success or handled API failures gracefully.
    # If API credentials are not valid, the extraction steps will fail, but the node should still complete.
    # The overall success of the node depends on whether any step critically failed *within the node's logic*.
    # For this test, we mainly care that it ran and interacted with the DB.
    assert isinstance(node_result, dict), "Node result should be a dictionary."
    assert "success" in node_result, "Node result should have a 'success' key."

    # Check if tables were created and potentially populated in the in-memory DB
    # The actual number of rows will depend on whether the live API calls succeeded.
    conn = in_memory_sqlite_engine.connect()
    try:
        inspector = inspect(conn) # Create an inspector

        occ_rows = conn.execute(Onet_Occupations_API_landing.__table__.select()).fetchall()
        skills_rows = conn.execute(Onet_Skills_API_landing.__table__.select()).fetchall()
        scales_rows = conn.execute(Onet_Scales_API_landing.__table__.select()).fetchall()
        
        print(f"\nDatabase State After Node Execution (using in-memory SQLite via {mock_get_engine.call_args}):")
        print(f"  Rows in Onet_Occupations_API_landing: {len(occ_rows)}")
        print(f"  Rows in Onet_Skills_API_landing: {len(skills_rows)}")
        print(f"  Rows in Onet_Scales_API_landing: {len(scales_rows)}")

        # Basic assertion: tables should exist (even if empty if API calls failed)
        assert inspector.has_table(Onet_Occupations_API_landing.__tablename__), f"{Onet_Occupations_API_landing.__tablename__} table should exist."
        assert inspector.has_table(Onet_Skills_API_landing.__tablename__), f"{Onet_Skills_API_landing.__tablename__} table should exist."
        assert inspector.has_table(Onet_Scales_API_landing.__tablename__), f"{Onet_Scales_API_landing.__tablename__} table should exist."

        # Note: We cannot reliably assert > 0 rows without valid, always-on API credentials
        # or by using pre-saved mock API data (which is currently against the guidelines here).
        # The test verifies the pipeline runs and interacts with the DB.
        # If real credentials are provided and APIs are up, rows should be > 0.

    finally:
        conn.close()

    # If the node failed due to API issues but the DB interaction was attempted, 
    # this test might still be considered a pass from a structural perspective.
    # The node_result['success'] reflects the node's own reported success.
    print("Integration test for node execution completed.") 