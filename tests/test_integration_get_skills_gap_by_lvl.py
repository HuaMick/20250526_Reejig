import os
import sys
import pytest

# Add the parent directory to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.functions.get_skills_gap_by_lvl import get_skills_gap_by_lvl
from src.config.schemas import get_sqlalchemy_engine
from tests.fixtures.db_config import test_db_config

def test_get_skills_gap_by_lvl_successful(check_api_credentials, test_db_config):
    """Test the get_skills_gap_by_lvl function with valid occupation codes that should have skill gaps."""
    # Using occupation codes identified by the user as having different skills after filtering level=0
    from_occupation = "11-1011.00"  # Chief Executives (32 skills with level > 0)
    to_occupation = "11-2021.00"    # Marketing Managers (29 skills with level > 0)
    
    # Print database being used for debugging
    print(f"\nUsing database: {os.environ.get('MYSQL_DATABASE')}")

    engine = get_sqlalchemy_engine(
        db_name=test_db_config['database'],
        db_user=test_db_config['user'],
        db_password=test_db_config['password'],
        db_host=test_db_config['host'],
        db_port=test_db_config['port']
    )
    
    # Use the test database engine explicitly
    result = get_skills_gap_by_lvl(from_occupation, to_occupation, engine=engine)
    
    # Print results for verification
    print("\nIntegration Test Results - Skills Gap Analysis with Proficiency Levels:")
    print(f"From: {result['result']['from_occupation_title']} ({from_occupation})")
    print(f"To: {result['result']['to_occupation_title']} ({to_occupation})")
    print(f"Number of skill gaps identified: {len(result['result']['skill_gaps'])}")
    
    if result['result']['skill_gaps']:
        sample_gaps = result['result']['skill_gaps'][:3]
        print("\nSample skill gaps with proficiency levels:")
        for gap in sample_gaps:
            print(f"- {gap['element_name']}: From Level: {gap['from_data_value']}, To Level: {gap['to_data_value']}")
    
    # Assertions to verify the results
    assert result["success"], f"Function failed: {result['message']}"
    assert "from_occupation_title" in result["result"], "Missing 'from_occupation_title' in result"
    assert "to_occupation_title" in result["result"], "Missing 'to_occupation_title' in result"
    assert "skill_gaps" in result["result"], "Missing 'skill_gaps' in result"
    
    # Verify skill_gaps contains the expected structure with proficiency levels
    for gap in result["result"]["skill_gaps"]:
        assert "element_id" in gap, "Missing 'element_id' in skill gap"
        assert "element_name" in gap, "Missing 'element_name' in skill gap"
        assert "from_data_value" in gap, "Missing 'from_data_value' in skill gap"
        assert "to_data_value" in gap, "Missing 'to_data_value' in skill gap"
        assert gap["to_data_value"] > gap["from_data_value"], f"Expected higher proficiency in target occupation for {gap['element_name']}"
