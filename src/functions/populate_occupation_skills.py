import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from typing import Dict, Any, Optional
from sqlalchemy.engine import Engine

from src.config.schemas import get_sqlalchemy_engine, Onet_Skills_Landing, Occupation_Skills

def populate_occupation_skills(source: str = 'text_file', engine: Optional[Engine] = None) -> Dict[str, Any]:
    """
    Populates the OccupationSkills table from the raw Skills table.
    
    This function:
    1. Extracts occupation-skill relationships with LV scale from the Skills table
    2. Populates the OccupationSkills table with these relationships
    
    Args:
        source (str): Source of the data. Default is 'text_file'.
                     Other possible values: 'api', 'merged'
        engine (Optional[Engine]): SQLAlchemy engine to use for database operations,
                                  or None to use the default engine
    
    Returns:
        Dict[str, Any]: A dictionary with keys:
            - 'success' (bool): Whether the operation was successful
            - 'message' (str): A message describing the result
            - 'result' (Dict): Statistics about the operation
    """
    try:
        # If no engine is provided, get the default one
        if engine is None:
            engine = get_sqlalchemy_engine()
            
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Current date for the last_updated field
        current_date = datetime.now().date()
        
        # Extract occupation-skill relationships with LV scale from Skills table
        print("Extracting occupation-skill relationships with LV scale...")
        lv_skills_query = (
            select(
                Onet_Skills_Landing.onet_soc_code,
                Onet_Skills_Landing.element_id,
                Onet_Skills_Landing.data_value
            )
            .where(Onet_Skills_Landing.scale_id == 'LV')
        )
        lv_skills = session.execute(lv_skills_query).all()
        
        # Clear existing data in OccupationSkills if needed
        session.query(Occupation_Skills).delete()
        session.commit()
        
        # Insert into OccupationSkills
        occ_skills = []
        for onet_soc_code, element_id, data_value in lv_skills:
            if data_value is not None:  # Ensure we have a valid proficiency level
                occ_skill = Occupation_Skills(
                    onet_soc_code=onet_soc_code,
                    element_id=element_id,
                    proficiency_level=data_value,
                    source=source,
                    last_updated=current_date
                )
                occ_skills.append(occ_skill)
        
        session.add_all(occ_skills)
        session.commit()
        skills_count = len(occ_skills)
        print(f"Inserted {skills_count} occupation-skill relationships into OccupationSkills")
        
        return {
            "success": True,
            "message": f"Successfully populated OccupationSkills table from {source} data.",
            "result": {
                "occupation_skills_count": skills_count
            }
        }
    
    except Exception as e:
        error_message = f"Error populating OccupationSkills table: {str(e)}"
        print(error_message)
        return {
            "success": False,
            "message": error_message,
            "result": {}
        }
    finally:
        session.close()

if __name__ == "__main__":
    print("Minimalistic happy path example for populate_occupation_skills:")
    print("This example assumes a populated database with O*NET raw data.")
    
    # Get default engine for testing
    default_engine = get_sqlalchemy_engine()
    
    # Call the function
    result = populate_occupation_skills(engine=default_engine)
    
    # Print the result
    print("\nFunction Call Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    print(f"  Statistics:")
    for key, value in result.get('result', {}).items():
        print(f"    - {key}: {value}")
    
    print("\nExample finished.") 