import pytest

@pytest.fixture
def test_input():
    """Fixture providing test input data."""
    return "test_input"

@pytest.fixture
def expected_success_response():
    """Fixture providing expected success response."""
    return {
        "success": True,
        "message": "Hello, how are you?"
    }

@pytest.fixture
def expected_error_response():
    """Fixture providing expected error response."""
    return {
        "success": False,
        "message": "An error occurred"
    }
