# Always structure imports in test files using full paths from the project root (e.g., `from src.functions.module import function`)
import pytest
from src.functions.example_function import example_function
from tests.fixtures.example_test_fixture import test_input, expected_success_response, expected_error_response

def test_example_integration(test_input, expected_success_response, expected_error_response):
    """
    Integration test that demonstrates real-world usage of the example function.
    Tests the actual function without mocking to ensure end-to-end functionality.
    """
    # Test happy path scenario
    result = example_function(test_input, happy_path=True)
    
    # Print results for verification
    print("\nIntegration Test Results:")
    print(f"Input: {test_input}")
    print(f"Result: {result}")
    
    # Assertions to verify the results
    assert result["success"] is expected_success_response["success"], "Operation failed"
    assert result["message"] == expected_success_response["message"], f"Expected greeting message, got: {result['message']}"
    
    # Test error scenario to ensure proper error handling
    error_result = example_function(test_input, happy_path=False)
    print(f"Error scenario result: {error_result}")
    
    assert error_result["success"] is expected_error_response["success"], "Error scenario should fail"
    assert error_result["message"] == expected_error_response["message"], f"Expected error message, got: {error_result['message']}"
    
    print("Integration test completed successfully!")
