import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from src.config.schemas import Occupation, Skill, get_sqlalchemy_engine
from src.functions.mysql_connection import get_mysql_connection

def load_data_from_dataframe(df: pd.DataFrame, table_name: str, engine, clear_existing: bool = True) -> dict:
    """
    Loads data from a pandas DataFrame into the specified table using SQLAlchemy.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to load.
        table_name (str): The name of the table to load data into.
                          Valid names are 'Occupations', 'Skills', 'Scales'.
        engine (sqlalchemy.engine.base.Engine): SQLAlchemy engine for database connection.
        clear_existing (bool): Whether to clear existing data before loading. Defaults to True.

    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str), and 'result' (dict).
    """
    if df.empty:
        return {
            "success": True,
            "message": f"No records to load into {table_name}",
            "result": {"records_loaded": 0}
        }

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Convert NaN to None for SQLAlchemy compatibility
        df = df.where(pd.notnull(df), None)

        if table_name == 'Occupations':
            model = Occupation
            # Ensure only relevant columns are selected if df has more
            df = df[['onet_soc_code', 'title', 'description']]
            records = df.to_dict(orient='records')
        elif table_name == 'Skills':
            model = Skill
            # The input DataFrame (df) is now expected to have all necessary columns for the expanded Skills table.
            # No need to select specific columns or drop duplicates here, as extract_load.py prepares the df.
            # The composite primary key (onet_soc_code, element_id, scale_id) handles uniqueness.
            required_skill_cols = [
                'onet_soc_code', 'element_id', 'element_name', 'scale_id', 'data_value',
                'n_value', 'standard_error', 'lower_ci_bound', 'upper_ci_bound',
                'recommend_suppress', 'not_relevant', 'date_recorded', 'domain_source'
            ]
            # Ensure all required columns for Skill are present
            # It's okay if df has extra columns, they will be ignored by SQLAlchemy during mapping if not in the model.
            # However, we should check for the core ones needed for a valid skill entry based on skills.txt structure.
            minimal_cols_present = [col for col in ['onet_soc_code', 'element_id', 'element_name', 'scale_id', 'data_value'] if col in df.columns]
            if len(minimal_cols_present) < 5: # Check if essential columns are present
                 session.close()
                 missing_essential = list(set(['onet_soc_code', 'element_id', 'element_name', 'scale_id', 'data_value']) - set(df.columns))
                 return {"success": False, "message": f"DataFrame for Skills table missing essential columns: {missing_essential}", "result": {}}

            records = df.to_dict(orient='records')
        elif table_name == 'Scales': # Added handling for Scales table
            model = Scale
            from src.config.schemas import Scale # Import Scale model here or at the top
            df = df[['scale_id', 'scale_name', 'minimum', 'maximum']]
            records = df.to_dict(orient='records')
        else:
            session.close()
            return {"success": False, "message": f"Invalid table name: {table_name}", "result": {}}

        # Always clear the table before loading new data
        try:
            print(f"Clearing existing data from table {table_name}...")
            session.query(model).delete()
            session.commit()
            print(f"Table {table_name} cleared.")
        except Exception as e:
            session.rollback()
            session.close()
            return {"success": False, "message": f"Error clearing table {table_name}: {e}", "result": {}}

        session.bulk_insert_mappings(model, records)
        session.commit()
        
        num_records_loaded = len(records)
        session.close()
        return {
            "success": True, 
            "message": f"Successfully loaded {num_records_loaded} records into {table_name}", 
            "result": {"records_loaded": num_records_loaded}
        }

    except Exception as e:
        session.rollback()
        session.close()
        return {"success": False, "message": f"Error loading data into {table_name}: {e}", "result": {}}

if __name__ == '__main__':
    from src.functions.extract_onet_data import extract_onet_data
    
    print("Starting data loading process from O*NET data...")

    # Get SQLAlchemy engine
    try:
        engine = get_sqlalchemy_engine()
        print("SQLAlchemy engine created successfully.")
    except ValueError as ve:
        print(f"Failed to create SQLAlchemy engine: {ve}")
        print("Ensure MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE environment variables are set.")
        print("You might need to source your env/env.env file.")
        exit(1)
    except Exception as e:
        print(f"Failed to create SQLAlchemy engine: {e}")
        exit(1)

    # Extract data from O*NET files
    print("\n--- Extracting O*NET Data ---")
    data_results = extract_onet_data()
    
    # Define the desired loading order
    load_order = ['occupations.txt', 'scales.txt', 'skills.txt']
    
    # Sort data_results based on load_order
    # This assumes all filenames in load_order are present in data_results
    # and handles cases where data_results might have other files not in load_order (they'll be appended)
    sorted_data_results = sorted(
        data_results,
        key=lambda x: load_order.index(x['filename']) if x['filename'] in load_order else float('inf')
    )

    # Process each extracted dataset in the defined order
    for result in sorted_data_results:
        filename = result['filename']
        df = result['df']
        load_result = {"success": False, "message": f"No specific loading logic for {filename}"} # Default
        
        if filename == 'occupations.txt':
            print("\n--- Loading Occupations ---")
            load_result = load_data_from_dataframe(df, 'Occupations', engine)
        elif filename == 'scales.txt': # Scales are now loaded before Skills
            print("\n--- Loading Scales ---")
            load_result = load_data_from_dataframe(df, 'Scales', engine)
        elif filename == 'skills.txt':
            print("\n--- Loading Skills (New Schema) ---")
            load_result = load_data_from_dataframe(df, 'Skills', engine)
        # Add other elif blocks here if there are other files to process
        
        print(load_result['message'])
        if not load_result['success']:
            print(f"Stopping due to error in loading data from {filename}.")
            exit(1)

    # Verification
    print("\n--- Verifying Data ---")
    connection_details = get_mysql_connection()
    if connection_details["success"]:
        connection = connection_details["result"]
        cursor = connection.cursor(dictionary=True)
        
        tables_to_verify = ['Occupations', 'Skills', 'Scales']
        for table in tables_to_verify:
            try:
                cursor.execute(f"SELECT COUNT(*) AS count FROM {table};")
                count_result = cursor.fetchone()
                count = count_result['count'] if count_result else 0
                print(f"Table '{table}' has {count} rows.")

                if count > 0:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
                    rows = cursor.fetchall()
                    if rows:
                        print(f"First {len(rows)} rows from '{table}':")
                        for row in rows:
                            print(row)
                    else:
                        print(f"Could not fetch sample rows from '{table}', though count is > 0.")
                else:
                    print(f"No rows found in '{table}' to sample.")
            except Exception as e:
                print(f"Error verifying table {table}: {e}")
            print("---")
            
        cursor.close()
        connection.close()
        print("MySQL connection closed after verification.")
    else:
        print(f"Failed to connect to MySQL for verification: {connection_details['message']}")

    print("\nData loading process finished.")
