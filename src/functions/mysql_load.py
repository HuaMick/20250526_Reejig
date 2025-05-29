import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.config.schemas import Occupation, Skill, Scale, get_sqlalchemy_engine, Base

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
            df_cols = [col for col in ['onet_soc_code', 'title', 'description'] if col in df.columns]
            if not all(c in df_cols for c in ['onet_soc_code', 'title']):
                 session.close()
                 return {"success": False, "message": f"DataFrame for Occupations table missing onet_soc_code or title", "result": {}}
            records = df[df_cols].to_dict(orient='records')
        elif table_name == 'Skills':
            model = Skill
            minimal_skill_cols = ['onet_soc_code', 'element_id', 'element_name', 'scale_id']
            if not all(col in df.columns for col in minimal_skill_cols):
                 session.close()
                 return {"success": False, "message": f"DataFrame for Skills table missing one or more essential columns: {minimal_skill_cols}", "result": {}}
            skill_model_cols = [c.name for c in Skill.__table__.columns]
            df_skill_load_cols = [col for col in df.columns if col in skill_model_cols]
            records = df[df_skill_load_cols].to_dict(orient='records')
        elif table_name == 'Scales':
            model = Scale
            df_cols = [col for col in ['scale_id', 'scale_name', 'minimum', 'maximum'] if col in df.columns]
            if not all(c in df_cols for c in ['scale_id', 'scale_name']):
                session.close()
                return {"success": False, "message": f"DataFrame for Scales table missing scale_id or scale_name", "result": {}}
            records = df[df_cols].to_dict(orient='records')
        else:
            session.close()
            return {"success": False, "message": f"Invalid table name: {table_name}", "result": {}}

        if clear_existing:
            try:
                session.query(model).delete()
                session.commit()
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
    print("Minimalistic example for load_data_from_dataframe function.")

    # This example requires a running MySQL database and tables to be initialized (e.g., via mysql_init_tables.py)
    # For simplicity, it uses an in-memory SQLite database for this example if env vars for MySQL are not fully set.

    db_user = os.getenv('MYSQL_USER')
    db_password = os.getenv('MYSQL_PASSWORD')
    db_name = os.getenv('MYSQL_DATABASE')
    db_host = os.getenv('MYSQL_HOST', 'localhost')
    db_port = os.getenv('MYSQL_PORT', '3306')

    engine_to_use = None
    is_sqlite_example = False

    if all([db_user, db_password, db_name]):
        try:
            print("Attempting to use MySQL from environment variables for example...")
            engine_to_use = get_sqlalchemy_engine()
            print("Using configured MySQL engine for example.")
        except ValueError as ve:
            print(f"MySQL environment variables not fully set or invalid ({ve}), falling back to SQLite for example.")
            engine_to_use = create_engine("sqlite:///:memory:")
            is_sqlite_example = True
        except Exception as e:
            print(f"Could not create MySQL engine for example ({e}), falling back to SQLite.")
            engine_to_use = create_engine("sqlite:///:memory:")
            is_sqlite_example = True
    else:
        print("MySQL environment variables not set, using in-memory SQLite for example.")
        engine_to_use = create_engine("sqlite:///:memory:")
        is_sqlite_example = True

    if is_sqlite_example:
        print("Using SQLite: Creating tables for example...")
        Base.metadata.create_all(engine_to_use)
        print("SQLite tables created for example.")

    sample_occupations_data = {
        'onet_soc_code': ['11-0000.00', '13-0000.00'],
        'title': ['Management Example', 'Business Example'],
        'description': ['Example description 1', 'Example description 2']
    }
    sample_occ_df = pd.DataFrame(sample_occupations_data)

    print(f"\n--- Loading sample data into Occupations table ({'SQLite' if is_sqlite_example else 'MySQL'}) ---")
    load_occ_result = load_data_from_dataframe(sample_occ_df, 'Occupations', engine_to_use, clear_existing=True)
    print(f"Load result: {load_occ_result}")

    sample_scales_data = {
        'scale_id': ['EX', 'TE'],
        'scale_name': ['Example Scale', 'Test Scale'],
        'minimum': [1, 0],
        'maximum': [5, 7]
    }
    sample_scales_df = pd.DataFrame(sample_scales_data)
    print(f"\n--- Loading sample data into Scales table ({'SQLite' if is_sqlite_example else 'MySQL'}) ---")
    load_scales_result = load_data_from_dataframe(sample_scales_df, 'Scales', engine_to_use, clear_existing=True)
    print(f"Load result: {load_scales_result}")

    print("\nExample finished.")
