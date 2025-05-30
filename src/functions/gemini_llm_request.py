"""
Send a prompt to the Gemini API and returns the response.
"""
import os
import json
import requests
import uuid # Added for request_id
from datetime import datetime, UTC # Added UTC for timezone-aware datetime
from typing import Dict, Any, List # Added List for prompt_skills_data

def gemini_llm_request(
    prompt: str,
    request_onet_soc_code: str, # Added
    prompt_skills_data: List[Dict[str, str]], # Added, e.g., [{"skill_element_id": "x", "skill_name": "y"}, ...]
    model: str = "gemini-2.0-flash",
    temperature: float = 0.7, 
    max_tokens: int = 1024
) -> Dict[str, Any]:
    """
    Send a prompt to the Google Gemini API and return the response, structured for DB logging.
    
    Args:
        prompt (str): The text prompt to send to the model.
        request_onet_soc_code (str): The O*NET SOC code for the occupation this prompt pertains to.
        prompt_skills_data (List[Dict[str, str]]): A list of skill dicts included in the prompt,
                                                   each with "skill_element_id" and "skill_name".
        model (str, optional): The Gemini model to use. Defaults to "gemini-pro".
        temperature (float, optional): Controls randomness of output. Defaults to 0.7.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1024.
        
    Returns:
        dict: Standard response format with keys:
            - success (bool): Whether the API call was successful
            - message (str): Status message or error description
            - result (dict): When successful, contains:
                - request_data (List[Dict]): Data for LLM_Skill_Proficiency_Requests table.
                - reply_data (List[Dict]): Data for LLM_Skill_Proficiency_Replies table.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "message": "GEMINI_API_KEY not found in environment variables",
            "result": None
        }
    
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    url = f"{base_url}/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }
    
    current_timestamp = datetime.now(UTC)
    # Ensure prompt_skills_data is a list of dicts as expected for safety
    if not isinstance(prompt_skills_data, list) or not all(isinstance(item, dict) for item in prompt_skills_data):
        return {
            "success": False,
            "message": "Invalid prompt_skills_data format. Expected a list of dictionaries.",
            "result": None
        }

    # Generate a single request_id for all skills in this request batch
    batch_request_id = str(uuid.uuid4()) 

    # Prepare request_data: one entry per skill in the prompt
    request_data_list = []
    for skill_info in prompt_skills_data:
        request_data_list.append({
            "request_id": batch_request_id,
            "request_model": model,
            "request_onet_soc_code": request_onet_soc_code,
            "request_skill_element_id": skill_info.get("skill_element_id"),
            "request_skill_name": skill_info.get("skill_name"),
            "request_timestamp": current_timestamp
        })

    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            try:
                generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Attempt to parse the LLM's response text as JSON
                try:
                    llm_output_json = json.loads(generated_text)
                except json.JSONDecodeError:
                    # If direct parsing fails, try cleaning markdown fences
                    cleaned_text = generated_text.strip()
                    if cleaned_text.startswith("```json"):
                        cleaned_text = cleaned_text[len("```json"):].strip()
                    if cleaned_text.startswith("```"):
                        cleaned_text = cleaned_text[len("```"):].strip()
                    if cleaned_text.endswith("```"):
                        cleaned_text = cleaned_text[:-len("```")].strip()
                    try:
                        llm_output_json = json.loads(cleaned_text)
                    except json.JSONDecodeError as e_clean:
                        return {
                            "success": False,
                            "message": f"LLM response text was not valid JSON even after cleaning: {str(e_clean)}",
                            "result": {"request_data": request_data_list, "reply_data": [], "raw_llm_response": generated_text}
                        }

                # Validate the structure of the parsed LLM output
                if not isinstance(llm_output_json, dict) or \
                   "skill_proficiency_assessment" not in llm_output_json or \
                   not isinstance(llm_output_json["skill_proficiency_assessment"], dict) or \
                   "assessed_skills" not in llm_output_json["skill_proficiency_assessment"] or \
                   not isinstance(llm_output_json["skill_proficiency_assessment"]["assessed_skills"], list):
                    return {
                        "success": False,
                        "message": "Parsed LLM output does not match expected structure (missing skill_proficiency_assessment or assessed_skills).",
                        "result": {"request_data": request_data_list, "reply_data": [], "raw_llm_response": llm_output_json}
                    }

                assessment_details = llm_output_json["skill_proficiency_assessment"]
                assessed_skills_from_llm = assessment_details["assessed_skills"]
                
                reply_data_list = []
                for assessed_skill in assessed_skills_from_llm:
                    reply_data_list.append({
                        "request_id": batch_request_id, # Link back to the request batch
                        "llm_onet_soc_code": assessment_details.get("llm_onet_soc_code", request_onet_soc_code), # Fallback if LLM omits
                        "llm_occupation_name": assessment_details.get("llm_occupation_name"),
                        "llm_skill_name": assessed_skill.get("llm_skill_name"),
                        "llm_assigned_proficiency_description": assessed_skill.get("llm_assigned_proficiency_description"),
                        "llm_assigned_proficiency_level": assessed_skill.get("llm_assigned_proficiency_level"),
                        "llm_explanation": assessed_skill.get("llm_explanation"),
                        "assessment_timestamp": current_timestamp
                    })
                
                return {
                    "success": True,
                    "message": "Successfully generated and parsed response from Gemini API",
                    "result": {
                        "request_data": request_data_list,
                        "reply_data": reply_data_list
                    }
                }
            except (KeyError, IndexError, TypeError) as e_parse: # Added TypeError for safety with .get()
                return {
                    "success": False,
                    "message": f"Failed to parse Gemini API response structure: {str(e_parse)}",
                    "result": {"request_data": request_data_list, "reply_data": [], "raw_api_response": response_data}
                }
        else:
            error_message = response_data.get("error", {}).get("message", "Unknown error")
            return {
                "success": False,
                "message": f"Gemini API returned error: {error_message}",
                "result": {"request_data": request_data_list, "reply_data": [], "raw_api_response_data": response_data}
            }
    
    except Exception as e_req:
        return {
            "success": False,
            "message": f"Exception occurred while calling Gemini API: {str(e_req)}",
            "result": {"request_data": request_data_list, "reply_data": []}
        }

if __name__ == "__main__":
    print("Minimalistic happy path example for gemini_llm_request:")
    print("This example assumes GEMINI_API_KEY environment variable is correctly set.")
    
    test_prompt = """{
  "skill_proficiency_assessment": {
    "llm_onet_soc_code": "11-1011.00",
    "llm_occupation_name": "Chief Executives",
    "assessed_skills": [
      {
        "llm_skill_name": "Reading Comprehension",
        "llm_assigned_proficiency_description": "Expert",
        "llm_assigned_proficiency_level": 7,
        "llm_explanation": "Detailed explanation for Reading Comprehension..."
      },
      {
        "llm_skill_name": "Active Listening",
        "llm_assigned_proficiency_description": "Expert",
        "llm_assigned_proficiency_level": 7,
        "llm_explanation": "Detailed explanation for Active Listening..."
      }
    ]
  }
}""" # Example of what the LLM *should* return as text
    
    example_onet_soc_code = "11-1011.00"
    example_skills_in_prompt = [
        {"skill_element_id": "1.A.1.a.1", "skill_name": "Reading Comprehension"},
        {"skill_element_id": "1.A.1.a.2", "skill_name": "Active Listening"}
    ]

    print(f"\n--- Simulating LLM call for occupation: {example_onet_soc_code} ---")
    # In a real scenario, the 'prompt' arg would be from gemini_llm_prompt
    # For this __main__, we use a hardcoded example of the *expected LLM text output* 
    # and then mock the requests.post call to return it, to test the parsing logic.

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = json.dumps(json_data) # requests.Response has a .text attribute

        def json(self):
            return self.json_data

    # This function will be used to mock requests.post
    def mock_requests_post(url, json):
        # Simulate the Gemini API's actual response structure
        # where the 'text' is the string we defined in test_prompt
        gemini_response_structure = {
            "candidates": [
                {
                    "content": {"parts": [{"text": test_prompt}]},
                    # Add other fields if your parsing logic depends on them
                }
            ]
        }
        return MockResponse(gemini_response_structure, 200)

    original_requests_post = requests.post
    requests.post = mock_requests_post

    actual_prompt_for_llm = "This is the actual prompt generated by gemini_llm_prompt for Chief Executives and its skills..."
    result = gemini_llm_request(
        prompt=actual_prompt_for_llm, 
        request_onet_soc_code=example_onet_soc_code,
        prompt_skills_data=example_skills_in_prompt,
        model="gemini-pro" # Using the default for the example
    )
    
    requests.post = original_requests_post # Restore original function

    print("\nFunction Call Result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    if result['success'] and result['result']:
        print("  Request Data (first item):")
        if result['result']['request_data']:
            print(json.dumps(result['result']['request_data'][0], indent=2, default=str))
        print("  Reply Data (first item):")
        if result['result']['reply_data']:
            print(json.dumps(result['result']['reply_data'][0], indent=2, default=str))
    elif result.get("result") and result["result"].get("raw_llm_response"):
        print(f"  Raw LLM Response: {result['result']['raw_llm_response']}")
    elif result.get("result") and result["result"].get("raw_api_response_data"):
        print(f"  Raw API Error Response: {result['result']['raw_api_response_data']}")


    print("\nExample finished.")