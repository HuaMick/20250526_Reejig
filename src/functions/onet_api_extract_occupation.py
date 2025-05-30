import requests
import pandas as pd
import time, io, logging
from typing import Dict, Any, Optional
from datetime import date
from src.config.schemas import OnetMappings
import xml.etree.ElementTree as ET
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def onet_api_extract_occupation(
    username: str,
    password: str,
    version: str = "1.9",
    initial_url_path: str = "/ws/database/rows/occupation_data",
    base_url: str = "https://services.onetcenter.org/",
) -> Dict[str, Any]:
    """
    Extracts all occupation data from the O*NET API, handling pagination.

    This function sends GET requests to the O*NET API to retrieve occupation data,
    parses the XML response into a pandas DataFrame, and follows 'next' links
    to fetch all pages of data.

    Args:
        username (str): The username for O*NET API authentication.
        password (str): The password for O*NET API authentication.
        version (str, optional): The API version to use. Defaults to "1.9".
        initial_url_path (str, optional): The specific initial API endpoint for occupation data.
                                     Defaults to "/ws/database/rows/occupation_data".
        base_url (str, optional): The base URL for the O*NET API.
                                  Defaults to "https://services.onetcenter.org/".

    Returns:
        Dict[str, Any]: A dictionary with the following keys:
            - "success" (bool): True if API calls were successful and data was parsed, False otherwise.
            - "message" (str): A message indicating the outcome of the operation.
            - "result" (Dict[str, pd.DataFrame] or None): A dictionary containing a pandas DataFrame
                                               with the key "occupation_df" if successful, otherwise None.
    """
    all_dfs = []
    current_request_url = f"{base_url.rstrip('/')}/v{version}{initial_url_path}"
    page_num = 1

    while current_request_url:
        logging.info(f"Requesting data from: {current_request_url} (Page {page_num})")
        try:
            response = requests.get(current_request_url, auth=(username, password), timeout=30)
            response.raise_for_status()

            if not response.text.strip():
                logging.warning(f"Received empty response from API for URL: {current_request_url}")
                break 

            # Parse XML to find the 'next' link
            next_page_url_from_xml = None
            try:
                root = ET.fromstring(response.content)
                next_link_element = root.find('./link[@rel="next"]')
                if next_link_element is not None and 'href' in next_link_element.attrib:
                    next_page_url_from_xml = next_link_element.attrib['href']
                    # Ensure the next URL is absolute if it's relative
                    if not next_page_url_from_xml.startswith('http'):
                        next_page_url_from_xml = f"{base_url.rstrip('/')}{next_page_url_from_xml}" \
                            if next_page_url_from_xml.startswith('/') \
                            else f"{base_url.rstrip('/')}/{next_page_url_from_xml}"
            except ET.ParseError as xml_err:
                logging.error(f"Error parsing XML to find next link from {current_request_url}: {xml_err}. Response text: {response.text[:500]}")
            
            current_request_url = next_page_url_from_xml # Update for next iteration or set to None

            xml_data_io = io.StringIO(response.text)
            df_page = pd.read_xml(xml_data_io, xpath="//row")

            if not df_page.empty:
                all_dfs.append(df_page)
                logging.info(f"Successfully extracted {len(df_page)} records from page {page_num}.")
            else:
                logging.info(f"No records found on page {page_num}.")

            page_num += 1
            if current_request_url: 
                time.sleep(0.5) 

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err} - URL: {current_request_url if current_request_url else response.url if response else 'N/A'} - Response: {response.text[:500] if response else 'No response text'}")
            return {"success": False, "message": f"HTTP error occurred: {http_err}", "result": None}
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err} - URL: {current_request_url if current_request_url else 'N/A'}")
            return {"success": False, "message": f"Connection error occurred: {conn_err}", "result": None}
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err} - URL: {current_request_url if current_request_url else 'N/A'}")
            return {"success": False, "message": f"Timeout error occurred: {timeout_err}", "result": None}
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An unexpected error occurred with the request: {req_err} - URL: {current_request_url if current_request_url else 'N/A'}")
            return {"success": False, "message": f"An unexpected error occurred with the request: {req_err}", "result": None}
        except pd.errors.ParserError as parse_err: 
            logging.error(f"Error parsing XML data with pandas from {response.url if response else 'N/A'}: {parse_err}. Response text: {response.text[:500] if response else 'N/A'}")
            if not all_dfs: 
                return {"success": False, "message": f"Error parsing XML data: {parse_err}", "result": None}
            else: 
                logging.warning("Pandas XML parsing error on a subsequent page. Returning successfully collected data so far.")
                current_request_url = None 
        except Exception as e:
            logging.error(f"An unexpected error occurred during pagination: {e} - URL: {current_request_url if current_request_url else response.url if response else 'N/A'}")
            if not all_dfs:
                 return {"success": False, "message": f"An unexpected error occurred: {e}", "result": None}
            else:
                logging.warning("Unexpected error on a subsequent page. Returning successfully collected data so far.")
                current_request_url = None 

    if not all_dfs:
        logging.info("No occupation data extracted after attempting all pages.")
        final_df = pd.DataFrame() 
    else:
        final_df = pd.concat(all_dfs, ignore_index=True)
    
    if not final_df.empty:
        final_df.rename(columns=OnetMappings.API_OCCUPATIONS_COLUMN_RENAME_MAP, inplace=True)
        final_df["last_updated"] = date.today()
        if 'onet_soc_code' not in final_df.columns:
            logging.warning(f"'onet_soc_code' column is missing after renaming. Columns found: {final_df.columns.tolist()}")

    logging.info(f"Successfully extracted a total of {len(final_df)} occupation records from API after handling pagination.")
    return {
        "success": True,
        "message": f"Occupation data extracted successfully. Total records: {len(final_df)}.",
        "result": {"occupation_df": final_df},
    }

if __name__ == '__main__':
    ONET_USERNAME = os.getenv("ONET_USERNAME_TEST", "YOUR_ONET_USERNAME")
    ONET_PASSWORD = os.getenv("ONET_PASSWORD_TEST", "YOUR_ONET_PASSWORD")

    if ONET_USERNAME == "YOUR_ONET_USERNAME" or ONET_PASSWORD == "YOUR_ONET_PASSWORD":
        print("Please replace 'YOUR_ONET_USERNAME' and 'YOUR_ONET_PASSWORD' with your actual O*NET credentials, or set ONET_USERNAME_TEST and ONET_PASSWORD_TEST environment variables to run the example.")
    else:
        print("Attempting to extract O*NET occupation data with pagination...")
        extraction_result = onet_api_extract_occupation(username=ONET_USERNAME, password=ONET_PASSWORD)
        if extraction_result["success"]:
            print("Successfully extracted occupation data.")
            df_occupations = extraction_result["result"]["occupation_df"]
            if df_occupations is not None:
                print(f"Total number of occupations found: {len(df_occupations)}")
                if not df_occupations.empty:
                    print("First 5 occupations:")
                    print(df_occupations.head())
                    print("\nLast 5 occupations:")
                    print(df_occupations.tail())
                else:
                    print("DataFrame is empty after extraction.")
            else:
                print("Extraction successful, but the DataFrame is None.")
        else:
            print(f"Failed to extract occupation data: {extraction_result['message']}")