import requests
import pandas as pd
import time
import logging
from typing import Dict, Any, Optional

def extract_onet_api_occupation_codes(
    api_username: str, 
    api_key: str, 
    client_name: str, 
    base_url: str
) -> Dict[str, Any]:
    """
    Fetches all O*NET-SOC occupation codes and titles from the O*NET API.
    
    Args:
        api_username (str): The API username for O*NET Web Services
        api_key (str): The API key for O*NET Web Services
        client_name (str): The registered client name for the O*NET API
        base_url (str): The base URL for the O*NET API (e.g., 'https://services.onetcenter.org/v1.9/ws')
        
    Returns:
        Dict[str, Any]: A dictionary with the following structure:
            {
                "success": bool,  # Whether the operation was successful
                "message": str,   # Message describing the operation's outcome
                "result": {
                    "occupation_codes_df": pd.DataFrame  # DataFrame containing O*NET-SOC codes and titles
                }
            }
    
    Raises:
        No exceptions are raised directly; errors are captured and reported in the return value.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Initialize return values
    result = {
        "success": False,
        "message": "",
        "result": {
            "occupation_codes_df": None
        }
    }
    
    try:
        # Create a session for making API requests
        session = requests.Session()
        session.auth = (api_username, api_key)
        session.headers.update({
            'Accept': 'application/json'
        })
        
        # Define endpoint for all occupations
        occupations_endpoint = f"{base_url}/online/occupations/"
        
        # Initialize variables for pagination
        all_occupations = []
        current_start = 1
        page_size = 100  # Request 100 occupations per page to minimize API calls
        total_occupations = None
        rate_limit_delay = 0.25  # 250ms delay between API calls (respects rate limits)
        
        # Fetch all occupations with pagination
        while True:
            # Construct query parameters
            params = {
                'clientname': client_name,
                'sort': 'code',  # Sort by O*NET-SOC code
                'start': current_start,
                'end': current_start + page_size - 1
            }
            
            logger.info(f"Fetching occupations {current_start} to {current_start + page_size - 1}")
            
            # Make API request
            try:
                response = session.get(occupations_endpoint, params=params)
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
                
                # Parse JSON response
                data = response.json()
                
                # Get total number of occupations if not already known
                if total_occupations is None:
                    total_occupations = data.get('total', 0)
                    logger.info(f"Total occupations: {total_occupations}")
                
                # Extract occupations from response
                occupations = data.get('occupation', [])
                
                # Add occupations to our list
                for occ in occupations:
                    all_occupations.append({
                        'onet_soc_code': occ.get('code', ''),
                        'title': occ.get('title', '')
                    })
                
                # Check if we've fetched all occupations
                if not occupations or len(all_occupations) >= total_occupations:
                    break
                
                # Update start index for next page
                current_start += len(occupations)
                
                # Respect rate limits with a delay
                time.sleep(rate_limit_delay)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"API request failed: {str(e)}"
                if hasattr(e, 'response') and e.response is not None:
                    error_msg += f" (Status code: {e.response.status_code})"
                    # Handle specific HTTP error codes
                    if e.response.status_code == 401:
                        error_msg += " - Invalid API credentials"
                    elif e.response.status_code == 429:
                        error_msg += " - Rate limit exceeded"
                
                logger.error(error_msg)
                result["message"] = error_msg
                return result
        
        # Create DataFrame from all occupations
        if all_occupations:
            df = pd.DataFrame(all_occupations)
            
            # Ensure columns are of string type
            df['onet_soc_code'] = df['onet_soc_code'].astype(str)
            df['title'] = df['title'].astype(str)
            
            # Update result
            result["success"] = True
            result["message"] = f"Successfully fetched {len(df)} O*NET-SOC occupation codes and titles."
            result["result"]["occupation_codes_df"] = df
        else:
            result["message"] = "No occupations found in the API response."
        
    except Exception as e:
        error_msg = f"Error fetching O*NET-SOC occupation codes: {str(e)}"
        logger.error(error_msg)
        result["message"] = error_msg
    
    return result

if __name__ == '__main__':
    print("Example usage of extract_onet_api_occupation_codes:")
    print("This example assumes valid O*NET API credentials are provided.")
    
    # These would typically come from environment variables or secure storage
    example_username = "your_api_username"
    example_key = "your_api_key"
    example_client = "your_client_name"
    example_base_url = "https://services.onetcenter.org/v1.9/ws"
    
    print("\nNote: This example will not run without valid credentials.")
    print("To run with real credentials, replace the example values and uncomment:")
    print("""
    # result = extract_onet_api_occupation_codes(
    #     api_username=example_username,
    #     api_key=example_key,
    #     client_name=example_client,
    #     base_url=example_base_url
    # )
    # 
    # print(f"Success: {result['success']}")
    # print(f"Message: {result['message']}")
    # if result['success']:
    #     df = result['result']['occupation_codes_df']
    #     print(f"DataFrame shape: {df.shape}")
    #     print("First 5 rows:")
    #     print(df.head(5))
    """) 