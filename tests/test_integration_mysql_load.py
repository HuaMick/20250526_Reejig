import os
import sys
import pytest
import pandas as pd

# Add project root to sys.path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.functions.mysql_load import load_data_from_dataframe
from src.functions.extract_onet_data import extract_onet_data
from src.functions.mysql_connection import get_mysql_connection
from src.config.schemas import get_sqlalchemy_engine # Base, Occupation, Skill, Scale not directly used here now
from src.functions.mysql_init_tables import initialize_database_tables

class TestMySQLLoadWithoutFixtures:

    def test_load_actual_data_end_to_end(self):
        print("\nRunning test_load_actual_data_end_to_end (no fixtures)...")

        # 1. Get SQLAlchemy engine
        engine = None
        try:
            engine = get_sqlalchemy_engine()
            print("SQLAlchemy engine created successfully.")
        except Exception as e:
            pytest.fail(f"Failed to create SQLAlchemy engine: {e}")

        # 2. Initialize database tables
        # initialize_database_tables uses its own engine creation logic based on env vars.
        # This is fine as it ensures a fresh setup.
        init_result = initialize_database_tables()
        if not init_result["success"]:
            pytest.fail(f"Failed to initialize database tables: {init_result['message']}")
        print("Database tables initialized successfully.")

        # 3. Extract actual data using extract_onet_data()
        extracted_data_results = []
        try:
            print("Extracting O*NET data using extract_onet_data()...")
            extracted_data_results = extract_onet_data()
            if not extracted_data_results:
                pytest.fail("extract_onet_data() returned no results. Ensure O*NET files are present in database/ directory and are not empty.")
            print(f"Data extracted for {len(extracted_data_results)} files.")
            # Check if any DataFrame is empty, which might indicate an issue or an empty source file
            for res in extracted_data_results:
                print(f"  - {res['filename']}: {res['df'].shape[0]} rows")
                if res['df'].empty and res['filename'] in ['occupations.txt', 'skills.txt', 'scales.txt']:
                    print(f"Warning: Extracted DataFrame for {res['filename']}] is empty. This might lead to 0 records loaded.")

        except Exception as e:
            pytest.fail(f"Error during extract_onet_data(): {e}")
        
        # 4. Load data into tables
        loaded_counts = {}
        expected_tables_to_load_from = ['occupations.txt', 'skills.txt', 'scales.txt']
        found_files_to_load = {res['filename']: res['df'] for res in extracted_data_results if res['filename'] in expected_tables_to_load_from}

        if not all(fn in found_files_to_load for fn in expected_tables_to_load_from):
            missing_files = list(set(expected_tables_to_load_from) - set(found_files_to_load.keys()))
            print(f"Warning: Not all expected source files were found in extract_onet_data results: {missing_files}. Test might not be comprehensive.")

        for filename, df in found_files_to_load.items():
            table_name_map = {
                'occupations.txt': 'Occupations',
                'skills.txt': 'Skills',
                'scales.txt': 'Scales'
            }
            table_name = table_name_map.get(filename)
            
            if table_name:
                print(f"--- Loading data from {filename} into {table_name} table ---")
                if df.empty:
                    print(f"DataFrame for {filename} is empty. Skipping load for {table_name}. 0 records expected.")
                    loaded_counts[table_name] = 0
                    continue # Skip to next file if DataFrame is empty
                
                load_result = load_data_from_dataframe(df, table_name, engine) 
                assert load_result["success"], f"Failed to load {table_name} from {filename}: {load_result['message']}"
                records_loaded = load_result["result"].get("records_loaded", 0)
                
                assert records_loaded == df.shape[0], \
                    f"Record count mismatch for {table_name}. Expected {df.shape[0]} rows from DataFrame, loaded {records_loaded} into DB."
                print(f"{table_name} load: {load_result['message']}")
                loaded_counts[table_name] = records_loaded
            # No else needed as we pre-filtered found_files_to_load

        # 5. Verification
        if not loaded_counts or all(count == 0 for count in loaded_counts.values()):
            pytest.skip("No data was loaded into any target tables (possibly due to empty source files or filters). Skipping DB verification.")

        conn_details = get_mysql_connection()
        assert conn_details["success"], f"Failed to connect to MySQL for verification: {conn_details['message']}"
        connection = conn_details["result"]
        cursor = connection.cursor(dictionary=True)

        print("\n--- Verifying Table Data (Counts and Sample) ---")
        for table_name, expected_db_count in loaded_counts.items():
            if expected_db_count == 0:
                print(f"Skipping DB verification for {table_name} as 0 records were loaded.")
                # Optionally, verify table is indeed empty
                cursor.execute(f"SELECT COUNT(*) AS count FROM {table_name}")
                db_empty_check = cursor.fetchone()
                assert db_empty_check['count'] == 0, f"Table {table_name} expected to be empty but has {db_empty_check['count']} rows."
                continue

            print(f"Verifying table: {table_name}")
            cursor.execute(f"SELECT COUNT(*) AS count FROM {table_name}")
            db_count_result = cursor.fetchone()
            db_count = db_count_result['count'] if db_count_result else 0
            
            assert db_count == expected_db_count, \
                f"Row count mismatch for table {table_name}. Loaded {expected_db_count}, found in DB {db_count}."
            print(f"Table '{table_name}' has {db_count} rows (matches loaded count).")

            if db_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                rows = cursor.fetchall()
                if rows:
                    column_names = list(rows[0].keys())
                    print(f"First {min(2, len(rows))} rows from '{table_name}':")
                    print(", ".join(column_names))
                    for row in rows:
                        print(row)
                assert len(rows) > 0, f"No rows sampled from {table_name} when count was > 0."
            print("---")

        cursor.close()
        connection.close()
        print("test_load_actual_data_end_to_end completed.")

# For direct execution
if __name__ == '__main__':
    print("Starting integration tests for MySQL data loading (no fixtures, pytest version)...")
    pytest.main(["-s", "-v", __file__]) 