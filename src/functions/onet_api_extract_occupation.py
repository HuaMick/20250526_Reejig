import requests
import pandas as pd
import time, io, logging
from typing import Dict, Any, Optional, List
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
    filter_params: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Extracts occupation data from the O*NET API, handling pagination and optional filtering.

    Args:
        username (str): The username for O*NET API authentication.
        password (str): The password for O*NET API authentication.
        version (str, optional): The API version to use. Defaults to "1.9".
        initial_url_path (str, optional): The specific initial API endpoint for occupation data.
                                     Defaults to "/ws/database/rows/occupation_data".
        base_url (str, optional): The base URL for the O*NET API.
                                  Defaults to "https://services.onetcenter.org/".
        filter_params (Optional[List[str]], optional): A list of filter strings 
                                                     (e.g., ["onetsoc_code.eq.CODE"]). 
                                                     Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary with the keys "success", "message", and "result".
    """
    all_dfs = []
    
    # Construct the initial URL
    url_params = []
    if filter_params:
        for f_param in filter_params:
            url_params.append(f"filter={f_param}")
    
    query_string = "&amp;".join(url_params)
    query_string = "&".join(url_params)

    current_request_url = f"{base_url.rstrip('/')}/v{version}{initial_url_path}"
    if query_string:
        current_request_url += f"?{query_string}"

    page_num = 1

    while current_request_url:
        logging.info(f"Requesting data from: {current_request_url} (Page {page_num})")
        try:
            response = requests.get(current_request_url, auth=(username, password), timeout=30)
            response.raise_for_status()

            if not response.text.strip():
                logging.warning(f"Received empty response from API for URL: {current_request_url}")
                break 

            next_page_url_from_xml = None
            try:
                root = ET.fromstring(response.content)
                next_link_element = root.find('./link[@rel="next"]')
                if next_link_element is not None and 'href' in next_link_element.attrib:
                    next_page_url_from_xml = next_link_element.attrib['href']
                    # O*NET next links are usually absolute and preserve query parameters
            except ET.ParseError as xml_err:
                logging.error(f"Error parsing XML to find next link from {current_request_url}: {xml_err}. Response text: {response.text[:500]}")
            
            current_request_url = next_page_url_from_xml

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
            err_url = current_request_url if current_request_url else (response.url if response else 'N/A')
            err_resp_text = response.text[:500] if response else 'No response text'
            logging.error(f"HTTP error occurred: {http_err} - URL: {err_url} - Response: {err_resp_text}")
            return {"success": False, "message": f"HTTP error occurred: {http_err}", "result": None}
        except requests.exceptions.ConnectionError as conn_err:
            err_url = current_request_url if current_request_url else 'N/A'
            logging.error(f"Connection error occurred: {conn_err} - URL: {err_url}")
            return {"success": False, "message": f"Connection error occurred: {conn_err}", "result": None}
        except requests.exceptions.Timeout as timeout_err:
            err_url = current_request_url if current_request_url else 'N/A'
            logging.error(f"Timeout error occurred: {timeout_err} - URL: {err_url}")
            return {"success": False, "message": f"Timeout error occurred: {timeout_err}", "result": None}
        except requests.exceptions.RequestException as req_err:
            err_url = current_request_url if current_request_url else 'N/A'
            logging.error(f"An unexpected error occurred with the request: {req_err} - URL: {err_url}")
            return {"success": False, "message": f"An unexpected error occurred with the request: {req_err}", "result": None}
        except pd.errors.ParserError as parse_err: 
            err_url = response.url if response else 'N/A'
            err_resp_text = response.text[:500] if response else 'N/A'
            logging.error(f"Error parsing XML data with pandas from {err_url}: {parse_err}. Response text: {err_resp_text}")
            if not all_dfs: 
                return {"success": False, "message": f"Error parsing XML data: {parse_err}", "result": None}
            else: 
                logging.warning("Pandas XML parsing error on a subsequent page. Returning successfully collected data so far.")
                current_request_url = None 
        except Exception as e:
            err_url = current_request_url if current_request_url else (response.url if response else 'N/A')
            logging.error(f"An unexpected error occurred during pagination: {e} - URL: {err_url}")
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
        if 'onet_soc_code' not in final_df.columns and not final_df.empty:
            logging.warning(f"'onet_soc_code' column is missing after renaming. Columns found: {final_df.columns.tolist()}")

    total_records = len(final_df)
    logging.info(f"Successfully extracted a total of {total_records} occupation records from API after handling pagination.")
    return {
        "success": True,
        "message": f"Occupation data extracted successfully. Total records: {total_records}.",
        "result": {"occupation_df": final_df},
    }

if __name__ == '__main__':
    ONET_USERNAME = os.getenv("ONET_USERNAME_TEST", os.getenv("ONET_USERNAME"))
    ONET_PASSWORD = os.getenv("ONET_PASSWORD_TEST", os.getenv("ONET_PASSWORD"))

    if not ONET_USERNAME or not ONET_PASSWORD or ONET_USERNAME == "YOUR_ONET_USERNAME" or ONET_PASSWORD == "YOUR_ONET_PASSWORD":
        print("Please set ONET_USERNAME and ONET_PASSWORD environment variables to run the example.")
    else:
        # print("Attempting to extract O*NET occupation data with pagination (no filter)...")
        # extraction_result_all = onet_api_extract_occupation(username=ONET_USERNAME, password=ONET_PASSWORD)
        # if extraction_result_all["success"]:
        #     df_all = extraction_result_all["result"]["occupation_df"]
        #     print(f"Total occupations (no filter): {len(df_all)}")
        #     if not df_all.empty:
        #         print("First 2 (no filter):")
        #         print(df_all.head(2))
        # else:
        #     print(f"Failed (no filter): {extraction_result_all['message']}")

        print("\nMinimalistic happy path example for onet_api_extract_occupation:")
        print("Attempting to extract specific O*NET occupation data (e.g., 15-1254.00 Web Developers)...")
        test_filter = ["onetsoc_code.eq.15-1254.00"]
        extraction_result_filtered = onet_api_extract_occupation(username=ONET_USERNAME, password=ONET_PASSWORD, filter_params=test_filter)
        
        print(f"\nFunction Call Result (filtered for {test_filter[0]}):")
        print(f"  Success: {extraction_result_filtered['success']}")
        print(f"  Message: {extraction_result_filtered['message']}")

        if extraction_result_filtered["success"] and extraction_result_filtered["result"]:
            df_filtered = extraction_result_filtered["result"]["occupation_df"]
            print(f"  Total occupations extracted: {len(df_filtered)}")
            if not df_filtered.empty:
                print(f"  First extracted occupation details: \n{df_filtered.head(1)}")
        
        print("\nExample finished.")