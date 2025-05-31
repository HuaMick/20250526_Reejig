"""
Integration test for the node src/nodes/transform.py
"""
import os
import sys
import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime

# Add the parent directory to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.functions.populate_skills_reference import populate_skills_reference
from src.functions.populate_occupation_skills import populate_occupation_skills
from src.config.schemas import get_sqlalchemy_engine, Skills, Occupation_Skills
from tests.fixtures.db_config import test_db_config

def test_transform_node(test_db_config):
    """
    Integration test for the transform node which populates the normalized downstream tables
    from raw data tables.
    
    This test:
    1. Calls populate_skills_reference to populate the Skills table
    2. Calls populate_occupation_skills to populate the Occupation_Skills table
    3. Verifies the data in the downstream tables
    """
    print(f"\nUsing test database: {test_db_config['database']}")
    
    # Create a SQLAlchemy engine from the test_db_config
    engine = get_sqlalchemy_engine(
        db_name=test_db_config['database'],
        db_user=test_db_config['user'],
        db_password=test_db_config['password'],
        db_host=test_db_config['host'],
        db_port=test_db_config['port']
    )
    
    # Set the data source
    source = 'test'
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"\n--- Using data source: {source} ---")
    print(f"--- Processing date: {current_date} ---")
    
    # Step 1: Populate Skills table
    print("\n--- Populating Skills Table ---")
    skills_ref_result = populate_skills_reference(source=source, engine=engine)
    print(f"Skills population: {skills_ref_result['message']}")
    
    assert skills_ref_result['success'], f"Failed to populate Skills table: {skills_ref_result['message']}"
    skills_count = skills_ref_result['result'].get('skills_reference_count', 0)
    print(f"Successfully added {skills_count} unique skills to Skills table.")
    
    # Step 2: Populate Occupation_Skills table
    print("\n--- Populating Occupation_Skills Table ---")
    occ_skills_result = populate_occupation_skills(source=source, engine=engine)
    print(f"Occupation_Skills population: {occ_skills_result['message']}")
    
    assert occ_skills_result['success'], f"Failed to populate Occupation_Skills table: {occ_skills_result['message']}"
    relationships_count = occ_skills_result['result'].get('occupation_skills_count', 0)
    print(f"Successfully added {relationships_count} occupation-skill relationships to Occupation_Skills table.")
    
    # Step 3: Verify the data in the downstream tables
    print("\n--- Verifying Data in Downstream Tables ---")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check Skills table
        skills_count_query = text("SELECT COUNT(*) FROM skills")
        skills_count_result = session.execute(skills_count_query).scalar_one()
        print(f"Skills table contains {skills_count_result} records.")
        assert skills_count_result > 0, "Skills table should not be empty"
        
        # Get a sample skill
        sample_skill_query = text("SELECT element_id, element_name, source FROM skills LIMIT 1")
        sample_skill = session.execute(sample_skill_query).first()
        if sample_skill:
            print(f"Sample skill: {sample_skill.element_name} (ID: {sample_skill.element_id}, Source: {sample_skill.source})")
        
        # Check Occupation_Skills table
        occ_skills_count_query = text("SELECT COUNT(*) FROM occupation_skills")
        occ_skills_count_result = session.execute(occ_skills_count_query).scalar_one()
        print(f"Occupation_Skills table contains {occ_skills_count_result} records.")
        assert occ_skills_count_result > 0, "Occupation_Skills table should not be empty"
        
        # Get a sample occupation-skill relationship
        sample_occ_skill_query = text("""
            SELECT os.onet_soc_code, s.element_name, os.proficiency_level, os.source 
            FROM occupation_skills os
            JOIN skills s ON os.element_id = s.element_id
            LIMIT 1
        """)
        sample_occ_skill = session.execute(sample_occ_skill_query).first()
        if sample_occ_skill:
            print(f"Sample occupation-skill relationship: Occupation {sample_occ_skill.onet_soc_code} - "
                 f"Skill '{sample_occ_skill.element_name}' - Proficiency Level {sample_occ_skill.proficiency_level}")
        
        # Check source field is correctly set
        source_check_query = text(f"SELECT COUNT(*) FROM skills WHERE source = :source")
        source_check_result = session.execute(source_check_query, {"source": source}).scalar_one()
        print(f"Number of skills with source '{source}': {source_check_result}")
        assert source_check_result > 0, f"Expected at least one skill with source '{source}'"
        
        # Check relationship between Skills and Occupation_Skills
        join_check_query = text("""
            SELECT COUNT(*) FROM occupation_skills os
            JOIN skills s ON os.element_id = s.element_id
        """)
        join_check_result = session.execute(join_check_query).scalar_one()
        print(f"Number of valid occupation-skill relationships: {join_check_result}")
        assert join_check_result == occ_skills_count_result, "All Occupation_Skills records should have corresponding Skills entries"
        
    finally:
        session.close()
    
    print("\n--- Transform Integration Test Summary ---")
    print(f"Data source: {source}")
    print(f"Processing date: {current_date}")
    print(f"Skills entries: {skills_count_result}")
    print(f"Occupation-skill relationships: {occ_skills_count_result}")
    
    print("\nTransform integration test completed successfully.")