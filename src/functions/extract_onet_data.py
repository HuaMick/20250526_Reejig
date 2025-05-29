import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

# Define standard column rename maps
OCCUPATIONS_COLUMN_RENAME_MAP = {
    "O*NET-SOC Code": "onet_soc_code",
    "Title": "title",
    "Description": "description",
}

SKILLS_COLUMN_RENAME_MAP = {
    "Element ID": "element_id",
    "Element Name": "element_name",
    "O*NET-SOC Code": "onet_soc_code",
    "Scale ID": "scale_id",
    "Data Value": "data_value",
    "N": "n_value",
    "Standard Error": "standard_error",
    "Lower CI Bound": "lower_ci_bound",
    "Upper CI Bound": "upper_ci_bound",
    "Recommend Suppress": "recommend_suppress",
    "Not Relevant": "not_relevant",
    "Date": "date_recorded",
    "Domain Source": "domain_source"
}

SCALES_COLUMN_RENAME_MAP = {
    "Scale ID": "scale_id",
    "Scale Name": "scale_name",
    "Minimum": "minimum",
    "Maximum": "maximum"
}

def _read_onet_file(file_path: str, column_rename_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Internal helper to read an O*NET data file and return a pandas DataFrame.
    Performs column renaming and data type conversions specific to O*NET files.
    Args:
        file_path (str): Path to the O*NET data file
        column_rename_map (Optional[Dict[str, str]]): Dictionary to rename columns
    Returns:
        pd.DataFrame: DataFrame containing the O*NET data
    Raises:
        FileNotFoundError: If the file_path does not exist.
        Exception: If pandas fails to read or process the file for other reasons.
    """
    if not os.path.exists(file_path):
        # This will be caught by the caller and reported
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path, sep='\t', low_memory=False) # Added low_memory=False for potentially mixed types
        
        if column_rename_map:
            existing_renames = {k: v for k, v in column_rename_map.items() if k in df.columns}
            df.rename(columns=existing_renames, inplace=True)
        
        if 'date_recorded' in df.columns:
            try:
                df['date_recorded'] = pd.to_datetime(df['date_recorded'], format='%Y%m', errors='coerce').dt.strftime('%Y-%m-%d')
                # Attempt to convert to date objects, coercing errors for flexibility
                df['date_recorded'] = pd.to_datetime(df['date_recorded'], errors='coerce').dt.date
            except Exception as e:
                # If specific parsing fails, log warning and attempt general conversion
                print(f"Warning: Could not parse 'date_recorded' with specific format in {os.path.basename(file_path)}. Attempting general conversion. Error: {e}")
                df['date_recorded'] = pd.to_datetime(df['date_recorded'], errors='coerce').dt.date

        if 'recommend_suppress' in df.columns:
            df['recommend_suppress'] = df['recommend_suppress'].astype(str).str[0]
        
        decimal_columns = ['data_value', 'standard_error', 'lower_ci_bound', 'upper_ci_bound']
        for col in decimal_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                if col == 'data_value':
                    df[col] = df[col].round(2)
                else:
                    df[col] = df[col].round(4)
        
        if 'n_value' in df.columns:
            df['n_value'] = pd.to_numeric(df['n_value'], errors='coerce').astype('Int64')
        
        integer_columns_scales = ['minimum', 'maximum']
        for col in integer_columns_scales:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                
        return df
    except Exception as e:
        # Re-raise to be caught by the main extract_onet_data function for reporting
        raise Exception(f"Error processing file {os.path.basename(file_path)} with pandas: {e}")

def extract_onet_data() -> Dict[str, Any]:
    """
    Extracts data from O*NET files specified by their relative paths from the project root.
    
    Returns:
        Dict[str, Any]: A dictionary with keys 'success' (bool), 'message' (str), 
                        and 'result' (dict with 'extracted_data' as List[Dict[str, Any]] 
                        and 'errors' as List[str]).
                        'extracted_data' contains successfully processed files and their DataFrames.
                        'errors' contains messages for files that failed to process.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    file_configs = [
        {'filename': 'occupations.txt', 'path_suffix': 'database/occupations.txt', 'map': OCCUPATIONS_COLUMN_RENAME_MAP,
         'string_cols': ['onet_soc_code', 'title', 'description']},
        {'filename': 'skills.txt', 'path_suffix': 'database/skills.txt', 'map': SKILLS_COLUMN_RENAME_MAP,
         'string_cols': ['element_id', 'element_name']},
        {'filename': 'scales.txt', 'path_suffix': 'database/scales.txt', 'map': SCALES_COLUMN_RENAME_MAP,
         'string_cols': ['scale_id', 'scale_name']}
    ]
    
    processed_data = []
    error_messages = []
    files_processed_count = 0
    files_succeeded_count = 0

    for config in file_configs:
        file_path = os.path.join(project_root, config['path_suffix'])
        files_processed_count += 1
        try:
            df = _read_onet_file(file_path, config['map'])
            for col in config.get('string_cols', []):
                if col in df.columns:
                    df[col] = df[col].astype(str)
            
            processed_data.append({
                'filename': config['filename'],
                'df': df
            })
            files_succeeded_count += 1
        except FileNotFoundError as fnf_e:
            msg = str(fnf_e)
            error_messages.append(msg)
            print(f"Error for {config['filename']}: {msg}")
        except Exception as e:
            msg = f"Error processing {config['filename']}: {e}"
            error_messages.append(msg)
            print(msg) # Also print to console for immediate feedback

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
