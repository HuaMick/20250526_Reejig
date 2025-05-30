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
    result = gemini_llm_request(test_prompt)
    
    # Print results for verification
    print("\nIntegration Test Results:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Model used: {result['result']['model']}")
        print(f"Response text: {result['result']['text']}")
    
    # Assertions to verify the results
    assert result["success"] == True, f"API call failed: {result.get('message')}"
    assert "message" in result, "Response should contain a message field"
    
    # Verify response structure
    assert "result" in result, "Response should contain a result dictionary"
    assert "text" in result["result"], "Result should contain the generated text"
    assert "model" in result["result"], "Result should contain the model name"
    assert "usage" in result["result"], "Result should contain usage information"
    
    # Verify response content
    assert len(result["result"]["text"]) > 0, "Generated text should not be empty"
    print("\nIntegration test completed successfully!")

def test_gemini_llm_request_with_params(test_prompt):
    """
    Integration test for gemini_llm_request function with custom parameters.
    Tests the temperature and max_tokens parameters.
    """
    # Make sure we have the API key set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\nSkipping test: GEMINI_API_KEY not found in environment variables")
        return
    
    print("\nIntegration Test - Gemini LLM Request with Custom Parameters:")
    print(f"Using prompt: \"{test_prompt}\" with temperature=0.1 and max_tokens=50")
    
    # Execute the function with custom parameters
    result = gemini_llm_request(
        prompt=test_prompt,
        temperature=0.1,
        max_tokens=50
    )
    
    # Print results for verification
    print("\nIntegration Test Results:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Model used: {result['result']['model']}")
        print(f"Response text: {result['result']['text']}")
    
    # Assertions to verify the results
    assert result["success"] == True, f"API call failed: {result.get('message')}"
    
    # Verify response structure and content
    assert "result" in result, "Response should contain a result dictionary"
    assert len(result["result"]["text"]) > 0, "Generated text should not be empty"
    
    print("\nIntegration test with custom parameters completed successfully!") 