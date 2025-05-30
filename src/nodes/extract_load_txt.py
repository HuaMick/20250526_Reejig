import os
import sys
from src.functions.extract_onet_data import extract_onet_data, extract_occupations, extract_skills, extract_scales
from src.functions.mysql_load_table import load_data_from_dataframe
from src.functions.mysql_connection import get_mysql_connection # For verification step
from src.config.schemas import get_sqlalchemy_engine, Onet_Occupations_Landing, Onet_Skills_Landing, Onet_Scales_Landing

def main():
    """
    Main function to orchestrate the extraction of O*NET data 
    and its loading into the MySQL database.
    It also verifies the loaded data by checking table counts and sampling rows.
    """
    print("Starting O*NET data extraction and loading process...")

    # Step 1: Get SQLAlchemy engine
    print("\n--- Initializing Database Connection ---")
    try:
        engine = get_sqlalchemy_engine()
        print("SQLAlchemy engine created successfully.")
    except ValueError as ve:
        print(f"ERROR: Failed to create SQLAlchemy engine: {ve}")
        print("Ensure MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE environment variables are set.")
        sys.exit(1)
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to create SQLAlchemy engine: {e}")
        sys.exit(1)

    # Step 2: Extract data from O*NET files
    print("\n--- Extracting O*NET Data ---")
    
    # Option 1: Use the combined extract_onet_data function
    extraction_result = extract_onet_data()

    if not extraction_result["success"] and not extraction_result["result"]["extracted_data"]:
        print(f"CRITICAL ERROR: Data extraction failed entirely. Message: {extraction_result['message']}")
        sys.exit(1)
    
    print(extraction_result['message']) # Print extraction summary (includes partial errors)
    extracted_data_list = extraction_result["result"]["extracted_data"]

    if not extracted_data_list:
        print("Warning: No data was successfully extracted from O*NET files. Exiting.")
        sys.exit(0) # Not a critical error if no files were found/processed, but nothing to load.

    # Step 3: Load data into database tables
    print("\n--- Loading Data into Database ---")
    for item in extracted_data_list:
        filename = item['filename']
        df = item['df']
        
        print(f"\nProcessing data from {filename}...")
        if df.empty:
            print(f"DataFrame for {filename} is empty. Skipping load.")
            continue
        
        # Map filenames to SQLAlchemy models
        model_to_load = None
        table_name = None
        if filename == 'occupations.txt':
            model_to_load = Onet_Occupations_Landing
            table_name = 'Occupations'
        elif filename == 'skills.txt':
            model_to_load = Onet_Skills_Landing
            table_name = 'Skills'
        elif filename == 'scales.txt':
            model_to_load = Onet_Scales_Landing
            table_name = 'Scales'
        else:
            print(f"Warning: Unknown file type {filename} encountered in extracted data. Skipping load.")
            continue

        print(f"--- Loading data into {table_name} table ---")
        load_result = load_data_from_dataframe(df, model_to_load, engine)
        print(f"{table_name} load: {load_result['message']}")
        if not load_result['success']:
            print(f"CRITICAL ERROR: Stopping due to error in loading data into {table_name} table.")
            sys.exit(1)

    # Step 4: Verifying Data (Optional but good for a node)
    print("\n--- Verifying Loaded Data ---")
    connection_details = get_mysql_connection()
    if connection_details["success"]:
        connection = connection_details["result"]
        cursor = connection.cursor(dictionary=True)
        
        # Map logical table names to actual database table names
        table_mapping = {
            'Occupations': 'onet_occupations_landing', 
            'Skills': 'onet_skills_landing', 
            'Scales': 'onet_scales_landing'
        }
        
        verification_errors = False
        for logical_name, db_table in table_mapping.items():
            try:
                cursor.execute(f"SELECT COUNT(*) AS count FROM {db_table};")
                count_result = cursor.fetchone()
                count = count_result['count'] if count_result else 0
                print(f"Table '{logical_name}' ({db_table}) has {count} rows.")

                if count > 0:
                    cursor.execute(f"SELECT * FROM {db_table} LIMIT 2;") # Sample 2 rows
                    rows = cursor.fetchall()
                    if rows:
                        print(f"Sample rows from '{logical_name}' ({db_table}):")
                        for row_idx, row_data in enumerate(rows):
                            # Basic formatting for cleaner output
                            formatted_row = {k: (str(v)[:75] + '...' if isinstance(v, str) and len(str(v)) > 75 else v) for k, v in row_data.items()}
                            print(f"  Row {row_idx+1}: {formatted_row}")
                else:
                    print(f"No rows found in '{logical_name}' ({db_table}) to sample. This might be an issue if data was expected.")
            except Exception as e:
                print(f"ERROR: Could not verify table {logical_name} ({db_table}): {e}")
                verification_errors = True
            print("---")
        cursor.close()
        connection.close()
        print("Database connection closed after verification.")
        if verification_errors:
            print("Warning: Errors occurred during data verification.")
    else:
        print(f"Warning: Could not connect to MySQL for verification: {connection_details['message']}")

    print("\nO*NET data extraction and loading process finished.")


if __name__ == '__main__':
    main()  