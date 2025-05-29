import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from typing import Dict, Any

from src.config.schemas import get_sqlalchemy_engine, Onet_Skills_Landing, Skills

def populate_skills_reference(source: str = 'text_file') -> Dict[str, Any]:
    """
    Populates the SkillsReference table from the raw Skills table.
    
    This function:
    1. Extracts unique skills from the Skills table
    2. Populates the SkillsReference table with these unique skills
    
    Args:
        source (str): Source of the data. Default is 'text_file'.
                     Other possible values: 'api', 'merged'
    
    Returns:
        Dict[str, Any]: A dictionary with keys:
            - 'success' (bool): Whether the operation was successful
            - 'message' (str): A message describing the result
            - 'result' (Dict): Statistics about the operation
    """
    try:
        engine = get_sqlalchemy_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Current date for the last_updated field
        current_date = datetime.now().date()
        
        # Step 1: Extract unique skills from Skills table and populate SkillsReference
        print("Extracting unique skills from Skills table...")
        unique_skills_query = (
            select(Onet_Skills_Landing.element_id, Onet_Skills_Landing.element_name)
            .group_by(Onet_Skills_Landing.element_id, Onet_Skills_Landing.element_name)
        )
        unique_skills = session.execute(unique_skills_query).all()
        
        # Clear existing data in SkillsReference if needed
        session.query(Skills).delete()
        session.commit()
        
        # Insert into SkillsReference
        skill_refs = []
        for element_id, element_name in unique_skills:
            skill_ref = Skills(
                element_id=element_id,
                element_name=element_name,
                source=source,
                last_updated=current_date
            )
            skill_refs.append(skill_ref)
        
        session.add_all(skill_refs)
        session.commit()
        skills_count = len(skill_refs)
        print(f"Inserted {skills_count} unique skills into SkillsReference")
        
        return {
            "success": True,
            "message": f"Successfully populated SkillsReference table from {source} data.",
            "result": {
                "skills_reference_count": skills_count
            }
        }
    
    except Exception as e:
        error_message = f"Error populating SkillsReference table: {str(e)}"
        print(error_message)
        return {
            "success": False,
            "message": error_message,
            "result": {}
        }
    finally:
        session.close()

if __name__ == "__main__":
    print("Minimalistic happy path example for populate_skills_reference:")
    print("This example assumes a populated database with O*NET raw data.")
    
    # Call the function
    result = populate_skills_reference()
    
    # Print the result
    print("\nFunction Call Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    print(f"  Statistics:")
    for key, value in result.get('result', {}).items():
        print(f"    - {key}: {value}")
    
    print("\nExample finished.") 