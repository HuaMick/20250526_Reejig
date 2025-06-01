"""
LLM-Enhanced Skill Gap Analysis function that provides detailed gap descriptions.
"""
import os
from typing import Optional
from sqlalchemy.engine import Engine
from src.config.schemas import get_sqlalchemy_engine
from src.functions.get_occupation_and_skills import get_occupation_and_skills
from src.functions.generate_skill_proficiency_prompt import generate_skill_proficiency_prompt
from src.functions.generate_skill_gap_analysis_prompt import generate_skill_gap_analysis_prompt
from src.functions.gemini_llm_request import gemini_llm_request

def get_skills_gap_by_lvl_llm(from_onet_soc_code: str, to_onet_soc_code: str, engine: Optional[Engine] = None):
    """
    Identifies skills required by the target occupation that the source occupation either does not have 
    or where the proficiency level is lower than in the target occupation, with LLM-generated descriptions.
    
    This function:
    1. Retrieves detailed skills data for both occupations using get_occupation_and_skills (with API fallback)
    2. Calls LLM to assess proficiency levels for both occupations
    3. Uses LLM to generate detailed skill gap analysis with descriptions
    4. Returns comprehensive assessment with LLM-enhanced gap descriptions
    
    Args:
        from_onet_soc_code (str): The O*NET-SOC code for the source occupation
        to_onet_soc_code (str): The O*NET-SOC code for the target occupation
        engine (Optional[Engine]): SQLAlchemy engine to use for database operations, 
                                   or None to use the default engine
    
    Returns:
        dict: {
            "success": bool,
            "message": str,
            "result": [
                {
                    "element_id": str,
                    "skill_name": str,
                    "from_proficiency_level": float/int,
                    "to_proficiency_level": float/int,
                    "llm_gap_description": str
                },
                ...
            ]
        }
    """
    try:
        # If no engine is provided, get the default one
        if engine is None:
            engine = get_sqlalchemy_engine()
            
        # Retrieve detailed data for both occupations (with API fallback)
        from_occupation_response = get_occupation_and_skills(from_onet_soc_code, engine=engine)
        to_occupation_response = get_occupation_and_skills(to_onet_soc_code, engine=engine)
        
        # Check if both queries were successful
        if not from_occupation_response["success"]:
            return {
                "success": False,
                "message": f"Error retrieving source occupation data: {from_occupation_response['message']}",
                "result": []
            }
            
        if not to_occupation_response["success"]:
            return {
                "success": False,
                "message": f"Error retrieving target occupation data: {to_occupation_response['message']}",
                "result": []
            }
        
        # Extract occupation data for LLM processing
        from_occupation_data = from_occupation_response["result"]["occupation_data"]
        to_occupation_data = to_occupation_response["result"]["occupation_data"]
        
        # Step 1: Generate LLM proficiency assessments for source occupation
        from_prompt_result = generate_skill_proficiency_prompt(
            occupation_data=from_occupation_data,
        )
        
        if not from_prompt_result["success"]:
            return {
                "success": False,
                "message": f"Error generating LLM prompt for source occupation: {from_prompt_result['message']}",
                "result": []
            }
        
        # Prepare skills data for LLM request (source occupation)
        from_prompt_skills_data = [
            {
                "skill_element_id": skill["skill_element_id"],
                "skill_name": skill["skill_name"]
            }
            for skill in from_occupation_data["skills"]
        ]
        
        # Call LLM for source occupation proficiency assessment
        from_llm_response = gemini_llm_request(
            prompt=from_prompt_result["result"]["prompt"],
            request_onet_soc_code=from_onet_soc_code,
            prompt_skills_data=from_prompt_skills_data,
            expected_response_type="skill_proficiency"
        )
        
        if not from_llm_response["success"]:
            return {
                "success": False,
                "message": f"Error getting LLM assessment for source occupation: {from_llm_response['message']}",
                "result": []
            }
        
        # Step 2: Generate LLM proficiency assessments for target occupation
        to_prompt_result = generate_skill_proficiency_prompt(
            occupation_data=to_occupation_data,
        )
        
        if not to_prompt_result["success"]:
            return {
                "success": False,
                "message": f"Error generating LLM prompt for target occupation: {to_prompt_result['message']}",
                "result": []
            }
        
        # Prepare skills data for LLM request (target occupation)
        to_prompt_skills_data = [
            {
                "skill_element_id": skill["skill_element_id"],
                "skill_name": skill["skill_name"]
            }
            for skill in to_occupation_data["skills"]
        ]
        
        # Call LLM for target occupation proficiency assessment
        to_llm_response = gemini_llm_request(
            prompt=to_prompt_result["result"]["prompt"],
            request_onet_soc_code=to_onet_soc_code,
            prompt_skills_data=to_prompt_skills_data,
            expected_response_type="skill_proficiency"
        )
        
        if not to_llm_response["success"]:
            return {
                "success": False,
                "message": f"Error getting LLM assessment for target occupation: {to_llm_response['message']}",
                "result": []
            }
        
        # Step 3: Process LLM responses and prepare data for gap analysis
        from_llm_skills = {}
        for skill_assessment in from_llm_response["result"]["reply_data"]:
            skill_name = skill_assessment["llm_skill_name"]
            proficiency_level = skill_assessment["llm_assigned_proficiency_level"]
            if skill_name and proficiency_level is not None:
                from_llm_skills[skill_name] = proficiency_level
        
        to_llm_skills = {}
        to_skill_elements = {}  # Map skill name to element_id
        for skill_assessment in to_llm_response["result"]["reply_data"]:
            skill_name = skill_assessment["llm_skill_name"]
            proficiency_level = skill_assessment["llm_assigned_proficiency_level"]
            if skill_name and proficiency_level is not None:
                to_llm_skills[skill_name] = proficiency_level
                # Find corresponding element_id from original skill data
                for original_skill in to_occupation_data["skills"]:
                    if original_skill["skill_name"] == skill_name:
                        to_skill_elements[skill_name] = original_skill["skill_element_id"]
                        break
        
        # Step 4: Create enhanced occupation data with LLM proficiency levels for gap analysis prompt
        enhanced_from_data = {
            "onet_id": from_occupation_data["onet_id"],
            "name": from_occupation_data["name"],
            "skills": []
        }
        
        enhanced_to_data = {
            "onet_id": to_occupation_data["onet_id"],
            "name": to_occupation_data["name"],
            "skills": []
        }
        
        # Add LLM-assessed skills to enhanced data
        for skill_name, proficiency in from_llm_skills.items():
            enhanced_from_data["skills"].append({
                "skill_name": skill_name,
                "proficiency_level": proficiency
            })
        
        for skill_name, proficiency in to_llm_skills.items():
            enhanced_to_data["skills"].append({
                "skill_name": skill_name,
                "proficiency_level": proficiency
            })
        
        # Step 5: Generate skill gap analysis prompt with LLM-assessed proficiencies
        gap_prompt_result = generate_skill_gap_analysis_prompt(
            to_occupation_data=enhanced_to_data,
            from_occupation_data=enhanced_from_data,
        )
        
        if not gap_prompt_result["success"]:
            return {
                "success": False,
                "message": f"Error generating skill gap analysis prompt: {gap_prompt_result['message']}",
                "result": []
            }
        
        # Prepare skills data for gap analysis LLM request
        gap_prompt_skills_data = [
            {
                "skill_element_id": to_skill_elements.get(skill["skill_name"], "unknown"),
                "skill_name": skill["skill_name"]
            }
            for skill in enhanced_to_data["skills"]
        ]
        
        # Step 6: Call LLM for skill gap analysis
        gap_llm_response = gemini_llm_request(
            prompt=gap_prompt_result["result"]["prompt"],
            request_onet_soc_code=to_onet_soc_code,
            prompt_skills_data=gap_prompt_skills_data,
            expected_response_type="skill_gap_analysis"
        )
        
        if not gap_llm_response["success"]:
            return {
                "success": False,
                "message": f"Error getting LLM skill gap analysis: {gap_llm_response['message']}",
                "result": []
            }
        
        # Step 7: Parse LLM gap analysis response and format results
        skill_gaps_result = []
        
        try:
            # Try to extract gap descriptions from LLM response
            llm_gap_descriptions = {}
            if "raw_response" in gap_llm_response["result"] and gap_llm_response["result"]["raw_response"]:
                raw_response = gap_llm_response["result"]["raw_response"]
                if "skill_gap_analysis" in raw_response and "skill_gaps" in raw_response["skill_gap_analysis"]:
                    for gap_info in raw_response["skill_gap_analysis"]["skill_gaps"]:
                        skill_name = gap_info.get("skill_name")
                        gap_description = gap_info.get("gap_description")
                        if skill_name and gap_description:
                            llm_gap_descriptions[skill_name] = gap_description
            
            # Build final result using LLM proficiency data and descriptions
            for skill_name, to_proficiency in to_llm_skills.items():
                from_proficiency = from_llm_skills.get(skill_name, 0)
                
                # Only include skills where there's a gap (to > from or skill missing from source)
                if to_proficiency > from_proficiency:
                    element_id = to_skill_elements.get(skill_name, "unknown")
                    
                    # Use LLM-generated gap description if available, otherwise create a basic one
                    gap_description = llm_gap_descriptions.get(
                        skill_name,
                        f"Target occupation requires {skill_name} at level {to_proficiency}/7, while source occupation has level {from_proficiency}/7. Development needed to bridge this {to_proficiency - from_proficiency} level gap."
                    )
                    
                    skill_gaps_result.append({
                        "element_id": element_id,
                        "skill_name": skill_name,
                        "from_proficiency_level": from_proficiency,
                        "to_proficiency_level": to_proficiency,
                        "llm_gap_description": gap_description
                    })
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing LLM gap analysis results: {str(e)}",
                "result": []
            }
        
        return {
            "success": True,
            "message": f"Successfully identified {len(skill_gaps_result)} skill gaps with LLM-enhanced descriptions between '{enhanced_from_data['name']}' and '{enhanced_to_data['name']}'",
            "result": skill_gaps_result
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in LLM-enhanced skill gap analysis: {str(e)}",
            "result": []
        }


