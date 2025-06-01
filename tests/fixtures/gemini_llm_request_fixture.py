import pytest

@pytest.fixture
def test_prompt():
    """Fixture providing a test prompt for Gemini API."""
    return """
I need you to analyze skills for a job and determine proficiency levels based on the information provided.

# Occupation Information
- O*NET ID: 11-2021.00
- Occupation Name: Marketing Managers
- Skills Required:
  - Reading Comprehension
  - Active Listening
  - Writing
  - Speaking
  - Mathematics

# Your Task:
1. Analyze the skills of the Occupation provided.
2. For each skill listed in the Occupation, determine a proficiency level.
   - Use a scale of 1-7 where 1 is Novice and 7 is Expert
   - Consider what level of proficiency would be typical/expected for someone in this occupation
3. Provide a detailed justification/explanation for each assigned proficiency level.
   - Your explanation should be in the context of the Occupation's typical duties and responsibilities.


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
"""

@pytest.fixture
def expected_success_structure():
    """Fixture providing expected structure of a successful response (without checking actual content)."""
    return {
        "success": True,
        "message": "Successfully generated response from Gemini API",
        "result": {
            "text": "",  # Will be a non-empty string
            "model": "gemini-pro",
            "usage": {}
        }
    }

@pytest.fixture
def expected_error_no_api_key():
    """Fixture providing expected response when API key is missing."""
    return {
        "success": False,
        "message": "GEMINI_API_KEY not found in environment variables"
    } 