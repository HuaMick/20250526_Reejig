import os
import sys
import pytest
from sqlalchemy import inspect, text

# Add the parent directory to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.functions.mysql_init_tables import initialize_database_tables
from src.config.schemas import get_sqlalchemy_engine
from tests.fixtures.db_config import test_db_config

def test_initialize_database_tables(test_db_config):
    """Test the initialize_database_tables function to ensure it correctly creates tables."""
    # Print database being used for debugging
    print(f"\nUsing database: {test_db_config['database']}")
    
    # Create a SQLAlchemy engine from the test_db_config
    engine = get_sqlalchemy_engine(
        db_name=test_db_config['database'],
        db_user=test_db_config['user'],
        db_password=test_db_config['password'],
        db_host=test_db_config['host'],
        db_port=test_db_config['port']
    )
    
    # Run the initialization function
    result = initialize_database_tables(engine=engine)
    
    # Print results for verification
    print("\nIntegration Test Results - Database Initialization:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Verify tables were created
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    print(f"\nTables created in database ({len(table_names)} total):")
    for table_name in sorted(table_names):
        print(f"- {table_name}")
        
        # Get column information for each table
        columns = inspector.get_columns(table_name)
        print(f"  Columns: {len(columns)}")
    
    # Assertions to verify the results
    assert result["success"], f"Database initialization failed: {result['message']}"
    assert len(table_names) > 0, "No tables were created in the database"
    
    # Check that all expected tables exist
    expected_tables = [
        'llm_skill_proficiency_replies',
        'llm_skill_proficiency_requests',
        'occupation_skills',
        'onet_occupations_api_landing',
        'onet_occupations_landing',
        'onet_skills_api_landing',
        'onet_skills_landing',
        'skills'
    ]
    
    for table in expected_tables:
        assert table in table_names, f"Expected table '{table}' was not created"
    
    # Verify connection can execute a query (optional)
    with engine.connect() as connection:
        try:
            connection.execute(text("SELECT 1"))
            print("\nDatabase connection is functioning correctly.")
        except Exception as e:
            assert False, f"Database connection test failed: {str(e)}"
