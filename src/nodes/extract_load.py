import os
import sys
from src.functions.extract_onet_data import extract_onet_data
from src.functions.mysql_load import load_data_from_dataframe
from src.functions.mysql_connection import get_mysql_connection # For verification step
from src.config.schemas import get_sqlalchemy_engine

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
        
        table_name_to_load = None
        if filename == 'occupations.txt':
            table_name_to_load = 'Occupations'
        elif filename == 'skills.txt':
            table_name_to_load = 'Skills'
        elif filename == 'scales.txt':
            table_name_to_load = 'Scales'
        else:
            print(f"Warning: Unknown file type {filename} encountered in extracted data. Skipping load.")
            continue

        print(f"--- Loading data into {table_name_to_load} table ---")
        load_result = load_data_from_dataframe(df, table_name_to_load, engine)
        print(f"{table_name_to_load} load: {load_result['message']}")
        if not load_result['success']:
            print(f"CRITICAL ERROR: Stopping due to error in loading data into {table_name_to_load} table.")
            sys.exit(1)

    # Step 4: Verifying Data (Optional but good for a node)
    print("\n--- Verifying Loaded Data ---")
    connection_details = get_mysql_connection()
    if connection_details["success"]:
        connection = connection_details["result"]
        cursor = connection.cursor(dictionary=True)
        tables_to_verify = ['Occupations', 'Skills', 'Scales']
        verification_errors = False
        for table in tables_to_verify:
            try:
                cursor.execute(f"SELECT COUNT(*) AS count FROM {table};")
                count_result = cursor.fetchone()
                count = count_result['count'] if count_result else 0
                print(f"Table '{table}' has {count} rows.")

                if count > 0:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 2;") # Sample 2 rows
                    rows = cursor.fetchall()
                    if rows:
                        print(f"Sample rows from '{table}':")
                        for row_idx, row_data in enumerate(rows):
                            # Basic formatting for cleaner output
                            formatted_row = {k: (str(v)[:75] + '...' if isinstance(v, str) and len(str(v)) > 75 else v) for k, v in row_data.items()}
                            print(f"  Row {row_idx+1}: {formatted_row}")
                else:
                    print(f"No rows found in '{table}' to sample. This might be an issue if data was expected.")
            except Exception as e:
                print(f"ERROR: Could not verify table {table}: {e}")
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
