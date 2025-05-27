import os
import sys
import pytest
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.functions.get_skill_gap import get_skill_gap
from src.functions.mysql_load import load_data_from_csv
from src.config.schemas import get_sqlalchemy_engine, Base
from src.functions.mysql_init_tables import initialize_database_tables

@pytest.fixture(scope="class")
def skill_gap_db_setup(request):
    """Set up a test database with controlled data for skill gap analysis for the class."""
    print("Setting up TestGetSkillGap class with pytest fixture...")
    engine = get_sqlalchemy_engine()
    request.cls.engine = engine

    init_result = initialize_database_tables()
    if not init_result["success"]:
        pytest.fail(f"Failed to initialize database tables for skill gap testing: {init_result['message']}")
    print("Database tables initialized for skill gap testing.")

    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    os.makedirs(fixtures_dir, exist_ok=True)

    # Use specific names to avoid collision with mysql_load test files
    test_occupations_csv = os.path.join(fixtures_dir, 'skill_gap_test_occupations.csv')
    test_skills_elements_csv = os.path.join(fixtures_dir, 'skill_gap_test_skills_elements.csv')
    test_occupation_skills_csv = os.path.join(fixtures_dir, 'skill_gap_test_occupation_skills.csv')
    
    request.cls.test_occupations_csv = test_occupations_csv
    request.cls.test_skills_elements_csv = test_skills_elements_csv
    request.cls.test_occupation_skills_csv = test_occupation_skills_csv

    occupations_df = pd.DataFrame([
        {'O*NET-SOC Code': 'OCC001', 'Title': 'Software Developer', 'Description': 'Develops software'},
        {'O*NET-SOC Code': 'OCC002', 'Title': 'Data Scientist', 'Description': 'Analyzes data'},
        {'O*NET-SOC Code': 'OCC003', 'Title': 'Project Manager', 'Description': 'Manages projects'},
        {'O*NET-SOC Code': 'OCC004', 'Title': 'UI/UX Designer', 'Description': 'Designs interfaces'}
    ])
    skills_elements_df = pd.DataFrame([
        {'Element ID': 'SKL001', 'Element Name': 'Programming'},
        {'Element ID': 'SKL002', 'Element Name': 'Data Analysis'},
        {'Element ID': 'SKL003', 'Element Name': 'Communication'},
        {'Element ID': 'SKL004', 'Element Name': 'Problem Solving'},
        {'Element ID': 'SKL005', 'Element Name': 'Graphic Design'}
    ])
    occupation_skills_df = pd.DataFrame([
        {'O*NET-SOC Code': 'OCC001', 'Element ID': 'SKL001', 'Scale ID': 'IM', 'Data Value': 5.0, 'Date': '2023-01-01', 'Domain Source': 'Test'},
        {'O*NET-SOC Code': 'OCC001', 'Element ID': 'SKL004', 'Scale ID': 'IM', 'Data Value': 4.5, 'Date': '2023-01-01', 'Domain Source': 'Test'},
        {'O*NET-SOC Code': 'OCC002', 'Element ID': 'SKL001', 'Scale ID': 'IM', 'Data Value': 4.0, 'Date': '2023-01-01', 'Domain Source': 'Test'},
        {'O*NET-SOC Code': 'OCC002', 'Element ID': 'SKL002', 'Scale ID': 'IM', 'Data Value': 5.0, 'Date': '2023-01-01', 'Domain Source': 'Test'},
        {'O*NET-SOC Code': 'OCC002', 'Element ID': 'SKL004', 'Scale ID': 'IM', 'Data Value': 4.0, 'Date': '2023-01-01', 'Domain Source': 'Test'},
        {'O*NET-SOC Code': 'OCC003', 'Element ID': 'SKL003', 'Scale ID': 'IM', 'Data Value': 5.0, 'Date': '2023-01-01', 'Domain Source': 'Test'},
        {'O*NET-SOC Code': 'OCC003', 'Element ID': 'SKL004', 'Scale ID': 'IM', 'Data Value': 4.0, 'Date': '2023-01-01', 'Domain Source': 'Test'},
        {'O*NET-SOC Code': 'OCC004', 'Element ID': 'SKL005', 'Scale ID': 'IM', 'Data Value': 4.8, 'Date': '2023-01-01', 'Domain Source': 'Test'},
        {'O*NET-SOC Code': 'OCC004', 'Element ID': 'SKL004', 'Scale ID': 'LV', 'Data Value': 3.9, 'Date': '2023-01-01', 'Domain Source': 'Test'}
    ])

    occupations_df.to_csv(test_occupations_csv, index=False, sep='\t')
    skills_elements_df.to_csv(test_skills_elements_csv, index=False, sep='\t')
    occupation_skills_df.to_csv(test_occupation_skills_csv, index=False, sep='\t')

    occ_load = load_data_from_csv(test_occupations_csv, 'Occupations', engine)
    if not occ_load["success"]:
        pytest.fail(f"Failed to load test occupations for skill gap: {occ_load['message']}")
    skill_load = load_data_from_csv(test_skills_elements_csv, 'Skills', engine) # Use the elements CSV for Skills table
    if not skill_load["success"]:
        pytest.fail(f"Failed to load test skills for skill gap: {skill_load['message']}")
    occ_skill_load = load_data_from_csv(test_occupation_skills_csv, 'Occupation_Skills', engine)
    if not occ_skill_load["success"]:
        pytest.fail(f"Failed to load test occupation_skills for skill gap: {occ_skill_load['message']}")
    print("Test data loaded for skill gap testing.")

    yield # For teardown

    print("\nTearing down TestGetSkillGap class fixture...")
    if os.path.exists(test_occupations_csv):
        os.remove(test_occupations_csv)
    if os.path.exists(test_skills_elements_csv):
        os.remove(test_skills_elements_csv)
    if os.path.exists(test_occupation_skills_csv):
        os.remove(test_occupation_skills_csv)
    print("Skill gap test dummy CSV files cleaned up.")

