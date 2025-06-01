"""
Integration test for gemini_llm_prompt function.
"""
import json
from src.functions.generate_skill_proficiency_prompt import generate_skill_proficiency_prompt

def test_generate_skill_proficiency_prompt():
    """
    Test generate_skill_proficiency_prompt with target occupation.
    """
    # Test data
    occupation_data = {
        "onet_id": "15-1252.00",
        "name": "Software Developer",
        "skills": [
            {"skill_name": "Programming", "proficiency_level": 5.0},
            {"skill_name": "Problem Solving", "proficiency_level": 4.5}
        ]
    }
    
    # Call the function
    result = generate_skill_proficiency_prompt(occupation_data=occupation_data)
    
    # Assertions
    assert result["success"] is True
    assert "Successfully generated prompt" in result["message"]
    assert "prompt" in result["result"]
    
    # Check prompt content
    prompt = result["result"]["prompt"]
    assert "Occupation Information" in prompt
    assert "15-1252.00" in prompt
    assert "Software Developer" in prompt
    assert "Programming" in prompt
    assert "Problem Solving" in prompt
    assert "Source Occupation Information" not in prompt
    assert "Your entire response must be a single, valid JSON object" in prompt
    assert "skill_proficiency_assessment" in prompt
