# Testing Framework

This directory contains tests for the O*NET data pipeline project, primarily using pytest.

## Test Structure

- `test_integration_*.py`: Integration tests that verify end-to-end functionality
- `test_unit_*.py`: Unit tests for individual functions
- `analyze_tests.py`: Script to analyze test coverage and results

## Running Tests with pytest

### Basic Commands

```bash
# Run all tests
. env/env.env && pytest

# Run all tests with detailed output
. env/env.env && pytest -v

# Run a specific test file
. env/env.env && pytest tests/test_integration_mysql_connection.py

# Run a specific test function
. env/env.env && pytest tests/test_integration_mysql_connection.py::test_actual_mysql_connection
```

### Running Tests by Pattern

```bash
# Run all database-related tests
. env/env.env && pytest -k "mysql"

# Run all API-related tests
. env/env.env && pytest -k "api"

# Run all skill gap tests
. env/env.env && pytest -k "skill_gap"
```

### Running Tests by Directory

```bash
# Run all integration tests
. env/env.env && pytest tests/test_integration_*.py
```

### Test Output Options

```bash
# Show print statements during tests
. env/env.env && pytest -v -s

# Generate XML report
. env/env.env && pytest --junitxml=test-report.xml

# Stop on first failure
. env/env.env && pytest -x
```

## Creating New Tests

To create a new test:

1. Create a new file following the naming convention:
   - `test_integration_*.py` for integration tests
   - `test_unit_*.py` for unit tests

2. Implement test functions with names starting with `test_`

3. Follow these best practices:
   - Make tests independent and idempotent
   - Use descriptive test names
   - Include setup and teardown to clean up after tests
   - Test both success and error cases
   - Use pytest fixtures for common setup

## Example Test Structure

```python
import pytest

# Optional fixture for setting up test resources
@pytest.fixture
def setup_test_data():
    # Setup code
    data = {"key": "value"}
    yield data
    # Teardown code (runs after test completes)

def test_my_function(setup_test_data):
    # Arrange
    input_data = setup_test_data
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result["success"] == True
```

## Analyzing Test Coverage

To analyze which functions are tested and which are not:

```bash
python3 tests/analyze_tests.py --coverage
```

## Environment Variables

Tests use the environment variables defined in `env/env.env`. This includes:

- Database connection parameters
- O*NET API credentials
- Other service credentials

Make sure these are properly set up before running tests. 