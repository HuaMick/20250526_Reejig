"""
Generate a prompt for the LLM to do skill gap analysis between two occupations.
"""
from typing import Dict, List, Any, Optional

def generate_skill_gap_analysis_prompt(from_occupation_data: Dict[str, Any], to_occupation_data: Dict[str, Any]) -> Dict[str, Any]:
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