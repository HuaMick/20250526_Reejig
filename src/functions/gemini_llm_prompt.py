"""
Generate a prompt for the LLM to assess skill proficiency levels for occupation transitions.
"""
from typing import Dict, List, Any, Optional

def gemini_llm_prompt(
    occupation_data: Dict[str, Any],
    from_occupation_data: Optional[Dict[str, Any]] = None,
    prompt_type: str = "skill_proficiency"
) -> Dict[str, Any]:
    """
    Generate a prompt for the LLM to assess skill proficiency levels or skill gap analysis.

    Args:
        occupation_data (Dict[str, Any]): Dictionary containing target occupation data with structure:
            {
                "onet_id": str,
                "name": str,
                "skills": [{"skill_element_id": str, "skill_name": str, "proficiency_level": float}, ...]
            }
        from_occupation_data (Optional[Dict[str, Any]]): Dictionary containing source occupation data for comparison.
            Same structure as occupation_data. Used for skill gap analysis prompts.
        prompt_type (str): Type of prompt to generate. Options:
            - "skill_proficiency": Generate skill proficiency assessment prompt
            - "skill_gap_analysis": Generate skill gap analysis prompt (requires from_occupation_data)

    Returns:
        Dict[str, Any]: Standard response format with keys:
            - success (bool): Whether the prompt generation was successful
            - message (str): Status message or error description
            - result (dict): When successful, contains:
                - prompt (str): The generated prompt for the LLM
    """
    # Validate input parameters
    if not isinstance(occupation_data, dict) or \
       "onet_id" not in occupation_data or \
       "name" not in occupation_data or \
       "skills" not in occupation_data:
        return {
            "success": False,
            "message": "Invalid occupation_data format. Must contain onet_id, name, and skills keys."
        }
    
    if prompt_type == "skill_gap_analysis":
        if not from_occupation_data:
            return {
                "success": False,
                "message": "from_occupation_data is required for skill gap analysis prompts."
            }
        if not isinstance(from_occupation_data, dict) or \
           "onet_id" not in from_occupation_data or \
           "name" not in from_occupation_data or \
           "skills" not in from_occupation_data:
            return {
                "success": False,
                "message": "Invalid from_occupation_data format. Must contain onet_id, name, and skills keys."
            }
    
    if prompt_type == "skill_proficiency":
        return _generate_skill_proficiency_prompt(occupation_data)
    elif prompt_type == "skill_gap_analysis":
        return _generate_skill_gap_analysis_prompt(from_occupation_data, occupation_data)
    else:
        return {
            "success": False,
            "message": f"Invalid prompt_type: {prompt_type}. Must be 'skill_proficiency' or 'skill_gap_analysis'."
        }


