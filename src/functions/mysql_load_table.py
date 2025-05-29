import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError, DataError
import src.config.schemas as schemas # Import the schemas module
from src.config.schemas import Base # Keep Base for type hinting
import logging
from typing import Type # For type hinting SQLAlchemy model classes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data_from_dataframe(df: pd.DataFrame, model: Type[Base], engine, clear_existing: bool = True) -> dict:
    """
    Loads data from a pandas DataFrame into the specified table using its SQLAlchemy model.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to load.
        model (Type[Base]): The SQLAlchemy model class representing the target table.
        engine (sqlalchemy.engine.base.Engine): SQLAlchemy engine for database connection.
        clear_existing (bool): Whether to clear existing data before loading. Defaults to True.

    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str), and 'result' (dict).
    """
    actual_table_name = model.__tablename__

    if df.empty:
        logging.info(f"DataFrame for table '{actual_table_name}' is empty. No records to load.")
        return {
            "success": True,
            "message": f"No records to load into {actual_table_name} as DataFrame is empty.",
            "result": {"records_loaded": 0}
        }

    inspector = inspect(model)
    model_column_names = {c.name for c in inspector.columns}
    
    # Infer required columns: non-nullable and not primary key (assuming PK might be auto-gen)
    # This is a heuristic. True "required-ness" can depend on defaults, etc.
    inferred_required_columns = {
        c.name for c in inspector.columns 
        if not c.nullable and not c.primary_key
    }
    # Also add non-nullable primary keys if they are not autoincremented
    for pk_col in inspector.primary_key:
        if not pk_col.nullable and not pk_col.autoincrement:
            inferred_required_columns.add(pk_col.name)

    df_columns = set(df.columns)
    missing_required_cols = inferred_required_columns - df_columns

    if missing_required_cols:
        msg = f"DataFrame for table '{actual_table_name}' is missing inferred required columns: {sorted(list(missing_required_cols))}. Non-nullable (non-PK or non-autoPK) model columns: {sorted(list(inferred_required_columns))}"
        logging.error(msg)
        return {"success": False, "message": msg, "result": {}}

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        df_cleaned = df.where(pd.notnull(df), None)
        
        df_load_cols = [col for col in df_cleaned.columns if col in model_column_names]
        if not df_load_cols:
            session.close()
            msg = f"No matching columns found between DataFrame and table '{actual_table_name}'. Model columns: {sorted(list(model_column_names))}. DataFrame columns: {sorted(list(df_columns))}."
            logging.error(msg)
            return {"success": False, "message": msg, "result": {}}
            
        records_df = df_cleaned[df_load_cols]
        records = records_df.to_dict(orient='records')

        if clear_existing:
            try:
                logging.info(f"Clearing existing data from table '{actual_table_name}'...")
                session.query(model).delete()
                session.commit()
                logging.info(f"Successfully cleared table '{actual_table_name}'.")
            except Exception as e:
                session.rollback()
                session.close()
                logging.error(f"Error clearing table '{actual_table_name}': {e}")
                return {"success": False, "message": f"Error clearing table '{actual_table_name}': {e}", "result": {}}

        logging.info(f"Loading {len(records)} records into '{actual_table_name}'...")
        session.bulk_insert_mappings(model, records)
        session.commit()
        
        num_records_loaded = len(records)
        logging.info(f"Successfully loaded {num_records_loaded} records into '{actual_table_name}'.")
        return {
            "success": True, 
            "message": f"Successfully loaded {num_records_loaded} records into {actual_table_name}", 
            "result": {"records_loaded": num_records_loaded}
        }

    except (IntegrityError, DataError) as db_err: # Catch specific database errors
        session.rollback()
        logging.error(f"Database error loading data into '{actual_table_name}': {db_err}")
        return {"success": False, "message": f"Database error loading data into {actual_table_name}: {db_err}", "result": {}}
    except Exception as e:
        session.rollback()
        logging.error(f"An unexpected error occurred loading data into '{actual_table_name}': {e}")
        return {"success": False, "message": f"An unexpected error occurred loading data into {actual_table_name}: {e}", "result": {}}
    finally:
        session.close()

if __name__ == '__main__':
    print("Minimalistic happy path example for load_data_from_dataframe.")
    print("This example loads sample data into the 'Onet_Occupations_API_landing' table using an in-memory SQLite database.")

    # Imports for the __main__ example
    from sqlalchemy import create_engine # For the example engine
    import pandas as pd # For creating a sample DataFrame
    from datetime import date # For sample date data
    # The 'schemas' module (aliased) and 'Base' are imported at the top of the file.

    # 1. Setup: In-memory SQLite engine. 
    #    Base.metadata.create_all will create all tables defined in schemas.py that inherit from Base.
    example_engine = create_engine("sqlite:///:memory:")
    schemas.Base.metadata.create_all(example_engine) 

    # 2. Prepare sample data for the Onet_Occupations_API_landing table
    sample_api_df = pd.DataFrame({
        'onet_soc_code': ['API001.00', 'API002.00'], 
        'title': ['API Developer', 'API Analyst'], 
        'description': ['Develops and maintains APIs.', 'Analyzes API performance and usage.'],
        'last_updated': [date(2024, 1, 15), date(2024, 1, 16)],
        'extra_column_to_be_ignored': ['extra_data_1', 'extra_data_2'] # This column is not in the schema and will be ignored
    })
    
    # 3. Call the function to load data
    print("\nAttempting to load data into Onet_Occupations_API_landing table...")
    load_result = load_data_from_dataframe(
        df=sample_api_df, 
        model=schemas.Onet_Occupations_API_landing, # Accessing the model via the 'schemas' alias
        engine=example_engine, 
        clear_existing=True
    )
    
    # 4. Print the result from the function call
    print("\nFunction Call Result:")
    print(load_result)

    if load_result["success"]:
        print(f"Successfully loaded {load_result['result'].get('records_loaded', 0)} records.")
        # Optionally, you could query the table here to verify, but for a minimalistic example, this is sufficient.
    else:
        print(f"Failed to load data. Message: {load_result['message']}")

    print("\nExample finished.")
