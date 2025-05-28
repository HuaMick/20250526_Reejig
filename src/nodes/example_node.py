import os
import sys
from src.functions.example_function import example_function

def main():
    """
    Example node that demonstrates chaining multiple functions together.
    This node processes a series of input values through the example_function.
    """
    print("Starting example node process...")

    # Example input data
    input_values = ["hello", "world", "test"]
    
    # Process each input value
    results = []
    for input_value in input_values:
        print(f"\nProcessing: '{input_value}'")
        
        try:
            # Call the example function with happy path
            result = example_function(input_value, happy_path=True)
            
            if not result['success']:
                print(f"Error processing '{input_value}': {result['message']}")
                sys.exit(1)
            
            print(f"Success: {result['message']}")
            print(f"Result: {result['result']}")
            results.append(result['result'])
            
        except Exception as e:
            print(f"Unexpected error processing '{input_value}': {e}")
            sys.exit(1)
    
    # Demonstrate error handling
    print(f"\n--- Testing Error Path ---")
    try:
        error_result = example_function("error_test", happy_path=False)
        print(f"Error result: {error_result['message']}")
    except Exception as e:
        print(f"Unexpected error in error path: {e}")
        sys.exit(1)
    
    # Final summary
    print(f"\nExample node process completed successfully.")
    print(f"Processed {len(results)} values: {results}")

if __name__ == '__main__':
    main()
