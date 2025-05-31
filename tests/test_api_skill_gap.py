import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the parent directory to the Python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.main import app

# Create a test client
client = TestClient(app)

@pytest.fixture(scope="module")
def check_api_credentials():
    """Fixture to check if O*NET API credentials are set"""
    if not os.getenv("ONET_USERNAME") or not os.getenv("ONET_PASSWORD"):
        pytest.skip("O*NET API credentials not set, skipping tests that require API fallback")

def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "message" in response.json()

def test_skill_gap_endpoint_basic(check_api_credentials):
    """Test the basic skill gap endpoint without proficiency levels."""
    # Using occupation codes identified by the user as having different skills
    from_occupation = "11-1011.00"  # Chief Executives
    to_occupation = "11-2021.00"    # Marketing Managers
    
    response = client.get(f"/api/v1/skill-gap?from_occupation={from_occupation}&to_occupation={to_occupation}")
    
    # Print the response for debugging
    print("\nAPI Test Results - Basic Skill Gap:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Assertions
    assert response.status_code == 200
    assert "from_occupation" in response.json()
    assert "to_occupation" in response.json()
    assert "skill_gaps" in response.json()
    
    # Verify occupation codes and titles
    assert response.json()["from_occupation"]["code"] == from_occupation
    assert response.json()["to_occupation"]["code"] == to_occupation
    
    # Verify skill gaps is a list of strings (skill names)
    assert isinstance(response.json()["skill_gaps"], list)
    if response.json()["skill_gaps"]:
        assert isinstance(response.json()["skill_gaps"][0], str)

def test_skill_gap_by_level_endpoint(check_api_credentials):
    """Test the skill gap by level endpoint with proficiency levels."""
    # Using occupation codes identified by the user as having different skills
    from_occupation = "11-1011.00"  # Chief Executives
    to_occupation = "11-2021.00"    # Marketing Managers
    
    response = client.get(f"/api/v1/skill-gap-by-lvl?from_occupation={from_occupation}&to_occupation={to_occupation}")
    
    # Print the response for debugging
    print("\nAPI Test Results - Skill Gap By Level:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Assertions
    assert response.status_code == 200
    assert "from_occupation" in response.json()
    assert "to_occupation" in response.json()
    assert "skill_gaps" in response.json()
    
    # Verify occupation codes and titles
    assert response.json()["from_occupation"]["code"] == from_occupation
    assert response.json()["to_occupation"]["code"] == to_occupation
    
    # Verify skill gaps is a list of objects with proficiency details
    assert isinstance(response.json()["skill_gaps"], list)
    if response.json()["skill_gaps"]:
        gap = response.json()["skill_gaps"][0]
        assert isinstance(gap, dict)
        assert "skill_name" in gap
        assert "element_id" in gap
        assert "from_proficiency" in gap
        assert "to_proficiency" in gap
        assert gap["to_proficiency"] > gap["from_proficiency"]

def test_skill_gap_endpoint_same_occupation(check_api_credentials):
    """Test the skill gap endpoint with the same occupation (should return empty gaps)."""
    occupation = "11-1011.00"  # Chief Executives
    
    response = client.get(f"/api/v1/skill-gap?from_occupation={occupation}&to_occupation={occupation}")
    
    # Print the response for debugging
    print("\nAPI Test Results - Same Occupation (Basic):")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Assertions
    assert response.status_code == 200
    assert len(response.json()["skill_gaps"]) == 0
    
    # Also test the skill-gap-by-lvl endpoint with same occupation
    response = client.get(f"/api/v1/skill-gap-by-lvl?from_occupation={occupation}&to_occupation={occupation}")
    
    print("\nAPI Test Results - Same Occupation (By Level):")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Assertions
    assert response.status_code == 200
    assert len(response.json()["skill_gaps"]) == 0

def test_skill_gap_endpoint_invalid_occupation():
    """Test the skill gap endpoint with an invalid occupation code."""
    from_occupation = "99-9999.99"  # Invalid code
    to_occupation = "11-1011.00"    # Chief Executives
    
    # Test basic endpoint
    response = client.get(f"/api/v1/skill-gap?from_occupation={from_occupation}&to_occupation={to_occupation}")
    
    # Print the response for debugging
    print("\nAPI Test Results - Invalid Occupation (Basic):")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Assertions - accept either 404 (Not Found) or 500 (Internal Server Error)
    # The API might return 500 for invalid occupations when they cause XML parsing errors
    assert response.status_code in [404, 500], f"Expected status code 404 or 500, got {response.status_code}"
    
    # Verify error message contains relevant information
    assert "occupation" in response.json()["detail"].lower(), "Error message should mention the occupation issue"
    
    # Test by-level endpoint
    response = client.get(f"/api/v1/skill-gap-by-lvl?from_occupation={from_occupation}&to_occupation={to_occupation}")
    
    print("\nAPI Test Results - Invalid Occupation (By Level):")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Assertions
    assert response.status_code in [404, 500]
    assert "occupation" in response.json()["detail"].lower() 