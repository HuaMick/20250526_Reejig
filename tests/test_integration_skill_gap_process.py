import os
import sys
import pytest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.functions.get_occupation_skills import get_occupation_skills
from src.functions.identify_skill_gap import identify_skill_gap
from src.config.schemas import get_sqlalchemy_engine, Occupation
from sqlalchemy.orm import sessionmaker

class TestSkillGapProcess:
    """
    Integration tests for the skill gap identification process, 
    covering get_occupation_skills and identify_skill_gap.
    Assumes DB is populated and skills have relevant 'LV' scale entries for comparison.
    """

    def test_process_chemist_to_software_developer(self):
        """Test full process: Chemist to Software Developer, expecting a delta in identify_skill_gap if both have LV skills."""
        print("\nRunning test_process_chemist_to_software_developer (Scale: LV)...")
        from_code = "19-2031.00"  # Chemists
        to_code = "15-1252.00"    # Software Developers

        print(f"--- Getting skills for FROM occupation: {from_code} (Chemists) ---")
        from_skills_response = get_occupation_skills(from_code)
        assert from_skills_response["success"], f"Failed to get skills for FROM occupation {from_code}: {from_skills_response['message']}"
        assert from_skills_response["result"]["skills"], f"FROM occupation {from_code} (Chemists) should have LV skills for this test."
        print(f"Got {len(from_skills_response['result']['skills'])} LV skills for {from_skills_response['result']['occupation_title']}")

        print(f"--- Getting skills for TO occupation: {to_code} (Software Developers) ---")
        to_skills_response = get_occupation_skills(to_code)
        
        # Per user, 15-1252.00 (Software Developers) might not have LV skills in the current test DB
        if not to_skills_response["success"] and "No 'LV' scale skills found" in to_skills_response["message"]:
            print(f"TO occupation {to_code} ({to_skills_response['result'].get('occupation_title', 'Software Developers')}) has no LV skills as per DB. Test adapts.")
            # In this case, identify_skill_gap should still run. If Chemist has skills, all those skills will be 'gaps'
            # because Software Dev has nothing at LV to compare against (effectively 0 for all its skills).
            # However, our definition of a gap is "skills for occ2 not in occ1" or "higher in occ2".
            # If occ2 has no skills, there can be no such gaps.
            gap_result = identify_skill_gap(from_skills_response["result"], to_skills_response["result"])
            assert gap_result["success"], "identify_skill_gap should succeed even if one occupation has no LV skills."
            assert not gap_result["result"]["skill_gaps"], f"Expected no skill gaps when TO occupation ({to_code}) has no LV skills, but got {len(gap_result['result']['skill_gaps'])}."
            print(f"Correctly found no gaps when TO occupation ({to_code}) has no LV skills.")
            return # Test is complete for this scenario
        
        assert to_skills_response["success"], f"Failed to get skills for TO occupation {to_code}: {to_skills_response['message']}"
        assert to_skills_response["result"]["skills"], f"TO occupation {to_code} (Software Developers) must have LV skills for a meaningful gap test here."
        print(f"Got {len(to_skills_response['result']['skills'])} LV skills for {to_skills_response['result']['occupation_title']}")

        print("--- Identifying skill gap between Chemist and Software Developer ---")
        gap_result = identify_skill_gap(from_skills_response["result"], to_skills_response["result"])
        assert gap_result["success"], f"identify_skill_gap failed: {gap_result['message']}"

        skill_gaps = gap_result["result"]["skill_gaps"]
        from_title = gap_result["result"]['from_occupation_title']
        to_title = gap_result["result"]['to_occupation_title']

        if skill_gaps:
            print(f"Found {len(skill_gaps)} 'LV' skill gap(s) from '{from_title}' to '{to_title}':")
            for skill in skill_gaps:
                print(f"  - ID: {skill['element_id']}, Name: {skill['element_name']}, Scale: {skill.get('scale_id')}, From_LV: {skill['from_data_value']}, To_LV: {skill['to_data_value']}")
                assert skill.get('scale_id') == 'LV'
            assert len(skill_gaps) > 0 # Tightened assertion: Expecting a delta
        else:
            print(f"No 'LV' scale skill gaps found from '{from_title}' to '{to_title}'. This is unexpected as a delta was anticipated.")
            assert len(skill_gaps) > 0, f"Expected LV skill gaps from '{from_title}' to '{to_title}', but found none."

    def test_no_skill_gap_identical_occupations(self):
        """Test with identical occupations, expecting no LV scale gaps after skill retrieval."""
        occ_code = "19-2031.00"  # Chemists (assuming this one has LV skills for the test)
        print(f"\nRunning test_no_skill_gap_identical_occupations for {occ_code} (Scale: LV)...")

        print(f"--- Getting skills for occupation: {occ_code} (first call) ---")
        occ1_skills_response = get_occupation_skills(occ_code)
        if not occ1_skills_response["success"]:
            pytest.skip(f"Skipping test: Failed to get LV skills for primary test code {occ_code}. Message: {occ1_skills_response['message']}")
        
        # No need for a second call to get_occupation_skills for the same occ_code
        # occ2_skills_response = get_occupation_skills(occ_code)
        # assert occ2_skills_response["success"], f"Second call to get skills for {occ_code} failed: {occ2_skills_response['message']}"

        print("--- Identifying skill gap for identical occupations ---")
        gap_result = identify_skill_gap(occ1_skills_response["result"], occ1_skills_response["result"])
        assert gap_result["success"], f"identify_skill_gap failed for identical inputs: {gap_result['message']}"
        assert not gap_result["result"]["skill_gaps"], \
            f"Expected no LV skill gaps for identical occupation {occ_code}, but found {len(gap_result['result']['skill_gaps'])}"
        print(f"No 'LV' scale gap for identical occupation ({occ1_skills_response['result']['occupation_title']}) as expected.")

    def test_get_occupation_skills_not_found(self):
        """Test get_occupation_skills with a non-existent occupation code."""
        non_existent_code = "99-9999.99"
        print(f"\nRunning test_get_occupation_skills_not_found for code {non_existent_code}...")
        
        skills_response = get_occupation_skills(non_existent_code)
        assert not skills_response["success"], "Expected get_occupation_skills to fail for a non-existent code."
        assert "not found" in skills_response["message"].lower(), f"Expected 'not found' in error message, got: {skills_response['message']}"
        print(f"Correctly handled non-existent occupation code: {skills_response['message']}")

    def test_get_occupation_skills_no_lv_skills(self):
        """Test get_occupation_skills for an occupation that exists but has no 'LV' scale skills."""
        # Assuming "11-1011.00" (Chief Executives) is in DB but has no LV skills, or few enough not to be an issue.
        # This requires specific data setup or knowledge of the test DB.
        # If this code is not in your test DB or DOES have LV skills, this test might not behave as intended.
        occ_code_no_lv = "11-1011.00" # Chief Executives (example)
        print(f"\nRunning test_get_occupation_skills_no_lv_skills for {occ_code_no_lv}...")

        # First, check if the occupation itself exists to avoid conflating errors.
        temp_engine = get_sqlalchemy_engine()
        Temp_Session = sessionmaker(bind=temp_engine)
        temp_session = Temp_Session()
        occupation_exists = temp_session.query(Occupation).filter(Occupation.onet_soc_code == occ_code_no_lv).first()
        temp_session.close()

        if not occupation_exists:
            pytest.skip(f"Skipping test_get_occupation_skills_no_lv_skills: Occupation {occ_code_no_lv} not found in DB.")

        skills_response = get_occupation_skills(occ_code_no_lv)
        assert not skills_response["success"], f"Expected get_occupation_skills to return success=False for {occ_code_no_lv} if no LV skills."
        assert "No 'LV' scale skills found" in skills_response["message"], \
            f"Expected message about no LV skills for {occ_code_no_lv}, got: {skills_response['message']}"
        assert skills_response["result"]["skills"] == [], "Skills list should be empty if no LV skills found."
        assert skills_response["result"].get("occupation_title") == occupation_exists.title, "Occupation title should still be in result."
        print(f"Correctly handled occupation {occ_code_no_lv} with no LV skills: {skills_response['message']}")

# Note: The test_get_occupation_skills_no_lv_skills requires `get_sqlalchemy_engine` and `Occupation` for the pre-check.
# Ensure these are available if running this test file standalone or adjust if necessary. 