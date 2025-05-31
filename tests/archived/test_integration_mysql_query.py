from src.functions.mysql_query import mysql_query

def test_mysql_query():
    # Test query to find specific occupation
    query = "SELECT * FROM Occupations WHERE onet_soc_code = '19-2031.00';"
    result = mysql_query(query)
    
    # Print results for verification
    print("\nIntegration Test Results:")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print("\nColumns:")
        print(result['result']['columns'])
        print("\nRows:")
        for row in result['result']['rows']:
            print(row)
    
    # Check for any skills data
    skills_query = """
    SELECT os.onet_soc_code, o.title, COUNT(*) as skill_count
    FROM Occupation_Skills os
    JOIN Occupations o ON o.onet_soc_code = os.onet_soc_code
    WHERE os.scale_id = 'LV'
    GROUP BY os.onet_soc_code, o.title
    LIMIT 5;
    """
    skills_result = mysql_query(skills_query)
    print("\nSkills Data Sample:")
    if skills_result['success']:
        print("First 5 occupations with skills:")
        for row in skills_result['result']['rows']:
            print(f"- {row[0]} ({row[1]}): {row[2]} skills")
    
    # Assertions to verify the results
    assert result["success"] == True, f"Query failed: {result['message']}"
    assert 'columns' in result['result'], "Expected columns in result"
    assert 'rows' in result['result'], "Expected rows in result"
    
    # Verify we have the correct columns
    expected_columns = {'onet_soc_code', 'title', 'description'}
    actual_columns = set(result['result']['columns'])
    assert expected_columns.issubset(actual_columns), f"Missing expected columns. Found: {actual_columns}" 