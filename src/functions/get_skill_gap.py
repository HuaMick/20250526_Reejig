import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text # For direct SQL execution if needed for complex queries, though ORM is preferred

# Add project root to sys.path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config.schemas import get_sqlalchemy_engine, Occupation, Skill, OccupationSkill
from src.functions.mysql_connection import get_mysql_connection # For direct verification if needed

def get_skill_gap(occupation_code1: str, occupation_code2: str):
    """
    Calculates the skill gap between two occupations.
    A skill gap is defined as skills required for occupation_code2 that are not required for occupation_code1.

    Args:
        occupation_code1 (str): The O*NET-SOC code of the 'from' occupation.
        occupation_code2 (str): The O*NET-SOC code of the 'to' occupation.

    Returns:
        dict: A dictionary with keys 'success' (bool), 'message' (str),
              and 'result' (dict containing 'skill_gaps' as a list of dicts
              e.g., {"element_id": "...", "element_name": "..."}).
    """
    engine = None
    try:
        engine = get_sqlalchemy_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        # Verify both occupation codes exist
        occ1 = session.query(Occupation).filter(Occupation.onet_soc_code == occupation_code1).first()
        occ2 = session.query(Occupation).filter(Occupation.onet_soc_code == occupation_code2).first()

        if not occ1:
            session.close()
            return {"success": False, "message": f"Occupation code {occupation_code1} not found.", "result": {}}
        if not occ2:
            session.close()
            return {"success": False, "message": f"Occupation code {occupation_code2} not found.", "result": {}}

        # Get skills for occupation 1
        occ1_skills_query = session.query(OccupationSkill.element_id).filter(OccupationSkill.onet_soc_code == occupation_code1)
        occ1_skill_ids = {row.element_id for row in occ1_skills_query.all()}

        # Get skills for occupation 2
        occ2_skills_query = session.query(OccupationSkill.element_id).filter(OccupationSkill.onet_soc_code == occupation_code2)
        occ2_skill_ids = {row.element_id for row in occ2_skills_query.all()}

        # Find skill IDs that are in occ2_skill_ids but not in occ1_skill_ids
        gap_skill_ids = occ2_skill_ids - occ1_skill_ids

        skill_gaps_result = []
        if gap_skill_ids:
            # Get names for the gap skills
            gap_skills_details_query = session.query(Skill.element_id, Skill.element_name).filter(Skill.element_id.in_(gap_skill_ids))
            skill_gaps_result = [{"element_id": s.element_id, "element_name": s.element_name} for s in gap_skills_details_query.all()]

        session.close()
        return {
            "success": True,
            "message": f"Successfully retrieved skill gap from '{occ1.title}' to '{occ2.title}'.",
            "result": {"skill_gaps": skill_gaps_result, "from_occupation_title": occ1.title, "to_occupation_title": occ2.title}
        }

    except Exception as e:
        if 'session' in locals() and session is not None:
            session.close()
        return {"success": False, "message": f"Error calculating skill gap: {e}", "result": {}}

if __name__ == '__main__':
    print("Running skill gap analysis example...")

    # This example assumes that the database has been populated by mysql_load.py
    # You might need to run `python src/functions/mysql_load.py` first.

    # Example O*NET codes (replace with actual codes from your loaded data for a meaningful test)
    # For this example, we'll try to find some codes that might have differences.
    # Let's pick from the initially loaded data if available.
    # From occupations.txt:
    # 11-1011.00 Chief Executives
    # 11-1021.00 General and Operations Managers
    # 15-1252.00 Software Developers
    # 15-1242.00 Database Administrators

    example_occ_code1 = "15-1252.00" # Software Developers
    example_occ_code2 = "15-1242.00" # Database Administrators
    
    # A more distinct example if data allows:
    # example_occ_code1 = "29-2061.00" # Medical Assistants
    # example_occ_code2 = "15-1252.00" # Software Developers
    
    # For initial test, use codes more likely to exist from default load
    print(f"Attempting to find skill gap from occupation {example_occ_code1} to {example_occ_code2}")

    gap_result = get_skill_gap(example_occ_code1, example_occ_code2)

    if gap_result["success"]:
        print(f"Message: {gap_result['message']}")
        from_title = gap_result['result'].get('from_occupation_title', example_occ_code1)
        to_title = gap_result['result'].get('to_occupation_title', example_occ_code2)
        print(f"Skill gap from '{from_title}' to '{to_title}':")
        
        if gap_result["result"]["skill_gaps"]:
            for skill in gap_result["result"]["skill_gaps"]:
                print(f"  - Skill ID: {skill['element_id']}, Name: {skill['element_name']}")
        else:
            print("  No skill gaps found, or one/both occupations have no skills defined.")
    else:
        print(f"Error: {gap_result['message']}")

    print("\n--- Another example: Identical occupations (should be no gap) ---")
    example_occ_code_identical = "11-1011.00" # Chief Executives
    if os.getenv("MYSQL_DATABASE"): # Quick check if DB might be populated
        gap_result_identical = get_skill_gap(example_occ_code_identical, example_occ_code_identical)
        if gap_result_identical["success"]:
            from_title = gap_result_identical['result'].get('from_occupation_title', example_occ_code_identical)
            to_title = gap_result_identical['result'].get('to_occupation_title', example_occ_code_identical)
            print(f"Skill gap from '{from_title}' to '{to_title}':")
            if gap_result_identical["result"]["skill_gaps"]:
                for skill in gap_result_identical["result"]["skill_gaps"]:
                    print(f"  - Skill ID: {skill['element_id']}, Name: {skill['element_name']}")
            else:
                print("  No skill gaps found, as expected.")
        else:
            print(f"Error fetching gap for identical codes: {gap_result_identical['message']}")
    else:
        print(f"Skipping identical occupation test as MYSQL_DATABASE env var not set (implies DB might not be ready).") 