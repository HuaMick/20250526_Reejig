from src.functions.get_occupation_skills import get_occupation_skills
from src.functions.mysql_query import mysql_query

def test_get_occupation_skills():
    # Debug: Check tables first
    tables_result = mysql_query("SHOW TABLES;")
    print("\nAvailable Tables:")
    if tables_result['success']:
        for row in tables_result['result']['rows']:
            print(f"- {row[0]}")
    
    # Debug: Check if we have any skills data
    skills_check = mysql_query("""
        SELECT os.*, s.element_name 
        FROM Occupation_Skills os
        JOIN Skills s ON s.element_id = os.element_id
        WHERE os.onet_soc_code = '19-2031.00' AND os.scale_id = 'LV'
        LIMIT 5;
    """)
    print("\nSkills Data Check:")
    if skills_check['success']:
        print(f"Columns: {skills_check['result']['columns']}")
        print("First 5 skills:")
        for row in skills_check['result']['rows']:
            print(row)
    
    # Test for Environmental Scientists (19-2031.00)
    occupation_code = "19-2031.00"
    
    # Execute test operation
    result = get_occupation_skills(occupation_code)
    
    # Print results for verification
    print("\nIntegration Test Results:")
    print(f"Occupation Code: {occupation_code}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Occupation Title: {result['result'].get('occupation_title', 'N/A')}")
        print(f"Number of skills found: {len(result['result'].get('skills', []))}")
        print("\nTop 5 skills:")
        for skill in result['result'].get('skills', [])[:5]:
            print(f"- {skill['element_name']} (Score: {skill['data_value']})")
    
    # Assertions to verify the results
    assert result["success"] == True, f"Operation failed: {result['message']}"
    assert result["result"]["occupation_title"] is not None, "Expected occupation title to be present"
    assert len(result["result"]["skills"]) > 0, "Expected non-empty skills list"
    
    # Verify data structure of returned skills
    if result["success"] and result["result"]["skills"]:
        skill = result["result"]["skills"][0]
        assert "element_id" in skill, "Expected element_id in skill data"
        assert "element_name" in skill, "Expected element_name in skill data"
        assert "data_value" in skill, "Expected data_value in skill data" 