import pytest
import pandas as pd
from typing import Dict, Any

@pytest.fixture
def mock_onet_api_credentials():
    """Fixture providing mock API credentials for testing."""
    return {
        "api_username": "test_username",
        "api_key": "test_api_key",
        "client_name": "test_client",
        "base_url": "https://services.onetcenter.org/v1.9/ws"
    }

@pytest.fixture
def mock_onet_occupations_response():
    """Fixture providing a mock response from the O*NET occupations API endpoint."""
    return {
        "sort": "code",
        "start": 1,
        "end": 3,
        "total": 1016,
        "link": [
            {
                "href": "https://services.onetcenter.org/v1.9/ws/online/occupations/?sort=code&start=4&end=6&clientname=test_client",
                "rel": "next"
            }
        ],
        "occupation": [
            {
                "href": "/v1.9/ws/online/occupations/11-1011.00/",
                "code": "11-1011.00",
                "title": "Chief Executives",
                "tags": {
                    "bright_outlook": True,
                    "green": False
                }
            },
            {
                "href": "/v1.9/ws/online/occupations/11-1021.00/",
                "code": "11-1021.00",
                "title": "General and Operations Managers",
                "tags": {
                    "bright_outlook": False,
                    "green": False
                }
            },
            {
                "href": "/v1.9/ws/online/occupations/11-2011.00/",
                "code": "11-2011.00",
                "title": "Advertising and Promotions Managers",
                "tags": {
                    "bright_outlook": False,
                    "green": False
                }
            }
        ]
    }

@pytest.fixture
def expected_occupations_df():
    """Fixture providing the expected DataFrame result from parsing the mock API response."""
    data = [
        {"onet_soc_code": "11-1011.00", "title": "Chief Executives"},
        {"onet_soc_code": "11-1021.00", "title": "General and Operations Managers"},
        {"onet_soc_code": "11-2011.00", "title": "Advertising and Promotions Managers"}
    ]
    return pd.DataFrame(data)

@pytest.fixture
def expected_success_response(expected_occupations_df):
    """Fixture providing the expected success response structure."""
    return {
        "success": True,
        "message": "Successfully fetched 3 O*NET-SOC occupation codes and titles.",
        "result": {
            "occupation_codes_df": expected_occupations_df
        }
    }

@pytest.fixture
def expected_error_response():
    """Fixture providing the expected error response structure."""
    return {
        "success": False,
        "message": "API request failed: HTTPError (Status code: 401) - Invalid API credentials",
        "result": {
            "occupation_codes_df": None
        }
    } 