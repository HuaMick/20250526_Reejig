import pytest

@pytest.fixture
def test_prompt():
    """Fixture providing a test prompt for Gemini API."""
    return "Explain what generative AI is in one sentence."

@pytest.fixture
def expected_success_structure():
    """Fixture providing expected structure of a successful response (without checking actual content)."""
    return {
        "success": True,
        "message": "Successfully generated response from Gemini API",
        "result": {
            "text": "",  # Will be a non-empty string
            "model": "gemini-pro",
            "usage": {}
        }
    }

@pytest.fixture
def expected_error_no_api_key():
    """Fixture providing expected response when API key is missing."""
    return {
        "success": False,
        "message": "GEMINI_API_KEY not found in environment variables"
    } 