import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.config.schemas import OnetMappings, Onet_Occupations_Landing, Onet_Skills_Landing, Onet_Scales_Landing
from src.functions.textfile_to_dataframe import textfile_to_dataframe

def extract_occupations(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract occupations data from O*NET text file.
    
    Args:
        file_path (Optional[str]): Path to the occupations file. If None, uses default path.
        
    Returns:
        Dict[str, Any]: Dictionary with 'success', 'df', and 'error' keys
    """
    if file_path is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        file_path = os.path.join(project_root, 'database/occupations.txt')
    
    dtype = {col: str for col in Onet_Occupations_Landing.string_columns}
    
    return textfile_to_dataframe(
        file_path=file_path,
        column_rename_map=OnetMappings.OCCUPATIONS_COLUMN_RENAME_MAP,
        dtype=dtype
    )

def extract_skills(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract skills data from O*NET text file.
    
    Args:
        file_path (Optional[str]): Path to the skills file. If None, uses default path.
        
    Returns:
        Dict[str, Any]: Dictionary with 'success', 'df', and 'error' keys
    """
    if file_path is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        file_path = os.path.join(project_root, 'database/skills.txt')
    
    dtype = {
        'element_id': str,
        'element_name': str,
        'onet_soc_code': str,
        'scale_id': str,
        'data_value': float,
        'n_value': 'Int64',
        'standard_error': float,
        'lower_ci_bound': float, 
        'upper_ci_bound': float,
        'not_relevant': str,
        'domain_source': str
    }
    
    return textfile_to_dataframe(
        file_path=file_path,
        column_rename_map=OnetMappings.SKILLS_COLUMN_RENAME_MAP,
        dtype=dtype,
        date_columns=['date_recorded']
    )

def extract_scales(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract scales data from O*NET text file.
    
    Args:
        file_path (Optional[str]): Path to the scales file. If None, uses default path.
        
    Returns:
        Dict[str, Any]: Dictionary with 'success', 'df', and 'error' keys
    """
    if file_path is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        file_path = os.path.join(project_root, 'database/scales.txt')
    
    dtype = {
        'scale_id': str,
        'scale_name': str,
        'minimum': 'Int64',
        'maximum': 'Int64'
    }
    
    return textfile_to_dataframe(
        file_path=file_path,
        column_rename_map=OnetMappings.SCALES_COLUMN_RENAME_MAP,
        dtype=dtype
    )

def extract_onet_data() -> Dict[str, Any]:
    """
    Extracts data from all O*NET files and combines the results.
    
    Returns:
        Dict[str, Any]: A dictionary with keys 'success' (bool), 'message' (str), 
                        and 'result' (dict with 'extracted_data' as List[Dict[str, Any]] 
                        and 'errors' as List[str]).
                        'extracted_data' contains successfully processed files and their DataFrames.
                        'errors' contains messages for files that failed to process.
    """
    extraction_functions = [
        {'name': 'occupations.txt', 'function': extract_occupations},
        {'name': 'skills.txt', 'function': extract_skills},
        {'name': 'scales.txt', 'function': extract_scales}
    ]
    
    processed_data = []
    error_messages = []
    files_processed_count = len(extraction_functions)
    files_succeeded_count = 0

    for config in extraction_functions:
        try:
            result = config['function']()
            if result['success']:
                processed_data.append({
                    'filename': config['name'],
                    'df': result['df']
                })
                files_succeeded_count += 1
            else:
                error_messages.append(f"Error for {config['name']}: {result['error']}")
                print(f"Error for {config['name']}: {result['error']}")
        except Exception as e:
            msg = f"Error processing {config['name']}: {e}"
            error_messages.append(msg)
            print(msg)

    overall_success = files_succeeded_count > 0 and files_succeeded_count == files_processed_count
    message = f"Data extraction complete. {files_succeeded_count}/{files_processed_count} files processed successfully."
    if error_messages:
        message += " Errors encountered: " + "; ".join(error_messages)

    return {
        "success": overall_success,
        "message": message,
        "result": {
            "extracted_data": processed_data,
            "errors": error_messages
        }
    }

if __name__ == '__main__':
    print("Minimalistic happy path example for extract_onet_data:")
    print("This example assumes O*NET files (e.g., occupations.txt) exist in the ./database/ directory.")

    # 1. Call the function
    extraction_result = extract_onet_data()

    # 2. Print the raw result from the function
    print("\nFunction Call Result:")
    print(f"  Success: {extraction_result['success']}")
    print(f"  Message: {extraction_result['message']}")
    # For brevity, we won't print the full DataFrames here, just a summary.
    if extraction_result["result"] and extraction_result["result"]["extracted_data"]:
        print("  Summary of Extracted DataFrames:")
        for item in extraction_result["result"]["extracted_data"]:
            print(f"    - {item['filename']}: Shape {item['df'].shape}")
    else:
        print("  No DataFrames were successfully extracted (as reported by the function).")
    
    if extraction_result["result"] and extraction_result["result"]["errors"]:
        print("  Extraction Errors Reported by Function:")
        for error_msg in extraction_result["result"]["errors"]:
            print(f"    - {error_msg}")
    print("\nExample finished.")
