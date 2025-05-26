import pytest
from src.functions.example_function import example_function
from tests.fixtures.example_test_fixture import test_input, expected_success_response

def test_example_function_operation(test_input, expected_success_response):
    """
    Unit test for the example function.
    Tests the function in isolation with expected inputs.
    """
    # Execute function
    result = example_function(test_input, happy_path=True)
    
    # Assertions to verify the results
    assert result["success"] is expected_success_response["success"], "Function operation failed"
    assert result["message"] == expected_success_response["message"], f"Expected greeting message, got: {result['message']}"
