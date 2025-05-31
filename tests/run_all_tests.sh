#!/bin/bash
# Script to run all integration tests

# Check if the environment file exists
if [ ! -f "env/env.env" ]; then
    echo "Warning: Environment file env/env.env not found."
    echo "Tests may fail if they require environment variables."
fi

# Run the batch test runner with all tests
python3 tests/batch_test_runner.py --output test_results.json

# Check if any tests failed
if [ $? -ne 0 ]; then
    echo "Some tests FAILED. See above for details."
    exit 1
else
    echo "All tests PASSED!"
fi 