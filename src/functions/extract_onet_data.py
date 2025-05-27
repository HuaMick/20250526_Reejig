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
    # Common fields for Occupation_Skills mapping
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

def read_onet_file(file_path: str, column_rename_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Reads an O*NET data file and returns a pandas DataFrame.
    
    Args:
        file_path (str): Path to the O*NET data file
        column_rename_map (Optional[Dict[str, str]]): Dictionary to rename columns
        
    Returns:
        pd.DataFrame: DataFrame containing the O*NET data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # O*NET files are tab-separated
    df = pd.read_csv(file_path, sep='\t')
    
    if column_rename_map:
        # Only rename columns that exist in the DataFrame
        existing_renames = {k: v for k, v in column_rename_map.items() if k in df.columns}
        df.rename(columns=existing_renames, inplace=True)
    
    # Handle data type conversions
    if 'date_recorded' in df.columns:
        # O*NET dates are typically in YYYY-MM-DD format
        try:
            df['date_recorded'] = pd.to_datetime(df['date_recorded'], format='%Y-%m-%d', errors='coerce').dt.date
        except Exception as e:
            print(f"Warning: Error parsing dates: {e}")
            # Fallback to more flexible parsing if strict format fails
            df['date_recorded'] = pd.to_datetime(df['date_recorded'], errors='coerce').dt.date
    
    if 'recommend_suppress' in df.columns:
        # Ensure single character
        df['recommend_suppress'] = df['recommend_suppress'].astype(str).str[0]
    
    # Handle decimal columns
    decimal_columns = ['data_value', 'standard_error', 'lower_ci_bound', 'upper_ci_bound']
    for col in decimal_columns:
        if col in df.columns:
            # Convert to float first to handle any string values
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Round to match schema precision
            if col == 'data_value':
                df[col] = df[col].round(2)  # DECIMAL(5,2)
            else:
                df[col] = df[col].round(4)  # DECIMAL(6,4)
    
    # Handle integer columns
    if 'n_value' in df.columns:
        df['n_value'] = pd.to_numeric(df['n_value'], errors='coerce').astype('Int64')  # nullable integer
    
    # Handle integer columns for Scales table
    integer_columns_scales = ['minimum', 'maximum']
    for col in integer_columns_scales:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            
    return df

def extract_onet_data() -> List[Dict[str, Any]]:
    """
    Extracts data from O*NET files and returns a list of dictionaries containing
    the filename and corresponding DataFrame.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries with 'filename' and 'df' keys
    """
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Define paths to O*NET data files
    occupations_path = os.path.join(project_root, 'database', 'occupations.txt')
    skills_path = os.path.join(project_root, 'database', 'skills.txt')
    scales_path = os.path.join(project_root, 'database', 'scales.txt')
    
    # List to store results
    results = []
    
    # Process occupations file
    try:
        occupations_df = read_onet_file(occupations_path, OCCUPATIONS_COLUMN_RENAME_MAP)
        # Ensure string columns are properly formatted
        occupations_df['onet_soc_code'] = occupations_df['onet_soc_code'].astype(str)
        occupations_df['title'] = occupations_df['title'].astype(str)
        occupations_df['description'] = occupations_df['description'].astype(str)
        
        results.append({
            'filename': 'occupations.txt',
            'df': occupations_df
        })
    except Exception as e:
        print(f"Error processing occupations file: {e}")
    
    # Process skills file
    try:
        skills_df = read_onet_file(skills_path, SKILLS_COLUMN_RENAME_MAP)
        # Ensure string columns are properly formatted
        if 'element_id' in skills_df.columns: # Check if column exists after rename
            skills_df['element_id'] = skills_df['element_id'].astype(str)
        if 'element_name' in skills_df.columns: # Check if column exists after rename
            skills_df['element_name'] = skills_df['element_name'].astype(str)
        
        results.append({
            'filename': 'skills.txt',
            'df': skills_df
        })
    except Exception as e:
        print(f"Error processing skills file: {e}")
    
    # Process scales file
    try:
        scales_df = read_onet_file(scales_path, SCALES_COLUMN_RENAME_MAP)
        # Ensure string columns are properly formatted
        if 'scale_id' in scales_df.columns:
            scales_df['scale_id'] = scales_df['scale_id'].astype(str)
        if 'scale_name' in scales_df.columns:
            scales_df['scale_name'] = scales_df['scale_name'].astype(str)
        
        results.append({
            'filename': 'scales.txt',
            'df': scales_df
        })
    except Exception as e:
        print(f"Error processing scales file: {e}")
    
    return results

if __name__ == '__main__':
    # Test the extraction
    results = extract_onet_data()
    for result in results:
        print(f"\nProcessing {result['filename']}:")
        print(f"DataFrame shape: {result['df'].shape}")
        print("\nFirst few rows:")
        print(result['df'].head())
        print("\nDataFrame info:")
        print(result['df'].info())
