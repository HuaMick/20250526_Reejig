"""
Send a prompt to the Gemini API and returns the response.
"""
import os
import json
import requests
import uuid # Added for request_id
import re  # Added for better JSON cleaning
from datetime import datetime, UTC # Added UTC for timezone-aware datetime
from typing import Dict, Any, List # Added List for prompt_skills_data

def gemini_llm_request(
    prompt: str,
    request_onet_soc_code: str, # Added
    prompt_skills_data: List[Dict[str, str]], # Added, e.g., [{"skill_element_id": "x", "skill_name": "y"}, ...]
    model: str = "gemini-2.0-flash",
    temperature: float = 0.7, 
    max_tokens: int = 6024,
    expected_response_type: str = "skill_proficiency"  # Added to handle different response formats
) -> Dict[str, Any]:
    """
    Send a prompt to the Google Gemini API and return the response, structured for DB logging.
    
    Args:
        prompt (str): The text prompt to send to the model.
        request_onet_soc_code (str): The O*NET SOC code for the occupation this prompt pertains to.
        prompt_skills_data (List[Dict[str, str]]): A list of skill dicts included in the prompt,
                                                   each with "skill_element_id" and "skill_name".
        model (str, optional): The Gemini model to use. Defaults to "gemini-2.0-flash".
        temperature (float, optional): Controls randomness of output. Defaults to 0.7.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1024.
        expected_response_type (str): Type of expected response structure. Options:
                                     - "skill_proficiency": Expects skill_proficiency_assessment format
                                     - "skill_gap_analysis": Expects skill_gap_analysis format
        
    Returns:
        dict: Standard response format with keys:
            - success (bool): Whether the API call was successful
            - message (str): Status message or error description
            - result (dict): When successful, contains:
                - request_data (List[Dict]): Data for LLM_Skill_Proficiency_Requests table.
                - reply_data (List[Dict]): Data for LLM_Skill_Proficiency_Replies table.
                - raw_response (dict): The full parsed LLM JSON response for custom processing
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
                
                # Save the raw response to a file for debugging
                debug_dir = "src/functions/llm_debug_responses"
                if not os.path.exists(debug_dir):
                    # According to rules, I cannot create this directory.
                    # It will be handled by informing the user.
                    pass # Directory creation will be handled by user.
                
                # Ensure the directory exists before trying to write to it.
                # This part assumes the user has created the directory.
                # If not, writing the file will fail, but the function will continue.
                # The primary goal is to attempt saving for debugging if the path is valid.
                if os.path.exists(debug_dir):
                    try:
                        response_filename = os.path.join(debug_dir, f"llm_response_{batch_request_id}_{expected_response_type}.txt")
                        with open(response_filename, "w") as f:
                            f.write(f"--- PROMPT SENT TO LLM ({expected_response_type} for {request_onet_soc_code}) ---\\n")
                            f.write(prompt + "\\n\\n")
                            f.write("--- RAW LLM RESPONSE ---\\n")
                            f.write(generated_text)
                        # print(f"LLM response saved to {response_filename}") # Optional: for live logging if needed
                    except Exception as e_save:
                        # Log or print that saving the debug file failed, but don't stop the main flow.
                        print(f"Warning: Could not save LLM debug response to file: {e_save}")

                # Enhanced JSON parsing with multiple cleaning strategies
                llm_output_json = _parse_llm_json_response(generated_text)
                
                if llm_output_json is None:
                    return {
                        "success": False,
                        "message": "LLM response text could not be parsed as valid JSON after all cleaning attempts",
                        "result": {"request_data": request_data_list, "reply_data": [], "raw_llm_response": generated_text}
                    }

                # Process response based on expected type
                if expected_response_type == "skill_proficiency":
                    reply_data_list = _process_skill_proficiency_response(
                        llm_output_json, batch_request_id, request_onet_soc_code, current_timestamp
                    )
                elif expected_response_type == "skill_gap_analysis":
                    reply_data_list = _process_skill_gap_analysis_response(
                        llm_output_json, batch_request_id, request_onet_soc_code, current_timestamp
                    )
                else:
                    return {
                        "success": False,
                        "message": f"Unknown expected_response_type: {expected_response_type}",
                        "result": {"request_data": request_data_list, "reply_data": [], "raw_response": llm_output_json}
                    }
                
                if reply_data_list is None:
                    return {
                        "success": False,
                        "message": f"Parsed LLM output does not match expected {expected_response_type} structure.",
                        "result": {"request_data": request_data_list, "reply_data": [], "raw_response": llm_output_json}
                    }
                
                return {
                    "success": True,
                    "message": "Successfully generated and parsed response from Gemini API",
                    "result": {
                        "request_data": request_data_list,
                        "reply_data": reply_data_list,
                        "raw_response": llm_output_json
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


def _parse_llm_json_response(generated_text: str) -> Dict[str, Any] | None:
    """
    Enhanced JSON parsing with multiple cleaning strategies.
    
    Args:
        generated_text (str): Raw text response from LLM
        
    Returns:
        Dict[str, Any] | None: Parsed JSON object or None if parsing fails
    """
    # Strategy 1: Direct parsing
    try:
        return json.loads(generated_text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Remove markdown fences
    cleaned_text = generated_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[len("```json"):].strip()
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[len("```"):].strip()
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-len("```")].strip()
    
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Find JSON block using regex
    json_pattern = r'\{.*\}'
    json_match = re.search(json_pattern, cleaned_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Strategy 4: More robustly fix common JSON issues, especially unescaped quotes within strings
    # This regex tries to find unescaped double quotes within a string value
    # It looks for a quote that is not preceded by a backslash,
    # and is followed by some characters and then another quote (marking the end of the intended string value)
    # before a comma or closing brace/bracket.
    def escape_quotes_in_strings(text):
        # This is a complex task for regex and might need iterative refinement.
        # This pattern attempts to identify strings and escape quotes within them.
        # It looks for ":\\s*\"" (a key followed by a string), then captures the string content,
        # and replaces unescaped quotes within that captured content.
        
        def replace_unenscaped_quotes(match):
            # The string content is in group 1
            string_content = match.group(1)
            # Replace unescaped quotes within this specific string_content
            escaped_string_content = re.sub(r'(?<!\\\\)"', r'\\\\"', string_content)
            return f': \\"{escaped_string_content}\\"'

        # This pattern is an attempt, might need more robustness
        # It looks for key: "value" patterns.
        # (?<!"key":\\s") - Negative lookbehind to avoid matching already escaped content or structure.
        # (?<!\\\\)" - Matches a " not preceded by a \\
        
        # A simpler approach: try to fix unescaped quotes only if they are part of what looks like a value.
        # This is still tricky. For now, let's try a targeted replacement for a common LLM error:
        # LLM might do: "explanation": "This is "bad" because..."
        # We want: "explanation": "This is \\"bad\\" because..."

        # Let's try to replace " before a word character, if not preceded by a backslash or start of string, or colon
        # This is very heuristic.
        text = re.sub(r'(?<![\\s{\[:,])"(?=\\w)', r'\\\\"', text)
        return text

    try:
        fixed_text = escape_quotes_in_strings(cleaned_text)
        # Fix trailing commas
        fixed_text = re.sub(r',(\\s*[}\\]])', r'\\1', fixed_text)
        return json.loads(fixed_text)
    except json.JSONDecodeError:
        # Try one more pass with the original cleaned_text after attempting to fix trailing commas only
        try:
            fixed_text_trailing_only = re.sub(r',(\\s*[}\\]])', r'\\1', cleaned_text)
            return json.loads(fixed_text_trailing_only)
        except json.JSONDecodeError:
            pass

    return None


def _process_skill_proficiency_response(
    llm_output_json: Dict[str, Any], 
    batch_request_id: str, 
    request_onet_soc_code: str, 
    current_timestamp
) -> List[Dict[str, Any]] | None:
    """Process skill proficiency assessment response format."""
    if not isinstance(llm_output_json, dict) or \
       "skill_proficiency_assessment" not in llm_output_json or \
       not isinstance(llm_output_json["skill_proficiency_assessment"], dict) or \
       "assessed_skills" not in llm_output_json["skill_proficiency_assessment"] or \
       not isinstance(llm_output_json["skill_proficiency_assessment"]["assessed_skills"], list):
        return None

    assessment_details = llm_output_json["skill_proficiency_assessment"]
    assessed_skills_from_llm = assessment_details["assessed_skills"]
    
    reply_data_list = []
    for assessed_skill in assessed_skills_from_llm:
        reply_data_list.append({
            "request_id": batch_request_id,
            "llm_onet_soc_code": assessment_details.get("llm_onet_soc_code", request_onet_soc_code),
            "llm_occupation_name": assessment_details.get("llm_occupation_name"),
            "llm_skill_name": assessed_skill.get("llm_skill_name"),
            "llm_assigned_proficiency_description": assessed_skill.get("llm_assigned_proficiency_description"),
            "llm_assigned_proficiency_level": assessed_skill.get("llm_assigned_proficiency_level"),
            "llm_explanation": assessed_skill.get("llm_explanation"),
            "assessment_timestamp": current_timestamp
        })
    
    return reply_data_list


def _process_skill_gap_analysis_response(
    llm_output_json: Dict[str, Any], 
    batch_request_id: str, 
    request_onet_soc_code: str, 
    current_timestamp
) -> List[Dict[str, Any]] | None:
    """Process skill gap analysis response format."""
    if not isinstance(llm_output_json, dict) or \
       "skill_gap_analysis" not in llm_output_json or \
       not isinstance(llm_output_json["skill_gap_analysis"], dict) or \
       "skill_gaps" not in llm_output_json["skill_gap_analysis"] or \
       not isinstance(llm_output_json["skill_gap_analysis"]["skill_gaps"], list):
        return None

    gap_analysis_details = llm_output_json["skill_gap_analysis"]
    skill_gaps_from_llm = gap_analysis_details["skill_gaps"]
    
    reply_data_list = []
    for skill_gap in skill_gaps_from_llm:
        reply_data_list.append({
            "request_id": batch_request_id,
            "llm_onet_soc_code": request_onet_soc_code,
            "llm_occupation_name": gap_analysis_details.get("to_occupation"),
            "llm_skill_name": skill_gap.get("skill_name"),
            "llm_assigned_proficiency_description": f"Gap from {skill_gap.get('from_proficiency_level', 0)} to {skill_gap.get('to_proficiency_level', 0)}",
            "llm_assigned_proficiency_level": skill_gap.get("to_proficiency_level"),
            "llm_explanation": skill_gap.get("gap_description"),
            "assessment_timestamp": current_timestamp,
            "gap_from_proficiency": skill_gap.get("from_proficiency_level"),
            "gap_to_proficiency": skill_gap.get("to_proficiency_level")
        })
    
    return reply_data_list


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