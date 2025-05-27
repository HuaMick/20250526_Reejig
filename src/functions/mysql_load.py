import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from src.config.schemas import Occupation, Skill, OccupationSkill, get_sqlalchemy_engine
from src.functions.mysql_connection import get_mysql_connection

def load_data_from_dataframe(df: pd.DataFrame, table_name: str, engine, clear_existing: bool = True) -> dict:
    """
    Loads data from a pandas DataFrame into the specified table using SQLAlchemy.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to load.
        table_name (str): The name of the table to load data into.
                          Valid names are 'Occupations', 'Skills', 'Occupation_Skills'.
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
            # For Skills table, we need unique element_id and element_name
            if 'element_id' in df.columns and 'element_name' in df.columns:
                df = df[['element_id', 'element_name']].drop_duplicates().reset_index(drop=True)
                records = df.to_dict(orient='records')
            else:
                session.close()
                return {"success": False, "message": "DataFrame missing 'element_id' or 'element_name' columns.", "result": {}}
        elif table_name == 'Occupation_Skills':
            model = OccupationSkill
            # Ensure all required columns for OccupationSkill are present
            required_cols = ['onet_soc_code', 'element_id', 'scale_id', 'data_value', 
                           'n_value', 'standard_error', 'lower_ci_bound', 'upper_ci_bound',
                           'recommend_suppress', 'not_relevant', 'date_recorded', 'domain_source']
            if not all(col in df.columns for col in required_cols):
                missing_cols = [col for col in required_cols if col not in df.columns]
                session.close()
                return {"success": False, "message": f"DataFrame missing required columns: {missing_cols}", "result": {}}
            df = df[required_cols]
            
            # Handle date conversion
            if 'date_recorded' in df.columns and df['date_recorded'].dtype == 'object':
                try:
                    df['date_recorded'] = pd.to_datetime(df['date_recorded'], errors='coerce')
                    df['date_recorded'] = df['date_recorded'].where(pd.notnull(df['date_recorded']), None)
                except Exception as e:
                    print(f"Warning: Could not parse all 'date_recorded' values: {e}")
            
            records = df.to_dict(orient='records')
            # Handle NaN/NaT values
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
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
    
    # Process each extracted dataset
    for result in data_results:
        filename = result['filename']
        df = result['df']
        
        if filename == 'occupations.txt':
            print("\n--- Loading Occupations ---")
            load_result = load_data_from_dataframe(df, 'Occupations', engine)
        elif filename == 'skills.txt':
            print("\n--- Loading Skills ---")
            load_result = load_data_from_dataframe(df, 'Skills', engine)
            
            print("\n--- Loading Occupation_Skills ---")
            load_result = load_data_from_dataframe(df, 'Occupation_Skills', engine)
        
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
        
        tables_to_verify = ['Occupations', 'Skills', 'Occupation_Skills']
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