def _generate_skill_proficiency_prompt(occupation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a skill proficiency assessment prompt for a single occupation."""
    # Build the prompt
    prompt = f"""
You are an expert in career transitions and occupational skill assessment.

I need you to analyze skills for a job and determine proficiency levels based on the information provided.

# Occupation Information
- O*NET ID: {occupation_data['onet_id']}
- Occupation Name: {occupation_data['name']}
- Skills Required:
"""
    
    # Add occupation skills
    if occupation_data['skills']:
        for skill in occupation_data['skills']:
            # Ensure skill_name is present and not None before adding to prompt
            skill_name = skill.get('skill_name')
            if skill_name:
                prompt += f"  - {skill_name}\n"
            else:
                # Optionally skip or add a placeholder if a skill_name is missing
                # For now, we'll just skip to avoid adding "None" to the prompt
                pass 
    else:
        prompt += "  - (No specific skills listed for this occupation)\n"
    
    # Add instructions for the LLM
    prompt += """

# Your Task:
1. Analyze the skills of the Occupation provided.
2. For each skill listed in the Occupation, determine a proficiency level.
   - Use a scale of 1-7 where 1 is Novice and 7 is Expert
   - Consider what level of proficiency would be typical/expected for someone in this occupation
3. Provide a detailed justification/explanation for each assigned proficiency level.
   - Your explanation should be in the context of the Occupation's typical duties and responsibilities.
"""
    
    # Add output format instructions
    prompt += """

# Output Format Requirements:
Your entire response must be a single, valid JSON object with this exact schema:
```json
{
  "skill_proficiency_assessment": {
    "llm_onet_soc_code": "string (O*NET code of the Occupation)",
    "llm_occupation_name": "string (Name of the Occupation)",
    "assessed_skills": [
      {
        "llm_skill_name": "string (Name of the skill)",
        "llm_assigned_proficiency_description": "string (e.g., 'Intermediate', 'Advanced', 'Expert')",
        "llm_assigned_proficiency_level": number (e.g., 3.5 on the 1-7 scale),
        "llm_explanation": "string (Your detailed reasoning for the assigned proficiency)"
      }
      // One object for each skill in the Occupation
    ]
  }
}
```

Ensure your response is properly formatted as valid JSON and includes all required fields.
"""
    
    return {
        "success": True,
        "message": "Successfully generated prompt for skill proficiency assessment",
        "result": {
            "prompt": prompt.strip()
        }
    }


def _generate_skill_gap_analysis_prompt(from_occupation_data: Dict[str, Any], to_occupation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a skill gap analysis prompt comparing two occupations with their assessed proficiency levels."""
    
    prompt = f"""
You are an expert in career transitions and skill gap analysis.

I need you to analyze the skill gaps between two occupations and provide detailed descriptions of what skills need development.

# Source Occupation (Current)
- O*NET ID: {from_occupation_data['onet_id']}
- Occupation Name: {from_occupation_data['name']}
- Skills and Proficiency Levels:
"""
    
    # Add source occupation skills with proficiency levels
    if from_occupation_data['skills']:
        for skill in from_occupation_data['skills']:
            skill_name = skill.get('skill_name')
            proficiency = skill.get('proficiency_level', 'Unknown')
            if skill_name:
                prompt += f"  - {skill_name}: {proficiency}/7\n"
    else:
        prompt += "  - (No specific skills listed for this occupation)\n"
    
    prompt += f"""

# Target Occupation (Desired)
- O*NET ID: {to_occupation_data['onet_id']}
- Occupation Name: {to_occupation_data['name']}
- Skills and Proficiency Levels:
"""
    
    # Add target occupation skills with proficiency levels
    if to_occupation_data['skills']:
        for skill in to_occupation_data['skills']:
            skill_name = skill.get('skill_name')
            proficiency = skill.get('proficiency_level', 'Unknown')
            if skill_name:
                prompt += f"  - {skill_name}: {proficiency}/7\n"
    else:
        prompt += "  - (No specific skills listed for this occupation)\n"
    
    prompt += """

# Your Task:
1. Compare the skills and proficiency levels between the source and target occupations.
2. Identify skills where there is a gap (target requires higher proficiency than source has, or skills missing from source).
3. For each skill gap identified, provide:
   - A clear description of what development is needed
   - Specific recommendations for bridging the gap
   - Context about why this skill is important for the target occupation
4. Focus on actionable insights that would help someone transition from the source to target occupation.

# Output Format Requirements:
Your entire response must be a single, valid JSON object with this exact schema:
```json
{
  "skill_gap_analysis": {
    "from_occupation": "string (Source occupation name)",
    "to_occupation": "string (Target occupation name)",
    "skill_gaps": [
      {
        "skill_name": "string (Name of the skill with a gap)",
        "from_proficiency_level": number (Current proficiency level, 0 if skill is missing),
        "to_proficiency_level": number (Required proficiency level for target occupation),
        "gap_description": "string (Detailed description of what development is needed and why this skill matters for the target occupation)"
      }
      // One object for each skill gap identified
    ]
  }
}
```

Ensure your response is properly formatted as valid JSON and includes all required fields.
"""
    
    return {
        "success": True,
        "message": "Successfully generated prompt for skill gap analysis",
        "result": {
            "prompt": prompt.strip()
        }
    }


if __name__ == "__main__":
    print("Minimalistic happy path example for gemini_llm_prompt:")
    
    # 1. Define sample occupation data (with skills)
    example_occupation_data = {
        "onet_id": "15-1252.00",
        "name": "Software Developer",
        "skills": [
            {"skill_name": "Programming", "proficiency_level": 5.0},
            {"skill_name": "Problem Solving", "proficiency_level": 4.5}
        ]
    }
    
    # 2. Call the function to generate the prompt
    prompt_result = gemini_llm_prompt(occupation_data=example_occupation_data)
    
    # 3. Print the result summary
    print("\nFunction Call Result:")
    print(f"  Success: {prompt_result['success']}")
    print(f"  Message: {prompt_result['message']}")
    if prompt_result['success'] and prompt_result['result']:
        # The full prompt can be very long, so we print a snippet.
        print(f"  Generated Prompt (first 100 chars): {prompt_result['result']['prompt'][:100]}...")
    
    print("\nExample finished.") 