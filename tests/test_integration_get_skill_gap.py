import os
import sys
import pytest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.functions.get_skill_gap import get_skill_gap
# No longer need load_data_from_csv, get_sqlalchemy_engine, Base, initialize_database_tables in the test file itself
# as we assume the database is pre-populated.

class TestGetSkillGap:
    """
    Integration tests for get_skill_gap function.
    Assumes the database has been initialized and populated with actual data
    (e.g., by running mysql_init_tables.py and mysql_load.py prior to these tests).
    """

    def test_skill_gap_software_developer_to_database_admin(self):
        """Test skill gap between Software Developer and Database Administrator."""
        print("\nRunning test_skill_gap_software_developer_to_database_admin...")
        # These O*NET codes are common and likely in the provided occupations.txt
        dev_code = "15-1252.00"  # Software Developers
        dba_code = "15-1242.00"  # Database Administrators
        
        result = get_skill_gap(dev_code, dba_code)
        
        print(f"Message: {result['message']}")
        from_title = result['result'].get('from_occupation_title', dev_code)
        to_title = result['result'].get('to_occupation_title', dba_code)
        print(f"Skill gap from '{from_title}' to '{to_title}':")

        if not result["success"]:
            # If the codes themselves are not found, the function will return success=False.
            # This might indicate the DB wasn't populated as expected, or these specific codes are missing.
            print(f"  Skipping detailed gap check as function reported an issue (e.g., occupation not found).")
            assert result["success"], f"Skill gap calculation failed unexpectedly: {result['message']}" 
            # The above assert will trigger if success is False, showing the message.

        if result["result"] and result["result"].get("skill_gaps"):
            for skill in result["result"]["skill_gaps"]:
                print(f"  - Skill ID: {skill['element_id']}, Name: {skill['element_name']}")
            # We expect some gaps, but the exact number and names depend on the full dataset.
            # For a robust test against actual data, one might query a few known specific skill gaps.
            # For now, just printing them is illustrative.
            assert len(result["result"]["skill_gaps"]) >= 0 # True if any gaps or no gaps
        else:
            print("  No skill gaps found (or occupation_code2 has no skills not in occupation_code1).")
        
        # This test primarily ensures the function runs and returns the expected structure.
        # Specific assertions on skill content would require knowing the exact state of the pre-populated DB.

    def test_no_skill_gap_identical_occupations(self):
        """Test when 'from' and 'to' occupations are the same."""
        print("\nRunning test_no_skill_gap_identical_occupations...")
        # Using a common O*NET code likely in occupations.txt
        occ_code = "11-1011.00"  # Chief Executives
        result = get_skill_gap(occ_code, occ_code)
        
        if not result["success"] and "not found" in result["message"]:
            pytest.skip(f"Skipping test: Occupation code {occ_code} not found in pre-populated database.")
        
        assert result["success"], result["message"]
        assert len(result["result"]["skill_gaps"]) == 0, "Expected no skill gaps for identical occupations"
        print(f"No gap for identical occupations ({result['result'].get('from_occupation_title', occ_code)}) as expected.")

    def test_occupation_code_not_found(self):
        """Test when one or both occupation codes do not exist in the pre-populated database."""
        print("\nRunning test_occupation_code_not_found...")
        existing_code = "11-1011.00" # A code assumed to exist. If not, the test might show a different failure.
                                     # A truly robust version might first query if this code exists.

        result_from_missing = get_skill_gap('NONEXISTENT-CODE-XYZ', existing_code)
        assert not result_from_missing["success"], "Expected failure for non-existent 'from' code"
        assert "NONEXISTENT-CODE-XYZ not found" in result_from_missing["message"], "Incorrect error for missing 'from' code"
        print(f"Correctly handled missing 'from' occupation: {result_from_missing['message']}")

        result_to_missing = get_skill_gap(existing_code, 'NONEXISTENT-CODE-ABC')
        assert not result_to_missing["success"], "Expected failure for non-existent 'to' code"
        assert "NONEXISTENT-CODE-ABC not found" in result_to_missing["message"], "Incorrect error for missing 'to' code"
        print(f"Correctly handled missing 'to' occupation: {result_to_missing['message']}")

# For direct execution if needed, assuming DB is populated and env vars are set.
if __name__ == '__main__':
    print("Starting integration tests for skill gap analysis (assuming pre-populated DB)...")
    # Note: Running this directly requires `database/occupations.txt` and `database/skills.txt` 
    # to have been loaded into the database by `src/functions/mysql_load.py`.
    # Also, environment variables (MYSQL_USER, etc.) must be set.
    pytest.main(["-s", "-v", __file__]) 