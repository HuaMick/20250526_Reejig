import os
import sys
import pytest
import pandas as pd

# Add project root to sys.path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.functions.mysql_load import load_data_from_csv
from src.functions.mysql_connection import get_mysql_connection
from src.config.schemas import Base, get_sqlalchemy_engine # To initialize and drop tables
from src.functions.mysql_init_tables import initialize_database_tables # To initialize tables

@pytest.fixture(scope="class")
def db_setup(request):
    """Set up the database and create dummy CSV files before any tests run in the class."""
    print("Setting up TestMySQLLoad class with pytest fixture...")
    engine = get_sqlalchemy_engine()
    request.cls.engine = engine
    
    init_result = initialize_database_tables()
    if not init_result["success"]:
        pytest.fail(f"Failed to initialize database tables for testing: {init_result['message']}")
    print("Database tables initialized for testing.")

    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    os.makedirs(fixtures_dir, exist_ok=True)
    request.cls.fixtures_dir = fixtures_dir

    occupations_csv = os.path.join(fixtures_dir, 'test_occupations.csv')
    skills_csv = os.path.join(fixtures_dir, 'test_skills.csv')
    occupation_skills_csv = os.path.join(fixtures_dir, 'test_occupation_skills.csv')

    request.cls.occupations_csv = occupations_csv
    request.cls.skills_csv = skills_csv
    request.cls.occupation_skills_csv = occupation_skills_csv

    occupations_data = pd.DataFrame({
        'O*NET-SOC Code': ['T1-0001.00', 'T1-0002.00', 'T1-0003.00', 'T1-0004.00', 'T1-0005.00', 'T1-0006.00'],
        'Title': ['Test Occ 1', 'Test Occ 2', 'Test Occ 3', 'Test Occ 4', 'Test Occ 5', 'Test Occ 6'],
        'Description': ['Desc 1', 'Desc 2', 'Desc 3', 'Desc 4', 'Desc 5', 'Desc 6']
    })
    # Use O*NET headers for dummy CSVs to match load_data_from_csv expectations
    occupations_data.to_csv(occupations_csv, index=False, sep='\t') 
    request.cls.occupations_data = occupations_data

    skills_data = pd.DataFrame({
        'Element ID': ['S1.A.1', 'S1.A.2', 'S1.A.3', 'S1.A.4', 'S1.A.5', 'S1.A.6'],
        'Element Name': ['Test Skill 1', 'Test Skill 2', 'Test Skill 3', 'Test Skill 4', 'Test Skill 5', 'Test Skill 6']
    })
    skills_data.to_csv(skills_csv, index=False, sep='\t')
    request.cls.skills_data = skills_data

    occupation_skills_data = pd.DataFrame({
        'O*NET-SOC Code': ['T1-0001.00', 'T1-0001.00', 'T1-0002.00', 'T1-0003.00', 'T1-0004.00', 'T1-0005.00', 'T1-0006.00'],
        'Element ID': ['S1.A.1', 'S1.A.2', 'S1.A.1', 'S1.A.3', 'S1.A.4', 'S1.A.5', 'S1.A.6'],
        'Scale ID': ['IM', 'IM', 'LV', 'IM', 'LV', 'IM', 'LV'],
        'Data Value': [4.5, 4.2, 3.7, 4.0, 3.5, 4.8, 3.2],
        'N': [10, 10, 8, 12, 9, 15, 7],
        'Standard Error': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        'Lower CI Bound': [4.3, 4.0, 3.5, 3.8, 3.3, 4.6, 3.0],
        'Upper CI Bound': [4.7, 4.4, 3.9, 4.2, 3.7, 5.0, 3.4],
        'Recommend Suppress': ['N', 'N', 'N', 'N', 'N', 'N', 'N'],
        'Not Relevant': [None, None, None, None, None, None, None],
        'Date': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01'],
        'Domain Source': ['Test', 'Test', 'Test', 'Test', 'Test', 'Test', 'Test']
    })
    occupation_skills_data.to_csv(occupation_skills_csv, index=False, sep='\t')
    request.cls.occupation_skills_data = occupation_skills_data
    print(f"Created dummy CSVs (tab-separated) in {fixtures_dir}")

    yield # For teardown

    print("\nTearing down TestMySQLLoad class fixture...")
    if os.path.exists(occupations_csv):
        os.remove(occupations_csv)
    if os.path.exists(skills_csv):
        os.remove(skills_csv)
    if os.path.exists(occupation_skills_csv):
        os.remove(occupation_skills_csv)
    print("Dummy CSV files cleaned up.")

@pytest.mark.usefixtures("db_setup")
class TestMySQLLoad:

    def test_load_data(self):
        """Test loading data into all tables and verify counts and content."""
        print("\nRunning test_load_data with pytest...")
        
        load_occ_result = load_data_from_csv(self.occupations_csv, 'Occupations', self.engine)
        assert load_occ_result["success"], f"Failed to load Occupations: {load_occ_result['message']}"
        assert load_occ_result["result"].get("records_loaded") == len(self.occupations_data), "Occupation record count mismatch"
        print(f"Occupations load: {load_occ_result['message']}")

        load_skill_result = load_data_from_csv(self.skills_csv, 'Skills', self.engine)
        assert load_skill_result["success"], f"Failed to load Skills: {load_skill_result['message']}"
        assert load_skill_result["result"].get("records_loaded") == len(self.skills_data), "Skill record count mismatch"
        print(f"Skills load: {load_skill_result['message']}")

        load_occ_skill_result = load_data_from_csv(self.occupation_skills_csv, 'Occupation_Skills', self.engine)
        assert load_occ_skill_result["success"], f"Failed to load Occupation_Skills: {load_occ_skill_result['message']}"
        assert load_occ_skill_result["result"].get("records_loaded") == len(self.occupation_skills_data), "Occupation_Skills record count mismatch"
        print(f"Occupation_Skills load: {load_occ_skill_result['message']}")

        conn_details = get_mysql_connection()
        assert conn_details["success"], f"Failed to connect to MySQL for verification: {conn_details['message']}"
        connection = conn_details["result"]
        cursor = connection.cursor()

        tables_to_verify = {
            "Occupations": len(self.occupations_data),
            "Skills": len(self.skills_data),
            "Occupation_Skills": len(self.occupation_skills_data)
        }

        print("\n--- Verifying Table Data ---")
        for table_name, expected_count in tables_to_verify.items():
            print(f"Verifying table: {table_name}")
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            assert count == expected_count, f"Row count mismatch for table {table_name}"
            print(f"Table '{table_name}' has {count} rows (matches expected)." )

            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            print(f"First {min(5, len(rows))} rows from '{table_name}':")
            print(", ".join(column_names))
            for row in rows:
                print(row)
            assert len(rows) > 0 if expected_count > 0 else True, f"No rows found in {table_name} when expected."
            print("---")

        cursor.close()
        connection.close()
        print("test_load_data completed.")

# For direct execution if needed, though pytest CLI is preferred
if __name__ == '__main__':
    print("Starting integration tests for MySQL data loading (pytest version)...")
    # Running pytest programmatically. Ensure correct arguments if used.
    # Example: pytest.main(["-v", __file__])
    # However, typical execution is via `pytest` command in terminal.
    pytest.main(["-s", "-v", __file__]) # -s to show print statements 