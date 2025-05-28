import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from src.config.schemas import Occupation, Skill, Scale, get_sqlalchemy_engine
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
        df = df.where(pd.notnull(df), None)

        if table_name == 'Occupations':
            model = Occupation
            df = df[['onet_soc_code', 'title', 'description']]
            records = df.to_dict(orient='records')
        elif table_name == 'Skills':
            model = Skill
            required_skill_cols = [
                'onet_soc_code', 'element_id', 'element_name', 'scale_id', 'data_value',
                'n_value', 'standard_error', 'lower_ci_bound', 'upper_ci_bound',
                'recommend_suppress', 'not_relevant', 'date_recorded', 'domain_source'
            ]
            minimal_cols_present = [col for col in ['onet_soc_code', 'element_id', 'element_name', 'scale_id', 'data_value'] if col in df.columns]
            if len(minimal_cols_present) < 5: 
                 session.close()
                 missing_essential = list(set(['onet_soc_code', 'element_id', 'element_name', 'scale_id', 'data_value']) - set(df.columns))
                 return {"success": False, "message": f"DataFrame for Skills table missing essential columns: {missing_essential}", "result": {}}
            records = df.to_dict(orient='records')
        elif table_name == 'Scales':
            model = Scale
            df = df[['scale_id', 'scale_name', 'minimum', 'maximum']]
            records = df.to_dict(orient='records')
        else:
            session.close()
            return {"success": False, "message": f"Invalid table name: {table_name}", "result": {}}

        if clear_existing:
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

    print("\n--- Extracting O*NET Data ---")
    data_results = extract_onet_data()
    
    for result in data_results:
        filename = result['filename']
        df = result['df']
        
        table_name_to_load = None
        if filename == 'occupations.txt':
            table_name_to_load = 'Occupations'
            print(f"\n--- Loading {table_name_to_load} from {filename} ---")
        elif filename == 'skills.txt':
            table_name_to_load = 'Skills'
            print(f"\n--- Loading {table_name_to_load} from {filename} ---")
        elif filename == 'scales.txt':
            table_name_to_load = 'Scales'
            print(f"\n--- Loading {table_name_to_load} from {filename} ---")
        
        if table_name_to_load and not df.empty:
            load_result = load_data_from_dataframe(df, table_name_to_load, engine)
            print(load_result['message'])
            if not load_result['success']:
                print(f"Stopping due to error in loading data from {filename}.")
                exit(1)
        elif df.empty:
            print(f"Skipping {filename} as it resulted in an empty DataFrame.")
        else:
            print(f"Skipping {filename} as it is not configured for loading.")

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
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                    rows = cursor.fetchall()
                    if rows:
                        print(f"First {len(rows)} rows from '{table}':")
                        for row in rows:
                            if table == 'Skills' and len(row) > 5:
                                displayed_row = {k: v for i, (k, v) in enumerate(row.items()) if i < 5}
                                print(f"{displayed_row} ... (and more columns)")
                            else:
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