@pytest.mark.usefixtures("skill_gap_db_setup")
class TestGetSkillGap:

    def test_skill_gap_exists(self):
        print("\nRunning test_skill_gap_exists with pytest...")
        result = get_skill_gap('OCC001', 'OCC002')
        assert result["success"], result["message"]
        assert "skill_gaps" in result["result"]
        gaps = {s['element_id']: s['element_name'] for s in result["result"]["skill_gaps"]}
        assert len(gaps) == 1
        assert 'SKL002' in gaps
        assert gaps['SKL002'] == 'Data Analysis'
        print(f"Gap from {result['result']['from_occupation_title']} to {result['result']['to_occupation_title']}:")
        for skill_id, skill_name in gaps.items():
            print(f"  - Need: {skill_name} (ID: {skill_id})")

    def test_no_skill_gap(self):
        print("\nRunning test_no_skill_gap with pytest...")
        result = get_skill_gap('OCC002', 'OCC001')
        assert result["success"], result["message"]
        assert len(result["result"]["skill_gaps"]) == 0
        print(f"No gap from {result['result']['from_occupation_title']} to {result['result']['to_occupation_title']} as expected.")

    def test_identical_occupations(self):
        print("\nRunning test_identical_occupations with pytest...")
        result = get_skill_gap('OCC001', 'OCC001')
        assert result["success"], result["message"]
        assert len(result["result"]["skill_gaps"]) == 0
        print(f"No gap for identical occupations ({result['result']['from_occupation_title']}) as expected.")

    def test_occupation_not_found(self):
        print("\nRunning test_occupation_not_found with pytest...")
        result_from_missing = get_skill_gap('NONEXISTENT', 'OCC001')
        assert not result_from_missing["success"]
        assert "NONEXISTENT not found" in result_from_missing["message"]
        print(f"Correctly handled missing 'from' occupation: {result_from_missing['message']}")

        result_to_missing = get_skill_gap('OCC001', 'NONEXISTENT')
        assert not result_to_missing["success"]
        assert "NONEXISTENT not found" in result_to_missing["message"]
        print(f"Correctly handled missing 'to' occupation: {result_to_missing['message']}")

    def test_occupation_with_no_skills(self):
        print("\nRunning test_occupation_with_no_skills with pytest...")
        result = get_skill_gap('OCC003', 'OCC004') # PM to UI/UX
        assert result["success"], result["message"]
        gaps = {s['element_id']: s['element_name'] for s in result["result"]["skill_gaps"]}
        assert len(gaps) == 1
        assert 'SKL005' in gaps
        assert gaps['SKL005'] == 'Graphic Design'
        print(f"Gap from {result['result']['from_occupation_title']} to {result['result']['to_occupation_title']}:")
        for skill_id, skill_name in gaps.items():
            print(f"  - Need: {skill_name} (ID: {skill_id})")

# For direct execution if needed
if __name__ == '__main__':
    print("Starting integration tests for skill gap analysis (pytest version)...")
    pytest.main(["-s", "-v", __file__]) 