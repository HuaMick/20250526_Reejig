import os
import sys
from datetime import datetime
from src.functions.populate_skills_reference import populate_skills_reference
from src.functions.populate_occupation_skills import populate_occupation_skills
from src.config.schemas import get_sqlalchemy_engine


def main():
    """
    Main function to orchestrate the transformation of raw O*NET data 
    into the normalized downstream tables.
    
    This process:
    1. Populates the SkillsReference table from unique skills in the raw Skills table
    2. Populates the OccupationSkills table from the occupation-skill relationships in the raw Skills table
    """
    print("Starting O*NET data transformation process...")
    
    # Step 1: Get the data source info
    source = os.getenv("DATA_SOURCE", "text_file")  # Default to 'text_file' if not specified
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"\n--- Using data source: {source} ---")
    print(f"--- Processing date: {current_date} ---")

    # Step 2: Populate SkillsReference table
    print("\n--- Populating SkillsReference Table ---")
    skills_ref_result = populate_skills_reference(source=source)
    print(f"SkillsReference population: {skills_ref_result['message']}")
    
    if not skills_ref_result['success']:
        print("CRITICAL ERROR: Failed to populate SkillsReference table. Stopping transformation.")
        sys.exit(1)
    
    skills_count = skills_ref_result['result'].get('skills_reference_count', 0)
    print(f"Successfully added {skills_count} unique skills to SkillsReference table.")

    # Step 3: Populate OccupationSkills table
    print("\n--- Populating OccupationSkills Table ---")
    occ_skills_result = populate_occupation_skills(source=source)
    print(f"OccupationSkills population: {occ_skills_result['message']}")
    
    if not occ_skills_result['success']:
        print("CRITICAL ERROR: Failed to populate OccupationSkills table. Stopping transformation.")
        sys.exit(1)
    
    relationships_count = occ_skills_result['result'].get('occupation_skills_count', 0)
    print(f"Successfully added {relationships_count} occupation-skill relationships to OccupationSkills table.")

    # Step 4: Print summary
    print("\n--- Transformation Summary ---")
    print(f"Data source: {source}")
    print(f"Processing date: {current_date}")
    print(f"Skills reference entries: {skills_count}")
    print(f"Occupation-skill relationships: {relationships_count}")
    
    print("\nO*NET data transformation process completed successfully.")


if __name__ == '__main__':
    main()
