import os
import sys
from src.functions.extract_onet_data import extract_onet_data
from src.functions.mysql_load import load_data_from_dataframe
from src.config.schemas import get_sqlalchemy_engine

def main():
    """
    Main function to extract O*NET data and load it into MySQL database.
    """
    print("Starting O*NET data extraction and loading process...")

    # Get SQLAlchemy engine
    try:
        engine = get_sqlalchemy_engine()
        print("SQLAlchemy engine created successfully.")
    except ValueError as ve:
        print(f"Failed to create SQLAlchemy engine: {ve}")
        print("Ensure MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE environment variables are set.")
        print("You might need to source your env/env.env file.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to create SQLAlchemy engine: {e}")
        sys.exit(1)

    # Extract data from O*NET files
    print("\n--- Extracting O*NET Data ---")
    try:
        data_results = extract_onet_data()
        if not data_results:
            print("No data was extracted from O*NET files.")
            sys.exit(1)
    except Exception as e:
        print(f"Error extracting O*NET data: {e}")
        sys.exit(1)
    
    # Process each extracted dataset
    for result in data_results:
        filename = result['filename']
        df = result['df']
        
        print(f"\nProcessing {filename}...")
        print(f"DataFrame shape: {df.shape}")
        
        if filename == 'occupations.txt':
            print("\n--- Loading Occupations ---")
            load_result = load_data_from_dataframe(df, 'Occupations', engine)
        elif filename == 'skills.txt':
            print("\n--- Loading Skills (New Schema) ---")
            # The entire df from skills.txt (after extract_onet_data processing)
            # now maps to the new expanded Skills table.
            if not df.empty:
                 load_result = load_data_from_dataframe(df, 'Skills', engine) # Load full df into Skills
                 print(f"Skills table: {load_result['message']}")
                 if not load_result['success']:
                    print(f"Stopping due to error in loading data into Skills table.")
                    sys.exit(1)
            else:
                print("Skills DataFrame is empty. Nothing to load.")
                load_result = {'success': True, 'message': "Skills DataFrame was empty, nothing loaded."}

        elif filename == 'scales.txt':
            print("\n--- Loading Scales ---")
            load_result = load_data_from_dataframe(df, 'Scales', engine)
        else:
            print(f"Unknown file: {filename}")
            continue
        
        print(load_result['message'])
        if not load_result['success']:
            print(f"Stopping due to error in loading data from {filename}.")
            sys.exit(1)

    print("\nO*NET data extraction and loading process completed successfully.")

if __name__ == '__main__':
    main()
