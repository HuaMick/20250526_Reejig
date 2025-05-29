import requests
import pandas as pd
import time, io, logging
from typing import Dict, Any, Optional
from datetime import date
from src.config.schemas import OnetMappings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def onet_api_extract_scales(
    username: str,
    password: str,
    version: str = "1.9",
    url: str = "/ws/database/rows/scales_reference",
    base_url: str = "https://services.onetcenter.org/",
) -> Dict[str, Any]:
    """
    Extracts scales reference data from the O*NET API.

    This function sends a GET request to the O*NET API to retrieve scales reference data,
    then parses the XML response into a pandas DataFrame.

    Args:
        username (str): The username for O*NET API authentication.
        password (str): The password for O*NET API authentication.
        version (str, optional): The API version to use. Defaults to "1.9".
        url (str, optional): The specific API endpoint for scales reference data.
                             Defaults to "/ws/database/rows/scales_reference".
        base_url (str, optional): The base URL for the O*NET API.
                                  Defaults to "https://services.onetcenter.org/".

    Returns:
        Dict[str, Any]: A dictionary with the following keys:
            - "success" (bool): True if the API call was successful and data was parsed, False otherwise.
            - "message" (str): A message indicating the outcome of the operation.
            - "result" (Dict[str, pd.DataFrame] or None): A dictionary containing a pandas DataFrame
                                               with the key "scales_df" if successful, otherwise None.
    """
    request_url = f"{base_url.rstrip('/')}/v{version}{url}"
    logging.info(f"Requesting data from: {request_url}")

    try:
        response = requests.get(request_url, auth=(username, password))
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        
        # Check if response content is empty or not valid XML before parsing
        if not response.text.strip():
            logging.warning("Received empty response from API.")
            return {
                "success": False,
                "message": "Received empty response from API.",
                "result": None,
            }

        df = pd.read_xml(io.StringIO(response.text), xpath="//row")
        
        if not df.empty:
            # Standardize column names generically
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Add last_updated column
            df["last_updated"] = date.today()

        return {
            "success": True,
            "message": "Scales reference data extracted successfully.",
            "result": {"scales_df": df},
        }
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Response: {response.text[:500]}")
        return {
            "success": False,
            "message": f"HTTP error occurred: {http_err}",
            "result": None,
        }
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred: {conn_err}")
        return {
            "success": False,
            "message": f"Connection error occurred: {conn_err}",
            "result": None,
        }
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred: {timeout_err}")
        return {
            "success": False,
            "message": f"Timeout error occurred: {timeout_err}",
            "result": None,
        }
    except requests.exceptions.RequestException as req_err:
        logging.error(f"An unexpected error occurred with the request: {req_err}")
        return {
            "success": False,
            "message": f"An unexpected error occurred with the request: {req_err}",
            "result": None,
        }
    except pd.errors.ParserError as parse_err:
        logging.error(f"Error parsing XML data: {parse_err}. Response text: {response.text[:500]}")
        return {
            "success": False,
            "message": f"Error parsing XML data: {parse_err}",
            "result": None,
        }
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {
            "success": False,
            "message": f"An unexpected error occurred: {e}",
            "result": None,
        }


if __name__ == '__main__':
    # !!! IMPORTANT !!!
    # Replace with your actual O*NET username and password before running.
    # You might want to use environment variables or a config file for credentials.
    ONET_USERNAME = "YOUR_ONET_USERNAME"  # Replace with your username
    ONET_PASSWORD = "YOUR_ONET_PASSWORD"  # Replace with your password

    if ONET_USERNAME == "YOUR_ONET_USERNAME" or ONET_PASSWORD == "YOUR_ONET_PASSWORD":
        print("Please replace 'YOUR_ONET_USERNAME' and 'YOUR_ONET_PASSWORD' with your actual O*NET credentials to run the example.")
    else:
        print("Attempting to extract O*NET scales reference data...")
        extraction_result = onet_api_extract_scales(username=ONET_USERNAME, password=ONET_PASSWORD)

        if extraction_result["success"]:
            print("Successfully extracted scales reference data.")
            df_scales = extraction_result["result"]["scales_df"]
            if df_scales is not None and not df_scales.empty:
                print(f"Number of scale records found: {len(df_scales)}")
                print("First 5 scale records:")
                print(df_scales.head())
            else:
                print("Extraction successful, but no data was returned or the DataFrame is empty.")
        else:
            print(f"Failed to extract scales reference data: {extraction_result['message']}")
