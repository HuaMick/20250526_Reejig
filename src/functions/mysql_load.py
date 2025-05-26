import os
import csv
import pandas as pd
from sqlalchemy.orm import sessionmaker
from src.config.schemas import Occupation, Skill, OccupationSkill, get_sqlalchemy_engine
from src.functions.mysql_connection import get_mysql_connection

def load_data_from_csv(csv_file_path, table_name, engine):
    """
    Loads data from a CSV or TSV file into the specified table using SQLAlchemy.

    Args:
        csv_file_path (str): The path to the CSV/TSV file.
        table_name (str): The name of the table to load data into.
                          Valid names are 'Occupations', 'Skills', 'Occupation_Skills'.
        engine (sqlalchemy.engine.base.Engine): SQLAlchemy engine for database connection.

    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str), and 'result' (dict).
    """
    if not os.path.exists(csv_file_path):
        return {"success": False, "message": f"File not found: {csv_file_path}", "result": {}}

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Determine separator: .txt from O*NET are usually tab-separated
        separator = '\t' if csv_file_path.endswith('.txt') else ','
        df = pd.read_csv(csv_file_path, sep=separator)

        # Rename columns to match SQLAlchemy schema if necessary (especially for O*NET files)
        # O*NET 'Element ID' -> schema 'element_id'
        # O*NET 'Element Name' -> schema 'element_name'
        # O*NET 'O*NET-SOC Code' -> schema 'onet_soc_code'
        # O*NET 'Scale ID' -> schema 'scale_id'
        # O*NET 'Data Value' -> schema 'data_value'
        # O*NET 'N' -> schema 'n_value'
        # O*NET 'Standard Error' -> schema 'standard_error'
        # O*NET 'Lower CI Bound' -> schema 'lower_ci_bound'
        # O*NET 'Upper CI Bound' -> schema 'upper_ci_bound'
        # O*NET 'Recommend Suppress' -> schema 'recommend_suppress'
        # O*NET 'Not Relevant' -> schema 'not_relevant'
        # O*NET 'Date' -> schema 'date_recorded'
        # O*NET 'Domain Source' -> schema 'domain_source'

        column_renames = {
            "O*NET-SOC Code": "onet_soc_code",
            "Title": "title",
            "Description": "description",
            "Element ID": "element_id",
            "Element Name": "element_name",
            "Scale ID": "scale_id",
            "Data Value": "data_value",
            "N": "n_value",
            "Standard Error": "standard_error",
            "Lower CI Bound": "lower_ci_bound",
            "Upper CI Bound": "upper_ci_bound",
            "Recommend Suppress": "recommend_suppress",
            "Not Relevant": "not_relevant",
            "Date": "date_recorded", # Ensure this matches your schema's date column name for Occupation_Skills
            "Domain Source": "domain_source"
        }
        df.rename(columns=column_renames, inplace=True)

        # Convert NaN to None for SQLAlchemy compatibility
        df = df.where(pd.notnull(df), None)

        if table_name == 'Occupations':
            model = Occupation
            # Ensure only relevant columns are selected if df has more
            df = df[['onet_soc_code', 'title', 'description']]
            records = df.to_dict(orient='records')
        elif table_name == 'Skills':
            model = Skill
            # For Skills table, we need unique element_id and element_name from skills.txt
            if 'element_id' in df.columns and 'element_name' in df.columns:
                df = df[['element_id', 'element_name']].drop_duplicates().reset_index(drop=True)
                records = df.to_dict(orient='records')
            else:
                session.close()
                return {"success": False, "message": "Skills file missing 'element_id' or 'element_name' columns after rename.", "result": {}}
        elif table_name == 'Occupation_Skills':
            model = OccupationSkill
            # Ensure all required columns for OccupationSkill are present
            required_cols = ['onet_soc_code', 'element_id', 'scale_id', 'data_value', 
                             'n_value', 'standard_error', 'lower_ci_bound', 'upper_ci_bound',
                             'recommend_suppress', 'not_relevant', 'date_recorded', 'domain_source']
            if not all(col in df.columns for col in required_cols):
                missing_cols = [col for col in required_cols if col not in df.columns]
                session.close()
                return {"success": False, "message": f"Occupation_Skills file missing required columns: {missing_cols}", "result": {}}
            df = df[required_cols]
            if 'date_recorded' in df.columns and df['date_recorded'].dtype == 'object':
                try:
                    df['date_recorded'] = pd.to_datetime(df['date_recorded'], errors='coerce')
                    df['date_recorded'] = df['date_recorded'].where(pd.notnull(df['date_recorded']), None)
                except Exception as e:
                    print(f"Warning: Could not parse all 'date_recorded' values: {e}")
            
            # Convert DataFrame to list of dicts, then explicitly handle NaN/NaT again
            records = df.to_dict(orient='records')
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
        else:
            session.close()
            return {"success": False, "message": f"Invalid table name: {table_name}", "result": {}}

        if not records:
            session.close()
            return {
                "success": True, # Or False, depending on whether empty load is an error
                "message": f"No records to load into {table_name} from {csv_file_path}", 
                "result": {"records_loaded": 0}
            }

        # Clear the table before loading new data
        # This is often desired for an ETL load, but make sure it's what you want.
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
            "message": f"Successfully loaded {num_records_loaded} records into {table_name} from {csv_file_path}", 
            "result": {"records_loaded": num_records_loaded}
        }

    except Exception as e:
        session.rollback()
        session.close()
        return {"success": False, "message": f"Error loading data into {table_name}: {e}", "result": {}}

