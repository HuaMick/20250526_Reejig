import requests
import pandas as pd
import time, io, logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from src.config.schemas import OnetMappings
import xml.etree.ElementTree as ET
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def onet_api_extract_skills(
    username: str,
    password: str,
    version: str = "1.9",
    initial_url_path: str = "/ws/database/rows/skills",
    base_url: str = "https://services.onetcenter.org/",
    filter_params: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Extracts skills data from the O*NET API generic /ws/database/rows/skills endpoint,
    handling pagination and optional filtering. This endpoint provides skills linked to occupations.
    """
    all_parsed_rows = []
    
    current_request_url = f"{base_url.rstrip('/')}/v{version}{initial_url_path}"
    page_num = 1
    is_first_request = True

    while current_request_url:
        request_params_for_requests_lib = {}
        if is_first_request and filter_params:
            request_params_for_requests_lib['filter'] = filter_params # requests will handle list as multiple params with same key
            is_first_request = False # Filters only needed for the first request URL construction
        
        # For subsequent requests, current_request_url is the full URL from 'next' link, already including filters
        logging.info(f"Requesting skills data from: {current_request_url} (Page {page_num}) with params: {request_params_for_requests_lib if page_num == 1 else 'via next link'}")
        
        try:
            # Only pass params dict for the initial manually constructed URL
            # Subsequent URLs from 'next' links already have params embedded.
            if page_num == 1 and request_params_for_requests_lib:
                 response = requests.get(current_request_url, auth=(username, password), params=request_params_for_requests_lib, timeout=30)
            else:
                 response = requests.get(current_request_url, auth=(username, password), timeout=30) # No params arg here
            
            response.raise_for_status()

            if not response.text.strip():
                logging.warning(f"Received empty response from skills API: {current_request_url}")
                break

            next_page_url_from_xml = None
            root = ET.fromstring(response.content)
            next_link_element = root.find('./link[@rel="next"]')
            if next_link_element is not None and 'href' in next_link_element.attrib:
                next_page_url_from_xml = next_link_element.attrib['href']
            
            current_request_url = next_page_url_from_xml # This will be None if no next link

            for row_element in root.findall('.//row'):
                # Helper to get text, returning None if tag not found
                def get_text_or_none(element, tag_name):
                    tag = element.find(tag_name)
                    return tag.text if tag is not None else None

                parsed_row = {
                    'onetsoc_code': get_text_or_none(row_element, 'onetsoc_code'),
                    'element_id': get_text_or_none(row_element, 'element_id'),
                    'element_name': get_text_or_none(row_element, 'element_name'),
                    'scale_id': get_text_or_none(row_element, 'scale_id'),
                    'scale_name': get_text_or_none(row_element, 'scale_name'),
                    'data_value': get_text_or_none(row_element, 'data_value'),
                    'n_value': get_text_or_none(row_element, 'n'), # XML tag is <n>
                    'standard_error': get_text_or_none(row_element, 'standard_error'),
                    'lower_ci_bound': get_text_or_none(row_element, 'lower_ci_bound'),
                    'upper_ci_bound': get_text_or_none(row_element, 'upper_ci_bound'),
                    'recommend_suppress': get_text_or_none(row_element, 'recommend_suppress'),
                    'not_relevant': get_text_or_none(row_element, 'not_relevant'),
                    'onet_update_date': get_text_or_none(row_element, 'date_updated'), # O*NET's update date
                    'domain_source': get_text_or_none(row_element, 'domain_source')
                    # 'title' (occupation title) is also available but usually not stored with skills directly
                }
                all_parsed_rows.append(parsed_row)
            
            logging.info(f"Parsed {len(root.findall('.//row'))} skills records from page {page_num}.")

            page_num += 1
            if current_request_url:
                time.sleep(0.5)

        except requests.exceptions.HTTPError as http_err:
            err_url_log = response.url if response else current_request_url # Log actual URL used
            logging.error(f"HTTP error (skills): {http_err} - URL: {err_url_log}")
            return {"success": False, "message": f"HTTP error (skills): {http_err}", "result": None}
        except ET.ParseError as xml_err:
            err_url_log = response.url if response else current_request_url
            logging.error(f"XML parsing error for skills: {xml_err}. URL: {err_url_log}")
            if not all_parsed_rows:
                return {"success": False, "message": f"XML parsing error (skills): {xml_err}", "result": None}
            else:
                logging.warning("XML parsing error on subsequent skills page. Returning collected data.")
                current_request_url = None
        except Exception as e:
            err_url_log = response.url if response else current_request_url
            logging.error(f"Unexpected error extracting skills: {e} - URL: {err_url_log}")
            if not all_parsed_rows:
                 return {"success": False, "message": f"Unexpected error (skills): {e}", "result": None}
            else:
                logging.warning("Error on subsequent skills page. Returning collected data.")
                current_request_url = None

    if not all_parsed_rows:
        logging.info("No skills data extracted after all pages.")
        final_df = pd.DataFrame() 
    else:
        final_df = pd.DataFrame(all_parsed_rows)
    
    if not final_df.empty:
        # Type conversions
        numeric_cols = ['data_value', 'n_value', 'standard_error', 'lower_ci_bound', 'upper_ci_bound']
        for col in numeric_cols:
            if col in final_df.columns:
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
        
        if 'onet_update_date' in final_df.columns:
            final_df['onet_update_date'] = pd.to_datetime(final_df['onet_update_date'], errors='coerce').dt.date

        final_df["last_updated"] = date.today() # Our fetch date
        # No general column renaming needed as we parse directly to desired names

    total_records = len(final_df)
    logging.info(f"Extracted total of {total_records} skills records from generic skills API.")
    return {
        "success": True,
        "message": f"Skills data extracted from generic endpoint. Total records: {total_records}.",
        "result": {"skills_df": final_df},
    }

if __name__ == '__main__':
    ONET_USERNAME = os.getenv("ONET_USERNAME_TEST", os.getenv("ONET_USERNAME"))
    ONET_PASSWORD = os.getenv("ONET_PASSWORD_TEST", os.getenv("ONET_PASSWORD"))

    if not ONET_USERNAME or not ONET_PASSWORD or ONET_USERNAME == "YOUR_ONET_USERNAME" or ONET_PASSWORD == "YOUR_ONET_PASSWORD":
        print("Please set ONET_USERNAME and ONET_PASSWORD environment variables.")
    else:
        print("Attempting to extract skills filtered by onetsoc_code (15-1254.00)...")
        # Test with a specific filter that should return results
        specific_code_filter = ["onetsoc_code.eq.15-1254.00"] 
        extraction_result_filtered = onet_api_extract_skills(username=ONET_USERNAME, password=ONET_PASSWORD, filter_params=specific_code_filter)
        
        if extraction_result_filtered["success"]:
            df_filtered = extraction_result_filtered["result"]["skills_df"]
            print(f"Total skills (filtered for 15-1254.00): {len(df_filtered)}")
            if not df_filtered.empty:
                print("Filtered skills result (first 5) with selected columns:")
                cols_to_show = ['onetsoc_code', 'element_id', 'element_name', 'scale_id', 'data_value', 'onet_update_date']
                # Ensure all columns in cols_to_show exist in df_filtered before trying to print
                actual_cols_to_show = [col for col in cols_to_show if col in df_filtered.columns]
                print(df_filtered[actual_cols_to_show].head())
            else:
                print("No skills data returned for the filter 15-1254.00, but extraction call was successful.")
        else:
            print(f"Failed to extract skills (filtered for 15-1254.00): {extraction_result_filtered['message']}")

        # Example for no filter (bulk)
        # print("\nAttempting to extract all O*NET skills (paginated from /ws/database/rows/skills)...")
        # extraction_result_all = onet_api_extract_skills(username=ONET_USERNAME, password=ONET_PASSWORD)
        # if extraction_result_all["success"]:
        #     df_all = extraction_result_all["result"]["skills_df"]
        #     print(f"Total skills (no filter): {len(df_all)}")
        #     if not df_all.empty:
        #         print("First 2 skills (no filter) with selected columns:")
        #         cols_to_show = ['onetsoc_code', 'element_id', 'element_name', 'scale_id', 'data_value', 'onet_update_date']
        #         actual_cols_to_show = [col for col in cols_to_show if col in df_all.columns]
        #         print(df_all[actual_cols_to_show].head(2))
        # else:
        #     print(f"Failed (no filter): {extraction_result_all['message']}")