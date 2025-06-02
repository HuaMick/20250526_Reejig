"""
Generate a prompt for the LLM to assess skill proficiency levels for occupation transitions.
"""
from typing import Dict, List, Any, Optional

def generate_skill_proficiency_prompt(occupation_data: Dict[str, Any]) -> Dict[str, Any]:
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

if __name__ == "__main__":
    print("Minimalistic happy path example for generate_skill_proficiency_prompt:")
    
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
    prompt_result = generate_skill_proficiency_prompt(occupation_data=example_occupation_data)
    
    # 3. Print the result summary
    print("\nFunction Call Result:")
    print(f"  Success: {prompt_result['success']}")
    print(f"  Message: {prompt_result['message']}")
    if prompt_result['success'] and prompt_result['result']:
        # The full prompt can be very long, so we print a snippet.
        print(f"  Generated Prompt (first 100 chars): {prompt_result['result']['prompt'][:100]}...")
    
    print("\nExample finished.")