import os
import sys
import unittest
import pandas as pd

# Add project root to sys.path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.functions.mysql_load import load_data_from_csv
from src.functions.mysql_connection import get_mysql_connection
from src.config.schemas import Base, get_sqlalchemy_engine # To initialize and drop tables
from src.functions.mysql_init_tables import initialize_database_tables # To initialize tables

class TestMySQLLoad(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the database and create dummy CSV files before any tests run."""
        print("Setting up TestMySQLLoad...")
        cls.engine = get_sqlalchemy_engine()
        
        # Initialize (create or clear) tables
        init_result = initialize_database_tables()
        if not init_result["success"]:
            raise Exception(f"Failed to initialize database tables for testing: {init_result['message']}")
        print("Database tables initialized for testing.")

        # Define paths for dummy CSVs
        cls.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        os.makedirs(cls.fixtures_dir, exist_ok=True)

        cls.occupations_csv = os.path.join(cls.fixtures_dir, 'test_occupations.csv')
        cls.skills_csv = os.path.join(cls.fixtures_dir, 'test_skills.csv')
        cls.occupation_skills_csv = os.path.join(cls.fixtures_dir, 'test_occupation_skills.csv')

        # Create dummy data
        cls.occupations_data = pd.DataFrame({
            'onet_soc_code': ['T1-0001.00', 'T1-0002.00', 'T1-0003.00', 'T1-0004.00', 'T1-0005.00', 'T1-0006.00'],
            'title': ['Test Occ 1', 'Test Occ 2', 'Test Occ 3', 'Test Occ 4', 'Test Occ 5', 'Test Occ 6'],
            'description': ['Desc 1', 'Desc 2', 'Desc 3', 'Desc 4', 'Desc 5', 'Desc 6']
        })
        cls.occupations_data.to_csv(cls.occupations_csv, index=False)

        cls.skills_data = pd.DataFrame({
            'element_id': ['S1.A.1', 'S1.A.2', 'S1.A.3', 'S1.A.4', 'S1.A.5', 'S1.A.6'],
            'element_name': ['Test Skill 1', 'Test Skill 2', 'Test Skill 3', 'Test Skill 4', 'Test Skill 5', 'Test Skill 6']
        })
        cls.skills_data.to_csv(cls.skills_csv, index=False)

        cls.occupation_skills_data = pd.DataFrame({
            'onet_soc_code': ['T1-0001.00', 'T1-0001.00', 'T1-0002.00', 'T1-0003.00', 'T1-0004.00', 'T1-0005.00', 'T1-0006.00'],
            'element_id': ['S1.A.1', 'S1.A.2', 'S1.A.1', 'S1.A.3', 'S1.A.4', 'S1.A.5', 'S1.A.6'],
            'scale_id': ['IM', 'IM', 'LV', 'IM', 'LV', 'IM', 'LV'],
            'data_value': [4.5, 4.2, 3.7, 4.0, 3.5, 4.8, 3.2],
            'n_value': [10, 10, 8, 12, 9, 15, 7],
            'standard_error': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            'lower_ci_bound': [4.3, 4.0, 3.5, 3.8, 3.3, 4.6, 3.0],
            'upper_ci_bound': [4.7, 4.4, 3.9, 4.2, 3.7, 5.0, 3.4],
            'recommend_suppress': ['N', 'N', 'N', 'N', 'N', 'N', 'N'],
            'not_relevant': [None, None, None, None, None, None, None],
            'date_recorded': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01'],
            'domain_source': ['Test', 'Test', 'Test', 'Test', 'Test', 'Test', 'Test']
        })
        cls.occupation_skills_data.to_csv(cls.occupation_skills_csv, index=False)
        print(f"Created dummy CSVs in {cls.fixtures_dir}")

    def test_load_data(self):
        """Test loading data into all tables and verify counts and content."""
        print("\nRunning test_load_data...")
        
        # Load Occupations
        load_occ_result = load_data_from_csv(self.occupations_csv, 'Occupations', self.engine)
        self.assertTrue(load_occ_result["success"], f"Failed to load Occupations: {load_occ_result['message']}")
        self.assertEqual(load_occ_result["result"].get("records_loaded"), len(self.occupations_data), "Occupation record count mismatch")
        print(f"Occupations load: {load_occ_result['message']}")

        # Load Skills
        load_skill_result = load_data_from_csv(self.skills_csv, 'Skills', self.engine)
        self.assertTrue(load_skill_result["success"], f"Failed to load Skills: {load_skill_result['message']}")
        self.assertEqual(load_skill_result["result"].get("records_loaded"), len(self.skills_data), "Skill record count mismatch")
        print(f"Skills load: {load_skill_result['message']}")

        # Load Occupation_Skills
        load_occ_skill_result = load_data_from_csv(self.occupation_skills_csv, 'Occupation_Skills', self.engine)
        self.assertTrue(load_occ_skill_result["success"], f"Failed to load Occupation_Skills: {load_occ_skill_result['message']}")
        self.assertEqual(load_occ_skill_result["result"].get("records_loaded"), len(self.occupation_skills_data), "Occupation_Skills record count mismatch")
        print(f"Occupation_Skills load: {load_occ_skill_result['message']}")

        # Verify data using direct SQL connection
        conn_details = get_mysql_connection()
        self.assertTrue(conn_details["success"], f"Failed to connect to MySQL for verification: {conn_details['message']}")
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
            self.assertEqual(count, expected_count, f"Row count mismatch for table {table_name}")
            print(f"Table '{table_name}' has {count} rows (matches expected)." )

            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            print(f"First {min(5, len(rows))} rows from '{table_name}':")
            print(", ".join(column_names)) # Print header
            for row in rows:
                print(row)
            self.assertTrue(len(rows) > 0 if expected_count > 0 else True, f"No rows found in {table_name} when expected.")
            print("---")

        cursor.close()
        connection.close()
        print("test_load_data completed.")

    @classmethod
    def tearDownClass(cls):
        """Clean up dummy CSV files after all tests have run."""
        print("\nTearing down TestMySQLLoad...")
        # Clean up by removing the dummy CSV files
        if os.path.exists(cls.occupations_csv):
            os.remove(cls.occupations_csv)
        if os.path.exists(cls.skills_csv):
            os.remove(cls.skills_csv)
        if os.path.exists(cls.occupation_skills_csv):
            os.remove(cls.occupation_skills_csv)
        
        # Optionally, remove the fixtures directory if it's empty and was created by the test
        if os.path.exists(cls.fixtures_dir) and not os.listdir(cls.fixtures_dir):
            # os.rmdir(cls.fixtures_dir) # Commented out: might be shared
            pass
        print("Dummy CSV files cleaned up.")

if __name__ == '__main__':
    print("Starting integration tests for MySQL data loading...")
    # Ensure environment variables are loaded (e.g., by sourcing env/env.env)
    # Example: source env/env.env && python tests/test_integration_mysql_load.py
    unittest.main() 