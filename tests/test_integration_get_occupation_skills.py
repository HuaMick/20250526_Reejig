import os
import sys
import pytest
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.functions.get_occupation_skills import get_occupation_skills
from src.functions.mysql_query import mysql_query
from src.config.schemas import get_sqlalchemy_engine
from tests.fixtures.db_config import test_db_config

def test_get_occupation_skills(test_db_config):
    """
    Integration test for the get_occupation_skills function that retrieves skills data 
    for a specific occupation code from the database.
    
    This test:
    1. Verifies the database contains necessary tables and data
    2. Calls get_occupation_skills for Environmental Scientists
    3. Validates the structure and content of the returned data
    """
    print(f"\nUsing test database: {test_db_config['database']}")
    
    # Create a SQLAlchemy engine from the test_db_config
    engine = get_sqlalchemy_engine(
        db_name=test_db_config['database'],
        db_user=test_db_config['user'],
        db_password=test_db_config['password'],
        db_host=test_db_config['host'],
        db_port=test_db_config['port']
    )
    
    # Create a session for database queries
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Debug: Check tables first
    print("\nAvailable Tables:")
    try:
        tables_query = text("SHOW TABLES;")
        tables_result = session.execute(tables_query)
        for row in tables_result:
            print(f"- {row[0]}")
    except Exception as e:
        print(f"Error querying tables: {str(e)}")
    
    # Debug: Check if we have any skills data
    print("\nSkills Data Check:")
    try:
        skills_check_query = text("""
            SELECT os.*, s.element_name 
            FROM occupation_skills os
            JOIN skills s ON s.element_id = os.element_id
            WHERE os.onet_soc_code = '19-2031.00'
            LIMIT 5;
        """)
        skills_check_result = session.execute(skills_check_query)
        
        print("First 5 skills:")
        for row in skills_check_result:
            print(row)
    except Exception as e:
        print(f"Error querying skills data: {str(e)}")
    finally:
        session.close()
    
    # Test for Environmental Scientists (19-2031.00)
    occupation_code = "19-2031.00"
    
    # Execute test operation
    result = get_occupation_skills(occupation_code, engine=engine)
    
    # Print results for verification
    print("\nIntegration Test Results:")
    print(f"Occupation Code: {occupation_code}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Occupation Title: {result['result'].get('occupation_title', 'N/A')}")
        print(f"Number of skills found: {len(result['result'].get('skills', []))}")
        print("\nTop 5 skills:")
        for skill in result['result'].get('skills', [])[:5]:
            print(f"- {skill['element_name']} (Score: {skill['data_value']})")
    
    # Assertions to verify the results
    assert result["success"] == True, f"Operation failed: {result['message']}"
    assert result["result"]["occupation_title"] is not None, "Expected occupation title to be present"
    assert len(result["result"]["skills"]) > 0, "Expected non-empty skills list"
    
    # Verify data structure of returned skills
    if result["success"] and result["result"]["skills"]:
        skill = result["result"]["skills"][0]
        assert "element_id" in skill, "Expected element_id in skill data"
        assert "element_name" in skill, "Expected element_name in skill data"
        assert "data_value" in skill, "Expected data_value in skill data" 