if __name__ == '__main__':
    print("Testing get_skills_gap_by_lvl_llm function with real occupation codes:")
    print("This example assumes GEMINI_API_KEY environment variable is set and valid O*NET data is available.")
    
    # Using the occupation codes identified as having different skills (after filtering level=0)
    from_occupation = "11-1011.00"  # Chief Executives
    to_occupation = "11-2021.00"    # Marketing Managers
    
    # Get default engine for testing
    default_engine = get_sqlalchemy_engine()
    
    # Call the function with default engine
    print(f"\n--- Identifying LLM-enhanced skill gap from '{from_occupation}' to '{to_occupation}' ---")
    result = get_skills_gap_by_lvl_llm(from_occupation, to_occupation, engine=default_engine)
    
    # Print the results
    print("\nFunction Call Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    if result['success']:
        print(f"  Number of skill gaps identified: {len(result['result'])}")
        
        if result['result']:
            print("\n  LLM-Enhanced Skill Gaps:")
            for gap in result['result']:
                print(f"    - Skill: {gap['skill_name']} (ID: {gap['element_id']})")
                print(f"      From Level: {gap['from_proficiency_level']}, To Level: {gap['to_proficiency_level']}")
                print(f"      LLM Description: {gap['llm_gap_description']}")
                print()
    
    print("Example finished.") 