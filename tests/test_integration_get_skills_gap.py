import os
import sys
import pytest

# Add the parent directory to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.functions.get_skills_gap import get_skills_gap
from src.config.schemas import get_sqlalchemy_engine
from tests.fixtures.db_config import test_db_config

@pytest.fixture(scope="module")
def check_api_credentials():
    """Fixture to check if O*NET API credentials are set"""
    if not os.getenv("ONET_USERNAME") or not os.getenv("ONET_PASSWORD"):
        pytest.skip("O*NET API credentials not set, skipping tests that require API fallback")

def test_get_skills_gap_successful(check_api_credentials, test_db_config):
    """Test the get_skills_gap function with valid occupation codes that should have skill gaps."""
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
    result = get_skills_gap(from_occupation, to_occupation, engine=engine)
    
    # Print results for verification
    print("\nIntegration Test Results - Skills Gap Analysis:")
    print(f"From: {result['result']['from_occupation_title']} ({from_occupation})")
    print(f"To: {result['result']['to_occupation_title']} ({to_occupation})")
    print(f"Number of skill gaps identified: {len(result['result']['skill_gaps'])}")
    
    if result['result']['skill_gaps']:
        print(f"Sample skill gaps: {', '.join(result['result']['skill_gaps'][:3])}...")
    
    # Assertions to verify the results
    assert result["success"], f"Function failed: {result['message']}"
    assert "from_occupation_title" in result["result"], "Missing 'from_occupation_title' in result"
    assert "to_occupation_title" in result["result"], "Missing 'to_occupation_title' in result"
    assert "skill_gaps" in result["result"], "Missing 'skill_gaps' in result"
    
    # Verify skill_gaps contains strings (skill names)
    for skill in result["result"]["skill_gaps"]:
        assert isinstance(skill, str), f"Expected skill name to be a string, got {type(skill)}"
