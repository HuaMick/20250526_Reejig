"""
Generate a prompt for the LLM to assess skill proficiency levels for occupation transitions.
"""
from typing import Dict, List, Any, Optional

def gemini_llm_prompt(
    occupation_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate a prompt for the LLM to assess skill proficiency levels for a target occupation.

    Args:
        occupation_data (Dict[str, Any]): Dictionary containing target occupation data with structure:
            {
                "onet_id": str,
                "name": str,
                "skills": [{"skill_element_id": str, "skill_name": str, "proficiency_level": float}, ...]
            }

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


if __name__ == "__main__":
    print("Minimalistic happy path example for gemini_llm_prompt:")
    
    # Define sample data
    example_occupation_data = {
        "onet_id": "15-1252.00",
        "name": "Software Developer",
        "skills": [
            {"skill_name": "Programming", "proficiency_level": 5.0},
            {"skill_name": "Problem Solving", "proficiency_level": 4.5},
            {"skill_name": "Communication", "proficiency_level": 3.8}
        ]
    }
    
    example_occupation_no_skills = {
        "onet_id": "10-1010.10",
        "name": "Manager of Things",
        "skills": []
    }

    # Call the function with the occupation data
    result1 = gemini_llm_prompt(occupation_data=example_occupation_data)
    
    # Print the results
    print("\nFunction Call Result (with skills):")
    print(f"  Success: {result1['success']}")
    print(f"  Message: {result1['message']}")
    if result1['success']:
        # print(f"  Prompt:\n{result1['result']['prompt']}") # Full prompt can be long
        print(f"  Prompt (first 300 chars): {result1['result']['prompt'][:300]}...")

    result2 = gemini_llm_prompt(occupation_data=example_occupation_no_skills)
    print("\nFunction Call Result (no skills listed):")
    print(f"  Success: {result2['success']}")
    print(f"  Message: {result2['message']}")
    if result2['success']:
        print(f"  Prompt (first 300 chars): {result2['result']['prompt'][:300]}...")

    
    print("\nExample finished.") 