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
from src.config.schemas import get_sqlalchemy_engine, Onet_Occupations_API_landing, Onet_Skills_API_landing, Base

TARGET_ONET_SOC_CODE = "11-2021.00" # Marketing Managers
EXPECTED_OCCUPATION_NAME = "Marketing Managers"

@pytest.fixture(scope="module")
def db_engine():
    """Provides a SQLAlchemy engine for the test module. Assumes DB is running."""
    # Ensure environment variables for DB connection are set (e.g., from env/env.env)
    # This should be handled by the test execution script.
    if not os.getenv("MYSQL_USER") or not os.getenv("MYSQL_PASSWORD") or not os.getenv("MYSQL_DATABASE"):
        pytest.fail("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE env vars are required.")
    engine = get_sqlalchemy_engine()
    # Ensure all tables are created (idempotent)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function") # Use function scope to ensure clean state for API landing tables per test
def db_session(db_engine):
    """Provides a DB session and handles cleanup of API landing tables for the target code."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        # Clean up any pre-existing data for TARGET_ONET_SOC_CODE in API landing tables
        # This ensures we are testing the load from API aspect correctly.
        session.query(Onet_Occupations_API_landing).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).delete()
        # For Onet_Skills_API_landing, the link to occupation is via onetsoc_code column in the DataFrame before load
        # Assuming skills_df loaded into Onet_Skills_API_landing has an 'onetsoc_code' column that can be filtered on
        # (onet_api_extract_skills populates this in its returned DataFrame)
        # Direct filtering on a column named 'onetsoc_code' if it exists in Onet_Skills_API_landing schema or was added:
        # The current Onet_Skills_API_landing schema has element_id as primary, and onetsoc_code as indexed.
        session.query(Onet_Skills_API_landing).filter(Onet_Skills_API_landing.onetsoc_code == TARGET_ONET_SOC_CODE).delete()
        session.commit()
        yield session
    finally:
        # Optional: Clean up again after test if desired, or leave for inspection
        # session.query(Onet_Occupations_API_landing).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).delete()
        # session.query(Onet_Skills_API_landing).filter(Onet_Skills_API_landing.onetsoc_code == TARGET_ONET_SOC_CODE).delete()
        # session.commit()
        session.close()

def test_get_occupation_and_skills_api_fallback(db_engine, db_session):
    """
    Tests that get_occupation_and_skills correctly fetches data from the O*NET API
    if it's not found locally, and then loads it into the API landing tables.
    Assumes that data for TARGET_ONET_SOC_CODE is NOT in Onet_Occupations_Landing or Occupation_Skills tables.
    """
    print(f"\n--- Testing get_occupation_and_skills for {TARGET_ONET_SOC_CODE} with API fallback ---")

    # Ensure O*NET API credentials are set for the test environment
    if not os.getenv("ONET_USERNAME") or not os.getenv("ONET_PASSWORD"):
        pytest.fail("ONET_USERNAME and ONET_PASSWORD environment variables must be set.")

    # Call the function under test
    result = get_occupation_and_skills(occupation_code=TARGET_ONET_SOC_CODE)

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
    
    # Check Onet_Occupations_API_landing
    occupation_in_api_landing = db_session.query(Onet_Occupations_API_landing).filter_by(onet_soc_code=TARGET_ONET_SOC_CODE).first()
    assert occupation_in_api_landing is not None, f"Occupation {TARGET_ONET_SOC_CODE} not found in Onet_Occupations_API_landing after API call."
    assert occupation_in_api_landing.title.lower() == EXPECTED_OCCUPATION_NAME.lower(), "Occupation title in API landing table mismatch."
    print(f"Verified: Occupation '{occupation_in_api_landing.title}' found in Onet_Occupations_API_landing.")

    # Check Onet_Skills_API_landing
    # The onet_api_extract_skills function structures its output DataFrame with an onetsoc_code column.
    # The Onet_Skills_API_landing schema has an onetsoc_code column that should be populated by load_data_from_dataframe.
    skills_in_api_landing_count = db_session.query(Onet_Skills_API_landing).filter(Onet_Skills_API_landing.onetsoc_code == TARGET_ONET_SOC_CODE).count()
    assert skills_in_api_landing_count > 0, f"No skills for {TARGET_ONET_SOC_CODE} found in Onet_Skills_API_landing after API call."
    print(f"Verified: {skills_in_api_landing_count} skills for occupation {TARGET_ONET_SOC_CODE} found in Onet_Skills_API_landing.")
    
    first_skill_db = db_session.query(Onet_Skills_API_landing).filter(Onet_Skills_API_landing.onetsoc_code == TARGET_ONET_SOC_CODE).first()
    assert first_skill_db.element_id == first_skill["skill_element_id"], "First skill element_id mismatch in DB"
    # Note: Proficiency level (data_value) check might need care due to type (Decimal vs float)

    print(f"\nIntegration test for get_occupation_and_skills with API fallback for {TARGET_ONET_SOC_CODE} PASSED.")

# To run this test:
# 1. Ensure your MySQL database is running and accessible.
# 2. Ensure ONET_USERNAME and ONET_PASSWORD are in your env/env.env file.
# 3. Ensure data for "11-2021.00" is NOT in Onet_Occupations_Landing or Occupation_Skills tables.
#    (The user query stated these deletes were executed).
# 4. The fixture db_session will attempt to clear this code from API landing tables before each test run.
# 5. Execute via: ./src/scripts/test_integration_get_occupation_and_skills_with_api_fallback.sh (once created) 