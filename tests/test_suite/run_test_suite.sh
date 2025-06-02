# Not Working, some reason using pytest causes the tests to fail.
#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Apply environment variables
source env/env.env

# Run all the specified integration tests
# The -s flag shows print statements, -v provides verbose output.
echo "Running integration test suite..."
echo " Using pytest causes some of the tests to fail so this is a work in progress."
echo " Please use the run_tests_suite_using_sh.sh instead."

# python -m pytest \
#     tests/test_integration_mysql_create_db.py \
#     tests/test_integration_mysql_init_tables.py \
#     tests/test_integration_mysql_connection.py \
#     tests/test_integration_mysql_load.py \
#     tests/test_integration_transform.py \
#     tests/test_integration_api_extract_load_skills.py \
#     tests/test_integration_api_extract_load_occupations.py \
#     tests/test_integration_get_occupation_and_skills_api_fallback.py \
#     tests/test_integration_get_occupation_skills.py \
#     tests/test_integration_get_skills_gap.py \
#     tests/test_integration_get_skills_gap_by_lvl.py \
#     -v -s

# # Deactivate virtual environment if it was activated
# if [ -n "$VIRTUAL_ENV" ]; then
#     deactivate
# fi

# echo "Integration test suite completed."
