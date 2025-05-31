"""
Integration test for the get_occupation_and_skills function,
focusing on its ability to fall back to O*NET API calls and load data if not found locally.
"""
import os
import pytest
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.functions.get_occupation_and_skills import get_occupation_and_skills
from src.config.schemas import get_sqlalchemy_engine, Onet_Occupations_API_landing, Onet_Skills_API_landing, Onet_Occupations_Landing, Occupation_Skills, Base
from tests.fixtures.db_config import test_db_config

TARGET_ONET_SOC_CODE = "11-2021.00" # Marketing Managers
EXPECTED_OCCUPATION_NAME = "Marketing Managers"

def test_get_occupation_and_skills_api_fallback(test_db_config):
    """
    Tests that get_occupation_and_skills correctly fetches data from the O*NET API
    if it's not found locally, and then loads it into the API landing tables.
    Assumes that data for TARGET_ONET_SOC_CODE is NOT in Onet_Occupations_Landing or Occupation_Skills tables.
    """
    print(f"\n--- Testing get_occupation_and_skills for {TARGET_ONET_SOC_CODE} with API fallback ---")

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

    # Clean up any pre-existing data for TARGET_ONET_SOC_CODE in API landing tables
    # This ensures we are testing the load from API aspect correctly.
    session.query(Onet_Occupations_API_landing).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).delete()
    
    # Clean up data in the Onet_Occupations_Landing table to ensure API fallback is triggered
    deleted_rows = session.query(Onet_Occupations_Landing).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).delete()
    print(f"Deleted {deleted_rows} rows from Onet_Occupations_Landing for {TARGET_ONET_SOC_CODE}")
    
    # Clean up any occupation-skill relationships for this occupation
    deleted_skills = session.query(Occupation_Skills).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).delete()
    print(f"Deleted {deleted_skills} rows from Occupation_Skills for {TARGET_ONET_SOC_CODE}")
    
    # For Onet_Skills_API_landing, the link to occupation is via onetsoc_code column in the DataFrame before load
    session.query(Onet_Skills_API_landing).filter(Onet_Skills_API_landing.onetsoc_code == TARGET_ONET_SOC_CODE).delete()
    
    session.commit()
    session.close()

    session = sessionmaker(bind=db_engine)
    session = Session()
    # Verify the occupation has been removed from the landing table
    occupation_check = session.query(Onet_Occupations_Landing).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).first()
    assert occupation_check is None, f"Target occupation {TARGET_ONET_SOC_CODE} still exists in Onet_Occupations_Landing, test prerequisite not met"
    print(f"Verified: Occupation {TARGET_ONET_SOC_CODE} not present in Onet_Occupations_Landing")
    
    # Ensure O*NET API credentials are set for the test environment
    if not os.getenv("ONET_USERNAME") or not os.getenv("ONET_PASSWORD"):
        pytest.fail("ONET_USERNAME and ONET_PASSWORD environment variables must be set.")

    # Call the function under test with the test database engine
    result = get_occupation_and_skills(occupation_code=TARGET_ONET_SOC_CODE, engine=db_engine)

    print("\n--- get_occupation_and_skills function result ---")
    print(json.dumps(result, indent=2, default=str))

    assert result["success"], f"get_occupation_and_skills failed: {result['message']}"
    assert "result" in result and "occupation_data" in result["result"], "Result structure is missing occupation_data"
    
    occupation_data = result["result"]["occupation_data"]
    assert occupation_data.get("onet_id") == TARGET_ONET_SOC_CODE, "O*NET ID mismatch"
    assert EXPECTED_OCCUPATION_NAME.lower() in occupation_data.get("name", "").lower(), \
        f"Expected occupation name '{EXPECTED_OCCUPATION_NAME}', got '{occupation_data.get("name")}'"
    
    assert "skills" in occupation_data, "Skills key missing in occupation_data"
    assert isinstance(occupation_data["skills"], list), "Skills should be a list"
    # We expect skills to be fetched from API for Marketing Managers
    assert len(occupation_data["skills"]) > 0, f"Expected skills for {TARGET_ONET_SOC_CODE}, but got an empty list."
    
    first_skill = occupation_data["skills"][0]
    assert "skill_element_id" in first_skill
    assert "skill_name" in first_skill
    assert "proficiency_level" in first_skill
    print(f"Sample skill found via API: {first_skill['skill_name']} (Element ID: {first_skill['skill_element_id']}, Proficiency: {first_skill['proficiency_level']}) ")
    # Verify that data was loaded into the API landing tables
    print(f"\n--- Verifying data loaded into API landing tables for {TARGET_ONET_SOC_CODE} ---")
    session.close()

    session = sessionmaker(bind=db_engine)
    session = Session()
    # Check Onet_Occupations_API_landing
    occupation_in_api_landing = session.query(Onet_Occupations_API_landing).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).first()
    print(f"Checking Onet_Occupations_API_landing in database: {db_engine.url.database}")
    print(f"occupation_in_api_landing: {occupation_in_api_landing}")
    assert occupation_in_api_landing is not None, f"Occupation {TARGET_ONET_SOC_CODE} not found in Onet_Occupations_API_landing after API call."
    assert occupation_in_api_landing.title.lower() == EXPECTED_OCCUPATION_NAME.lower(), "Occupation title in API landing table mismatch."
    print(f"Verified: Occupation '{occupation_in_api_landing.title}' found in Onet_Occupations_API_landing.")

    # Check Onet_Skills_API_landing
    # The onet_api_extract_skills function structures its output DataFrame with an onetsoc_code column.
    # The Onet_Skills_API_landing schema has an onetsoc_code column that should be populated by load_data_from_dataframe.
    skills_in_api_landing_count = session.query(Onet_Skills_API_landing).filter(Onet_Skills_API_landing.onetsoc_code == TARGET_ONET_SOC_CODE).count()
    assert skills_in_api_landing_count > 0, f"No skills for {TARGET_ONET_SOC_CODE} found in Onet_Skills_API_landing after API call."
    print(f"Verified: {skills_in_api_landing_count} skills for occupation {TARGET_ONET_SOC_CODE} found in Onet_Skills_API_landing.")
    
    first_skill_db = session.query(Onet_Skills_API_landing).filter(Onet_Skills_API_landing.onetsoc_code == TARGET_ONET_SOC_CODE).first()
    assert first_skill_db.element_id == first_skill["skill_element_id"], "First skill element_id mismatch in DB"
    # Note: Proficiency level (data_value) check might need care due to type (Decimal vs float)
    session.close()
    print(f"\nIntegration test for get_occupation_and_skills with API fallback for {TARGET_ONET_SOC_CODE} PASSED.")

# To run this test:
# 1. Ensure your MySQL database is running and accessible.
# 2. Ensure ONET_USERNAME and ONET_PASSWORD are in your env/env.env file.
# 3. The test will automatically delete any existing data for the target occupation from:
#    - Onet_Occupations_Landing
#    - Occupation_Skills
#    - Onet_Occupations_API_landing
#    - Onet_Skills_API_landing
# 4. Execute via: ./tests/test_integration_get_occupation_and_skills_api_fallback.sh 