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
    print("Minimalistic happy path example for load_data_from_dataframe:")
    print("Loads a tiny sample DataFrame into an in-memory SQLite 'Occupations' table.")

    from sqlalchemy import create_engine
    import pandas as pd
    from src.config.schemas import Base, Occupation # For table creation

    # 1. Setup: In-memory SQLite engine and create a table
    example_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(example_engine) # Create tables defined in Base (e.g., Occupation)

    # 2. Prepare sample data and DataFrame
    sample_df = pd.DataFrame({
        'onet_soc_code': ['HP001.00'], 
        'title': ['Happy Path Tester'], 
        'description': ['Tests happy paths.']
    })

    # 3. Call the function
    print("\nCalling load_data_from_dataframe...")
    load_result = load_data_from_dataframe(
        df=sample_df, 
        table_name='Occupations', 
        engine=example_engine, 
        clear_existing=True
    )
    
    # 4. Print the raw result from the function
    print("\nFunction Call Result:")
    print(load_result)
    print("\nExample finished.")
