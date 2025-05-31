"""
Integration test for the get_occupation_and_skills function,
focusing on the core functionality to retrieve occupation and skills data from local database.
"""
import pytest
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.functions.get_occupation_and_skills import get_occupation_and_skills
from src.config.schemas import get_sqlalchemy_engine, Onet_Occupations_Landing, Occupation_Skills, Skills
from tests.fixtures.db_config import test_db_config

TARGET_ONET_SOC_CODE = "11-1011.00"  # Chief Executives
EXPECTED_OCCUPATION_NAME = "Chief Executives"

def test_get_occupation_and_skills(test_db_config):
    """
    Tests that get_occupation_and_skills correctly retrieves occupation and skills data
    from the local database. Assumes that data for TARGET_ONET_SOC_CODE exists in 
    Onet_Occupations_Landing and Occupation_Skills tables.
    """
    print(f"\n--- Testing get_occupation_and_skills for {TARGET_ONET_SOC_CODE} ---")

    engine = get_sqlalchemy_engine(
        db_name=test_db_config['database'],
        db_user=test_db_config['user'],
        db_password=test_db_config['password'],
        db_host=test_db_config['host'],
        db_port=test_db_config['port']
    )
    db_engine = engine

    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Verify that the target occupation exists in the database
    occupation_check = session.query(Onet_Occupations_Landing).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).first()
    
    if occupation_check is None:
        pytest.skip(f"Test occupation {TARGET_ONET_SOC_CODE} does not exist in Onet_Occupations_Landing. This test requires pre-existing data.")
    
    print(f"Verified: Occupation {TARGET_ONET_SOC_CODE} - '{occupation_check.title}' exists in Onet_Occupations_Landing")
    
    # Verify that skills exist for this occupation
    skills_count = session.query(Occupation_Skills).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).count()
    if skills_count == 0:
        pytest.skip(f"No skills found for occupation {TARGET_ONET_SOC_CODE}. This test requires pre-existing skills data.")
    
    print(f"Verified: {skills_count} skills found for occupation {TARGET_ONET_SOC_CODE}")
    session.close()

    # Call the function under test
    result = get_occupation_and_skills(occupation_code=TARGET_ONET_SOC_CODE, engine=db_engine)

    print("\n--- get_occupation_and_skills function result ---")
    print(json.dumps(result, indent=2, default=str))

    assert result["success"], f"get_occupation_and_skills failed: {result['message']}"
    assert "result" in result and "occupation_data" in result["result"], "Result structure is missing occupation_data"
    
    occupation_data = result["result"]["occupation_data"]
    assert occupation_data.get("onet_id") == TARGET_ONET_SOC_CODE, "O*NET ID mismatch"
    assert EXPECTED_OCCUPATION_NAME.lower() in occupation_data.get("name", "").lower(), \
        f"Expected occupation name '{EXPECTED_OCCUPATION_NAME}', got '{occupation_data.get('name')}'"
    
    assert "skills" in occupation_data, "Skills key missing in occupation_data"
    assert isinstance(occupation_data["skills"], list), "Skills should be a list"
    assert len(occupation_data["skills"]) > 0, f"Expected skills for {TARGET_ONET_SOC_CODE}, but got an empty list."
    
    first_skill = occupation_data["skills"][0]
    assert "skill_element_id" in first_skill
    assert "skill_name" in first_skill
    assert "proficiency_level" in first_skill
    print(f"Sample skill found: {first_skill['skill_name']} (Element ID: {first_skill['skill_element_id']}, Proficiency: {first_skill['proficiency_level']}) ")
    
    print(f"\nIntegration test for get_occupation_and_skills for {TARGET_ONET_SOC_CODE} PASSED.")

# To run this test:
# 1. Ensure your MySQL database is running and accessible.
# 2. The test assumes that data for TARGET_ONET_SOC_CODE already exists in the database.
# 3. Execute via: ./tests/test_integration_get_occupation_and_skills.sh