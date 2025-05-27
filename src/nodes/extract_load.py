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
            print("\n--- Loading Skills ---")
            # We only load distinct skills into the Skills table
            # The full skills_df is used for Occupation_Skills
            distinct_skills_df = df[['element_id', 'element_name']].drop_duplicates().copy()
            if not distinct_skills_df.empty and 'element_id' in distinct_skills_df.columns and 'element_name' in distinct_skills_df.columns:
                 load_result_skills = load_data_from_dataframe(distinct_skills_df, 'Skills', engine)
                 print(f"Skills table: {load_result_skills['message']}")
                 if not load_result_skills['success']:
                    print(f"Stopping due to error in loading data into Skills table.")
                    sys.exit(1)
            else:
                print("No distinct skills to load or columns missing.")

            print("\n--- Loading Occupation_Skills ---")
            # Select only columns relevant to Occupation_Skills
            occupation_skills_columns = [
                'onet_soc_code', 'element_id', 'scale_id', 'data_value', 
                'n_value', 'standard_error', 'lower_ci_bound', 'upper_ci_bound',
                'recommend_suppress', 'not_relevant', 'date_recorded', 'domain_source'
            ]
            # Filter df to only include relevant columns that actually exist in it
            relevant_occupation_skills_df = df[[col for col in occupation_skills_columns if col in df.columns]].copy()
            
            if not relevant_occupation_skills_df.empty:
                load_result_occupation_skills = load_data_from_dataframe(relevant_occupation_skills_df, 'Occupation_Skills', engine)
                print(f"Occupation_Skills table: {load_result_occupation_skills['message']}")
                if not load_result_occupation_skills['success']:
                    print(f"Stopping due to error in loading data into Occupation_Skills table.")
                    sys.exit(1)
            else:
                print("No data to load into Occupation_Skills table or relevant columns missing.")
            load_result = {'success': True, 'message': "Skills and Occupation_Skills processed."} # Overall success for this branch

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
