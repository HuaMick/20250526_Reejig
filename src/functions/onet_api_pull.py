"""
Passes a given occupation code to the O*NET API to retrieve occupation and skills data
and returns the data as a pandas dataframe.
"""
import pandas as pd
import requests
import logging
from typing import Dict, Any, Optional, List, Tuple
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
ONET_API_BASE_URL = "https://services.onetcenter.org/ws"
DEFAULT_VERSION = "v1"

def get_onet_api_credentials() -> Tuple[str, str]:
    """
    Retrieve O*NET API credentials from environment variables.
    
    Returns:
        Tuple[str, str]: Username and password for O*NET API
    
    Raises:
        ValueError: If credentials are not found in environment variables
    """
    username = os.environ.get("ONET_API_USERNAME")
    password = os.environ.get("ONET_API_PASSWORD")
    
    if not username or not password:
        raise ValueError("O*NET API credentials not found in environment variables. "
                         "Please set ONET_API_USERNAME and ONET_API_PASSWORD.")
    
    return username, password

def onet_api_pull(occupation_code: str) -> Dict[str, Any]:
    """
    Fetch occupation and skills data from O*NET API for a given occupation code.
    
    Args:
        occupation_code (str): The O*NET-SOC code for the occupation (e.g., "15-1252.00")
    
    Returns:
        Dict with keys:
            'success' (bool): Whether the operation was successful
            'message' (str): Description of the result or error
            'result' (Dict): Contains 'occupation_data' and 'skills_data' DataFrames if successful
    """
    try:
        # Validate and format occupation code
        formatted_code = format_occupation_code(occupation_code)
        if not formatted_code:
            return {
                "success": False,
                "message": f"Invalid occupation code format: {occupation_code}. Expected format: XX-XXXX.XX",
                "result": {}
            }
        
        # Get API credentials
        try:
            username, password = get_onet_api_credentials()
        except ValueError as e:
            return {
                "success": False,
                "message": str(e),
                "result": {}
            }
        
        # Fetch occupation data
        occupation_data = fetch_occupation_data(formatted_code, username, password)
        if not occupation_data["success"]:
            return occupation_data
        
        # Fetch skills data
        skills_data = fetch_skills_data(formatted_code, username, password)
        if not skills_data["success"]:
            return skills_data
        
        # Combine results
        return {
            "success": True,
            "message": f"Successfully retrieved O*NET data for occupation {formatted_code}",
            "result": {
                "occupation_data": occupation_data["result"]["df"],
                "skills_data": skills_data["result"]["df"]
            }
        }
        
    except Exception as e:
        logging.error(f"Unexpected error in onet_api_pull: {str(e)}")
        return {
            "success": False,
            "message": f"Unexpected error in onet_api_pull: {str(e)}",
            "result": {}
        }

def format_occupation_code(code: str) -> Optional[str]:
    """
    Validate and format the occupation code to ensure it matches O*NET API requirements.
    
    Args:
        code (str): The occupation code to format
        
    Returns:
        Optional[str]: Formatted code or None if invalid
    """
    # Remove any whitespace
    code = code.strip()
    
    # Check if it already has the correct format (XX-XXXX.XX)
    if len(code) == 10 and code[2] == '-' and code[7] == '.':
        return code
    
    # If it's just numbers without formatting, try to format it
    # Example: "151252" or "1512520" or "15125200" -> "15-1252.00"
    digits_only = ''.join(c for c in code if c.isdigit())
    
    if len(digits_only) == 6:
        # Format: XXXXXX -> XX-XXXX.00
        return f"{digits_only[:2]}-{digits_only[2:6]}.00"
    elif len(digits_only) == 7:
        # Format: XXXXXXX -> XX-XXXX.X0
        return f"{digits_only[:2]}-{digits_only[2:6]}.{digits_only[6]}0"
    elif len(digits_only) == 8:
        # Format: XXXXXXXX -> XX-XXXX.XX
        return f"{digits_only[:2]}-{digits_only[2:6]}.{digits_only[6:8]}"
    
    # If we can't format it properly, return None
    return None

