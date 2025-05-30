import os
import pandas as pd
from typing import Dict, Any, Optional, List


def textfile_to_dataframe(
    file_path: str, 
    column_rename_map: Optional[Dict[str, str]] = None,
    dtype: Optional[Dict[str, Any]] = None,
    date_columns: Optional[List[str]] = None,
    separator: str = '\t'
) -> Dict[str, Any]:
    """
    Convert a text file to a pandas DataFrame, leveraging pandas' built-in functionality.
    
    Args:
        file_path (str): Path to the text file
        column_rename_map (Optional[Dict[str, str]]): Dictionary to rename columns
        dtype (Optional[Dict[str, Any]]): Dictionary mapping columns to their data types
        date_columns (Optional[List[str]]): List of columns to convert to date type
        separator (str): Column separator in the file, defaults to tab
        
    Returns:
        Dict[str, Any]: Dictionary with keys 'success', 'df', and 'error'
    """
    result = {
        'success': False,
        'df': None,
        'error': None
    }
    
    if not os.path.exists(file_path):
        result['error'] = f"File not found: {file_path}"
        return result
    
    try:
        # Read the file into a DataFrame with specified data types
        df = pd.read_csv(file_path, sep=separator, dtype=dtype, low_memory=False)
        
        # Rename columns if a mapping is provided
        if column_rename_map:
            existing_renames = {k: v for k, v in column_rename_map.items() if k in df.columns}
            df.rename(columns=existing_renames, inplace=True)
        
        # Process date columns
        if date_columns:
            for col in date_columns:
                if col in df.columns:
                    try:
                        # First try a specific format (for O*NET data)
                        df[col] = pd.to_datetime(df[col], format='%Y%m', errors='coerce')
                    except Exception:
                        # If specific format fails, try general conversion
                        df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Special handling for recommend_suppress column (O*NET specific)
        if 'recommend_suppress' in df.columns:
            df['recommend_suppress'] = df['recommend_suppress'].astype(str).str[0]
        
        result['success'] = True
        result['df'] = df
        return result
    
    except Exception as e:
        result['error'] = f"Error processing file {os.path.basename(file_path)}: {str(e)}"
        return result

if __name__ == '__main__':
    # Minimalistic happy path example for textfile_to_dataframe.
    # This example assumes a sample tab-separated text file named 'sample_data.txt'
    # exists in the same directory with simple data.

    # 1. Create a dummy sample_data.txt for the example
    sample_file_path = "sample_data.txt"
    with open(sample_file_path, 'w') as f:
        f.write("col1\\tcol2\\tcol3\\n")
        f.write("a\\tb\\t1\\n")
        f.write("c\\td\\t2\\n")

    # 2. Define parameters for the function call
    rename_map = {"col1": "ID", "col2": "Value"}
    dtypes = {"col3": int} # 'ID' and 'Value' will be inferred as object/string

    print(f"Attempting to convert '{sample_file_path}' to DataFrame...")
    conversion_result = textfile_to_dataframe(
        file_path=sample_file_path,
        column_rename_map=rename_map,
        dtype=dtypes
    )

    # 3. Print the result summary
    print("\\nFunction Call Result:")
    print(f"  Success: {conversion_result['success']}")
    if conversion_result['success'] and conversion_result['df'] is not None:
        print(f"  DataFrame shape: {conversion_result['df'].shape}")
        print("  DataFrame head:")
        print(conversion_result['df'].head())
    elif conversion_result['error']:
        print(f"  Error: {conversion_result['error']}")

    # 4. Clean up the dummy file
    if os.path.exists(sample_file_path):
        os.remove(sample_file_path)

    print("\\nExample finished.")
