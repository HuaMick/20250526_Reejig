"""
Integration test for LLM-enhanced skill gap analysis function.

This test verifies that the get_skills_gap_by_lvl_llm function correctly:
1. Retrieves occupation data for both source and target occupations
2. Calls LLM for proficiency assessments
3. Generates LLM-enhanced skill gap analysis with descriptions
4. Returns properly formatted results
"""
import pytest
from src.functions.get_skills_gap_by_lvl_llm import get_skills_gap_by_lvl_llm
from src.config.schemas import get_sqlalchemy_engine

def test_get_skills_gap_by_lvl_llm_successful():
    """
    Test the get_skills_gap_by_lvl_llm function with valid occupation codes.
    
    This test requires:
    - Valid GEMINI_API_KEY environment variable
    - Working database connection
    - Occupation data available (either in database or via API)
    """
    # Test with occupations that should have skill gaps
    from_occupation = "11-1011.00"  # Chief Executives
    to_occupation = "11-2021.00"    # Marketing Managers
    
    # Get default engine
    engine = get_sqlalchemy_engine()
    
    print(f"\n--- Testing LLM-enhanced skill gap analysis ---")
    print(f"From: {from_occupation} (Chief Executives)")
    print(f"To: {to_occupation} (Marketing Managers)")
    
    # Call the function
    result = get_skills_gap_by_lvl_llm(from_occupation, to_occupation, engine=engine)
    
    # Print results for verification
    print(f"\nIntegration Test Results:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Number of skill gaps identified: {len(result['result'])}")
        
        if result['result']:
            print("\nFirst few skill gaps with LLM descriptions:")
            for i, gap in enumerate(result['result'][:3]):  # Show first 3 gaps
                print(f"  {i+1}. Skill: {gap['skill_name']}")
                print(f"     Element ID: {gap['element_id']}")
                print(f"     From Level: {gap['from_proficiency_level']}")
                print(f"     To Level: {gap['to_proficiency_level']}")
                print(f"     LLM Description: {gap['llm_gap_description'][:100]}...")
                print()
    else:
        print(f"Error occurred: {result['message']}")
    
    # Assertions to verify the results
    assert result["success"] == True, f"Function failed: {result['message']}"
    assert isinstance(result["result"], list), "Result should be a list"
    
    # If successful, verify structure of results
    if result["result"]:
        for gap in result["result"]:
            assert "element_id" in gap, "Each gap should have element_id"
            assert "skill_name" in gap, "Each gap should have skill_name"
            assert "from_proficiency_level" in gap, "Each gap should have from_proficiency_level"
            assert "to_proficiency_level" in gap, "Each gap should have to_proficiency_level"
            assert "llm_gap_description" in gap, "Each gap should have llm_gap_description"
            
            # Verify proficiency levels are numeric
            assert isinstance(gap["from_proficiency_level"], (int, float)), "from_proficiency_level should be numeric"
            assert isinstance(gap["to_proficiency_level"], (int, float)), "to_proficiency_level should be numeric"
            
            # Verify that target proficiency is higher than source (gap logic)
            assert gap["to_proficiency_level"] > gap["from_proficiency_level"], "Target should have higher proficiency than source for gaps"
            
            # Verify LLM description exists and is meaningful
            assert len(gap["llm_gap_description"]) > 0, "LLM gap description should not be empty"
    
    print(f"\n✅ All assertions passed! LLM-enhanced skill gap analysis working correctly.")

if __name__ == "__main__":
    print("Running integration tests for get_skills_gap_by_lvl_llm...")
    print("Note: These tests require GEMINI_API_KEY environment variable and may take time due to LLM calls.")
    
    try:
        test_get_skills_gap_by_lvl_llm_successful()
        test_get_skills_gap_by_lvl_llm_invalid_occupation()
        test_get_skills_gap_by_lvl_llm_same_occupation()
        print("\n🎉 All integration tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        raise 