def fetch_occupation_data(occupation_code: str, username: str, password: str) -> Dict[str, Any]:
    """
    Fetch occupation data from O*NET API for a specific occupation code.
    
    Args:
        occupation_code (str): The O*NET-SOC code
        username (str): O*NET API username
        password (str): O*NET API password
        
    Returns:
        Dict with operation result and DataFrame if successful
    """
    try:
        url = f"{ONET_API_BASE_URL}/{DEFAULT_VERSION}/occupation/{occupation_code}"
        
        response = requests.get(
            url,
            auth=(username, password),
            headers={"Accept": "application/json"}
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"Failed to fetch occupation data. Status code: {response.status_code}, Response: {response.text}",
                "result": {}
            }
        
        data = response.json()
        
        # Extract relevant occupation information
        occupation_info = {
            "onet_soc_code": data.get("code", ""),
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Create DataFrame
        df = pd.DataFrame([occupation_info])
        
        return {
            "success": True,
            "message": f"Successfully fetched occupation data for {occupation_code}",
            "result": {"df": df}
        }
        
    except Exception as e:
        logging.error(f"Error fetching occupation data: {str(e)}")
        return {
            "success": False,
            "message": f"Error fetching occupation data: {str(e)}",
            "result": {}
        }

def fetch_skills_data(occupation_code: str, username: str, password: str) -> Dict[str, Any]:
    """
    Fetch skills data from O*NET API for a specific occupation code.
    
    Args:
        occupation_code (str): The O*NET-SOC code
        username (str): O*NET API username
        password (str): O*NET API password
        
    Returns:
        Dict with operation result and DataFrame if successful
    """
    try:
        url = f"{ONET_API_BASE_URL}/{DEFAULT_VERSION}/occupation/{occupation_code}/skills"
        
        response = requests.get(
            url,
            auth=(username, password),
            headers={"Accept": "application/json"}
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"Failed to fetch skills data. Status code: {response.status_code}, Response: {response.text}",
                "result": {}
            }
        
        data = response.json()
        skills_data = []
        
        # Extract skills information
        for skill in data.get("skills", []):
            skill_info = {
                "onet_soc_code": occupation_code,
                "element_id": skill.get("id", ""),
                "element_name": skill.get("name", ""),
                "scale_id": "LV",  # Level
                "data_value": skill.get("level", 0),
                "n": 1,  # Default sample size
                "standard_error": 0.0,  # Default standard error
                "lower_ci_bound": 0.0,  # Default lower confidence interval
                "upper_ci_bound": 0.0,  # Default upper confidence interval
                "recommend_suppress": False,  # Default recommendation
                "not_relevant": False,  # Default relevance
                "date": datetime.now().strftime("%Y-%m-%d"),
                "domain_source": "API"
            }
            skills_data.append(skill_info)
            
            # Add importance scale as well
            skill_info_imp = skill_info.copy()
            skill_info_imp["scale_id"] = "IM"  # Importance
            skill_info_imp["data_value"] = skill.get("importance", 0)
            skills_data.append(skill_info_imp)
        
        # Create DataFrame
        df = pd.DataFrame(skills_data)
        
        return {
            "success": True,
            "message": f"Successfully fetched skills data for {occupation_code}",
            "result": {"df": df}
        }
        
    except Exception as e:
        logging.error(f"Error fetching skills data: {str(e)}")
        return {
            "success": False,
            "message": f"Error fetching skills data: {str(e)}",
            "result": {}
        }

if __name__ == "__main__":
    # Example usage
    import os
    
    # Check if credentials are set
    if "ONET_API_USERNAME" in os.environ and "ONET_API_PASSWORD" in os.environ:
        # Example: Software Developers
        result = onet_api_pull("15-1252.00")
        
        if result["success"]:
            print("Occupation Data:")
            print(result["result"]["occupation_data"])
            print("\nSkills Data:")
            print(result["result"]["skills_data"])
        else:
            print(f"Error: {result['message']}")
    else:
        print("Please set ONET_API_USERNAME and ONET_API_PASSWORD environment variables to test.")