if __name__ == '__main__':
    print("Starting data loading process from O*NET .txt files...")

    # Define paths to the actual O*NET data files
    # These paths assume O*NET files are in a 'database' folder at the project root.
    # The 'database' folder was provided by the user.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    occupations_txt = os.path.join(project_root, 'database', 'occupations.txt')
    skills_txt = os.path.join(project_root, 'database', 'skills.txt') # This file serves both Skills and Occupation_Skills

    # Verify files exist
    if not os.path.exists(occupations_txt):
        print(f"ERROR: Occupations file not found at {occupations_txt}")
        exit(1)
    if not os.path.exists(skills_txt):
        print(f"ERROR: Skills file not found at {skills_txt}")
        exit(1)
    
    print(f"Using Occupations file: {occupations_txt}")
    print(f"Using Skills/Occupation_Skills file: {skills_txt}")

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

    # Initialize database tables (optional, but good for a clean load)
    # from src.functions.mysql_init_tables import initialize_database_tables
    # print("\n--- Initializing Database Tables (dropping existing) ---")
    # init_result = initialize_database_tables() # This will use the same engine settings
    # if init_result["success"]:
    #     print(init_result["message"])
    # else:
    #     print(f"Failed to initialize tables: {init_result['message']}")
    #     exit(1)

    # Load data into tables
    print("\n--- Loading Occupations ---")
    load_occ_result = load_data_from_csv(occupations_txt, 'Occupations', engine)
    print(load_occ_result['message'])
    if not load_occ_result['success']:
        print("Stopping due to error in loading Occupations.")
        exit(1)

    print("\n--- Loading Skills ---")
    # Skills data (Element ID, Element Name) is derived from skills_txt
    load_skill_result = load_data_from_csv(skills_txt, 'Skills', engine)
    print(load_skill_result['message'])
    if not load_skill_result['success']:
        print("Stopping due to error in loading Skills.")
        exit(1)
    
    print("\n--- Loading Occupation_Skills ---")
    # Occupation_Skills data (linking table) also comes from skills_txt
    load_occ_skill_result = load_data_from_csv(skills_txt, 'Occupation_Skills', engine)
    print(load_occ_skill_result['message'])
    if not load_occ_skill_result['success']:
        print("Stopping due to error in loading Occupation_Skills.")
        exit(1)

    # Verification (same as before, but now with real data)
    print("\n--- Verifying Data ---")
    connection_details = get_mysql_connection()
    if connection_details["success"]:
        connection = connection_details["result"]
        cursor = connection.cursor(dictionary=True) # Use dictionary=True for named columns
        
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
                            print(row) # Each row will be a dictionary
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
