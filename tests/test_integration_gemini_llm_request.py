import os
from src.functions.gemini_llm_request import gemini_llm_request
from tests.fixtures.gemini_llm_request_fixture import test_prompt, expected_success_structure, expected_error_no_api_key

def test_gemini_llm_request(test_prompt, expected_success_structure):
    """
    Integration test for gemini_llm_request function.
    This test makes an actual API call to the Gemini API.
    Requires GEMINI_API_KEY to be set in the environment.
    """
    # Make sure we have the API key set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\nSkipping test: GEMINI_API_KEY not found in environment variables")
        return
        
    print("\nIntegration Test - Gemini LLM Request:")
    print(f"Using prompt: \"{test_prompt}\"")
    
    # Execute the function
    result = gemini_llm_request(
        test_prompt, 
        request_onet_soc_code="11-1011.00",
        prompt_skills_data=[{"skill_element_id": "2.A.1.f", "skill_name": "Science"}],
    )
    
    # Print results for verification
    print("\nIntegration Test Results:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Model used: {result['result']['request_data'][0]['request_model']}")
        print(f"Response text: {result['result']['raw_response']}")
    
    # Assertions to verify the results
    assert result["success"] == True, f"API call failed: {result.get('message')}"
    assert "message" in result, "Response should contain a message field"
    
    # Verify response structure
    assert "result" in result, "Response should contain a result dictionary"
    assert "request_data" in result["result"], "Result should contain the request data"
    assert "reply_data" in result["result"], "Result should contain the reply data"
    assert "raw_response" in result["result"], "Result should contain the raw LLM response"
    
    # Verify response content
    assert len(result["result"]["raw_response"]) > 0, "Generated text should not be empty"
    print("\nIntegration test completed successfully!")