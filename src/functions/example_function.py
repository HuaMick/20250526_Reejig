import os

def example_function(input_value: str, happy_path: bool = True) -> dict[str, str]:
    """
    An example function that takes a string input and returns a modified string.
    
    Args:
        input_value (str): The input string to process
        
    Returns:
        str: The processed string with a prefix added
    """
    happy_path_result = "prefix" + input_value

    if not happy_path:
        return {
            "success": False,
            "message": "An error occurred",
        }
    else: # Happy Path
        return {
            "success": True,
            "message": "string processed with prefix added",
            "result": happy_path_result,
        }