"""
Fixture for providing mock LLM assessment output.
"""
import pytest
from datetime import datetime, UTC # For timezone-aware datetimes
import uuid

@pytest.fixture(scope="session")
def mock_llm_assessment_output_fixture():
    """
    Provides a mock dictionary similar to the output of gemini_llm_request,
    containing request_data and reply_data for testing LLM data loading.
    """
    request_id_1 = str(uuid.uuid4())
    request_id_2 = str(uuid.uuid4()) # A different request batch for variety, if needed, but usually one batch per call
    
    # For this test, we'll simulate one batch_request_id as per gemini_llm_request
    shared_request_id = str(uuid.uuid4())
    timestamp = datetime.now(UTC)

    mock_output = {
        "request_data": [
            {
                "request_id": shared_request_id,
                "request_model": "gemini-test-model",
                "request_onet_soc_code": "11-1011.00",
                "request_skill_element_id": "2.A.1.a",
                "request_skill_name": "Reading Comprehension",
                "request_timestamp": timestamp
            },
            {
                "request_id": shared_request_id,
                "request_model": "gemini-test-model",
                "request_onet_soc_code": "11-1011.00",
                "request_skill_element_id": "2.A.1.b",
                "request_skill_name": "Active Listening",
                "request_timestamp": timestamp
            }
        ],
        "reply_data": [
            {
                "request_id": shared_request_id,
                "llm_onet_soc_code": "11-1011.00",
                "llm_occupation_name": "Chief Executives (Test)",
                "llm_skill_name": "Reading Comprehension",
                "llm_assigned_proficiency_description": "Expert (Test)",
                "llm_assigned_proficiency_level": 7,
                "llm_explanation": "Test explanation for Reading Comprehension.",
                "assessment_timestamp": timestamp
            },
            {
                "request_id": shared_request_id,
                "llm_onet_soc_code": "11-1011.00",
                "llm_occupation_name": "Chief Executives (Test)",
                "llm_skill_name": "Active Listening",
                "llm_assigned_proficiency_description": "Advanced (Test)",
                "llm_assigned_proficiency_level": 6,
                "llm_explanation": "Test explanation for Active Listening.",
                "assessment_timestamp": timestamp
            }
        ]
    }
    return mock_output 