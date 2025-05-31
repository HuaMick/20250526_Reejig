#!/bin/bash
# Script to run a single test

# Check if a test file was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <test_file>"
    echo "Example: $0 tests/test_integration_mysql_connection.py"
    exit 1
fi

TEST_FILE=$1

# Check if the test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "Error: Test file '$TEST_FILE' not found."
    exit 1
fi

# Check if the environment file exists
if [ ! -f "env/env.env" ]; then
    echo "Warning: Environment file env/env.env not found."
    echo "Tests may fail if they require environment variables."
fi

# Run the test with environment variables
echo "Running test: $TEST_FILE"
echo "----------------------------------------------"
. env/env.env && python3 -m pytest $TEST_FILE -v

# Check if the test was successful
if [ $? -eq 0 ]; then
    echo "----------------------------------------------"
    echo "Test PASSED!"
else
    echo "----------------------------------------------"
    echo "Test FAILED!"
    exit 1
fi 