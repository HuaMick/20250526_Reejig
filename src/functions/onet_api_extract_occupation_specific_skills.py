import requests
import pandas as pd
import io
import logging
import time # For potential delays
from typing import Dict, Any, Optional
from datetime import date
import xml.etree.ElementTree as ET # For parsing if needed, though pandas might handle it

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def onet_api_extract_occupation_specific_skills(
    onet_soc_code: str,
    username: str,
    password: str,
    version: str = "1.9",
    report_type: str = "details", # "summary" or "details"
    base_url: str = "https://services.onetcenter.org/"
) -> Dict[str, Any]:
    """
    Extracts skills data for a specific O*NET-SOC code from the O*NET API.

    This function calls the /online/occupations/{onet_soc_code}/{report_type}/skills endpoint.

    Args:
        onet_soc_code (str): The O*NET-SOC code for the occupation.
        username (str): The username for O*NET API authentication.
        password (str): The password for O*NET API authentication.
        version (str, optional): The API version to use. Defaults to "1.9".
        report_type (str, optional): "summary" or "details". Defaults to "details".
        base_url (str, optional): The base URL for the O*NET API.
                                  Defaults to "https://services.onetcenter.org/".

    Returns:
        Dict[str, Any]: A dictionary with keys "success", "message", and "result".
                        The "result" dictionary will contain "skills_df" with the data.
    """
    request_url = f"{base_url.rstrip('/')}/v{version}/ws/online/occupations/{onet_soc_code}/{report_type}/skills"
    logging.info(f"Requesting occupation-specific skills from: {request_url}")

    all_data = [] # To store data from <element> tags

    try:
        response = requests.get(request_url, auth=(username, password), timeout=30)
        response.raise_for_status()

        if not response.text.strip():
            logging.warning(f"Received empty response for occupation-specific skills: {onet_soc_code}")
            return {"success": True, "message": "API returned empty response, no skills data.", "result": {"skills_df": pd.DataFrame()}}

        # The XML structure is <skills><scale><element>...</element></scale></skills>
        # We need to parse this to get all <element> data under potentially multiple <scale>
        root = ET.fromstring(response.content)
        
        for scale_element in root.findall('.//scale'):
            scale_id = scale_element.get('id')
            scale_name = scale_element.get('name')
            for skill_element in scale_element.findall('./element'):
                data_value_tag = skill_element.find('./data_value')
                importance_tag = skill_element.find('./importance') # for summary reports
                level_tag = skill_element.find('./level') # for summary reports

                record = {
                    'onetsoc_code': onet_soc_code, # Add the occupation code for linking
                    'element_id': skill_element.get('id'),
                    'element_name': skill_element.findtext('./name'),
                    'scale_id': scale_id,
                    'scale_name': scale_name,
                    'data_value': data_value_tag.text if data_value_tag is not None else None,
                    'importance': importance_tag.text if importance_tag is not None else None,
                    'level': level_tag.text if level_tag is not None else None,
                    # Add other relevant fields from the <element> if needed
                    # e.g., description, n, standard_error, lower_ci_bound, upper_ci_bound
                    'description': skill_element.findtext('./description') 
                }
                all_data.append(record)
        
        skills_df = pd.DataFrame(all_data)

        if not skills_df.empty:
            # Standardize column names (already mostly standard from XML parsing)
            skills_df.columns = [col.lower().replace(' ', '_') for col in skills_df.columns]
            skills_df["last_updated"] = date.today() # Add our fetch date
            # Convert data_value to numeric, coercing errors
            if 'data_value' in skills_df.columns:
                skills_df['data_value'] = pd.to_numeric(skills_df['data_value'], errors='coerce')
            if 'importance' in skills_df.columns:
                skills_df['importance'] = pd.to_numeric(skills_df['importance'], errors='coerce')
            if 'level' in skills_df.columns:
                skills_df['level'] = pd.to_numeric(skills_df['level'], errors='coerce')


        logging.info(f"Successfully extracted {len(skills_df)} skills for occupation {onet_soc_code}.")
        return {"success": True, "message": f"Successfully extracted skills for {onet_soc_code}", "result": {"skills_df": skills_df}}

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error for {onet_soc_code} skills: {http_err} - URL: {request_url}")
        # Check if 404, meaning no skills data for this occupation (common for some occupations)
        if response and response.status_code == 404:
             logging.warning(f"No skills data (404) found for occupation {onet_soc_code} at {request_url}")
             return {"success": True, "message": f"No skills data (404) for {onet_soc_code}", "result": {"skills_df": pd.DataFrame()}} # Return empty df
        return {"success": False, "message": f"HTTP error for {onet_soc_code} skills: {http_err}", "result": None}
    except ET.ParseError as xml_err:
        logging.error(f"XML parsing error for {onet_soc_code} skills: {xml_err}. URL: {request_url}")
        return {"success": False, "message": f"XML parsing error for {onet_soc_code} skills: {xml_err}", "result": None}
    except Exception as e:
        logging.error(f"Unexpected error for {onet_soc_code} skills: {e} - URL: {request_url}")
        return {"success": False, "message": f"Unexpected error for {onet_soc_code} skills: {e}", "result": None}

if __name__ == '__main__':
    import os
    ONET_USERNAME = os.getenv("ONET_USERNAME_TEST", os.getenv("ONET_USERNAME"))
    ONET_PASSWORD = os.getenv("ONET_PASSWORD_TEST", os.getenv("ONET_PASSWORD"))
    TEST_OCC_CODE = "15-1254.00" # Web Developers

    if not ONET_USERNAME or not ONET_PASSWORD or ONET_USERNAME == "YOUR_ONET_USERNAME" or ONET_PASSWORD == "YOUR_ONET_PASSWORD":
        print(f"Please set ONET_USERNAME and ONET_PASSWORD environment variables to run example for {TEST_OCC_CODE}.")
    else:
        print(f"Attempting to extract skills for occupation code: {TEST_OCC_CODE} (report_type='details')...")
        result_details = onet_api_extract_occupation_specific_skills(
            onet_soc_code=TEST_OCC_CODE,
            username=ONET_USERNAME,
            password=ONET_PASSWORD,
            report_type="details"
        )
        if result_details["success"]:
            df_skills_details = result_details["result"]["skills_df"]
            print(f"Successfully extracted {len(df_skills_details)} skills (details report) for {TEST_OCC_CODE}.")
            if not df_skills_details.empty:
                print("Sample (details report):")
                print(df_skills_details.head())
        else:
            print(f"Failed to extract skills (details report) for {TEST_OCC_CODE}: {result_details['message']}")

        print(f"\nAttempting to extract skills for occupation code: {TEST_OCC_CODE} (report_type='summary')...")
        result_summary = onet_api_extract_occupation_specific_skills(
            onet_soc_code=TEST_OCC_CODE,
            username=ONET_USERNAME,
            password=ONET_PASSWORD,
            report_type="summary"
        )
        if result_summary["success"]:
            df_skills_summary = result_summary["result"]["skills_df"]
            print(f"Successfully extracted {len(df_skills_summary)} skills (summary report) for {TEST_OCC_CODE}.")
            if not df_skills_summary.empty:
                print("Sample (summary report):")
                print(df_skills_summary.head())
        else:
            print(f"Failed to extract skills (summary report) for {TEST_OCC_CODE}: {result_summary['message']}") 