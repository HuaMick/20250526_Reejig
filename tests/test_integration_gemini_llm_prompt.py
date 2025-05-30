"""
Integration test for gemini_llm_prompt function.
"""
import json
from src.functions.gemini_llm_prompt import gemini_llm_prompt

def test_gemini_llm_prompt_to_only():
    """
    Test gemini_llm_prompt with only target occupation.
    """
    # Test data
    to_occupation = {
        "onet_id": "15-1252.00",
        "name": "Software Developer",
        "skills": [
            {"skill_name": "Programming", "proficiency_level": 5.0},
            {"skill_name": "Problem Solving", "proficiency_level": 4.5}
        ]
    }
    
    # Call the function
    result = gemini_llm_prompt(to_occupation=to_occupation)
    
    # Assertions
    assert result["success"] is True
    assert "Successfully generated prompt" in result["message"]
    assert "prompt" in result["result"]
    
    # Check prompt content
    prompt = result["result"]["prompt"]
    assert "Target Occupation Information" in prompt
    assert "15-1252.00" in prompt
    assert "Software Developer" in prompt
    assert "Programming" in prompt
    assert "Problem Solving" in prompt
    assert "Source Occupation Information" not in prompt
    assert "Your entire response must be a single, valid JSON object" in prompt
    assert "skill_proficiency_assessment" in prompt

def test_gemini_llm_prompt_with_from():
    """
    Test gemini_llm_prompt with both source and target occupations.
    """
    # Test data
    to_occupation = {
        "onet_id": "15-1252.00",
        "name": "Software Developer",
        "skills": [
            {"skill_name": "Programming", "proficiency_level": 5.0},
            {"skill_name": "Problem Solving", "proficiency_level": 4.5}
        ]
    }
    
    from_occupation = {
        "onet_id": "13-1161.00",
        "name": "Market Research Analyst",
        "skills": [
            {"skill_name": "Data Analysis", "proficiency_level": 4.2},
            {"skill_name": "Communication", "proficiency_level": 4.5}
        ]
    }
    
    # Call the function
    result = gemini_llm_prompt(
        to_occupation=to_occupation,
        from_occupation=from_occupation
    )
    
    # Assertions
    assert result["success"] is True
    assert "Successfully generated prompt" in result["message"]
    assert "prompt" in result["result"]
    
    # Check prompt content
    prompt = result["result"]["prompt"]
    assert "Target Occupation Information" in prompt
    assert "15-1252.00" in prompt
    assert "Software Developer" in prompt
    assert "Programming" in prompt
    assert "Problem Solving" in prompt
    assert "Source Occupation Information" in prompt
    assert "13-1161.00" in prompt
    assert "Market Research Analyst" in prompt
    assert "Data Analysis" in prompt
    assert "Communication" in prompt
    assert "skill transferability" in prompt
    assert "Your entire response must be a single, valid JSON object" in prompt
    assert "skill_proficiency_assessment" in prompt

def test_gemini_llm_prompt_invalid_to():
    """
    Test gemini_llm_prompt with invalid to_occupation.
    """
    # Test with missing required fields
    invalid_to = {"name": "Test Job"}
    result = gemini_llm_prompt(to_occupation=invalid_to)
    
    # Assertions
    assert result["success"] is False
    assert "Invalid to_occupation format" in result["message"]

def test_gemini_llm_prompt_invalid_from():
    """
    Test gemini_llm_prompt with invalid from_occupation.
    """
    # Valid to_occupation
    to_occupation = {
        "onet_id": "15-1252.00",
        "name": "Software Developer",
        "skills": [
            {"skill_name": "Programming", "proficiency_level": 5.0}
        ]
    }
    
    # Invalid from_occupation
    invalid_from = {"name": "Previous Job"}
    
    # Call the function
    result = gemini_llm_prompt(
        to_occupation=to_occupation,
        from_occupation=invalid_from
    )
    
    # Assertions
    assert result["success"] is False
    assert "Invalid from_occupation format" in result["message"] 