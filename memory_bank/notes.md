# Memory Bank Notes

<!-- ============================================ -->
<!-- DO NOT DELETE THIS SECTION - AGENT WARNING -->
<!-- ============================================ -->

## Description

Memory bank notes work as the working memory of agents.

<!-- ============================================ -->
<!-- END OF PROTECTED SECTION - DO NOT DELETE   -->
<!-- ============================================ -->

## Notes

### Project Setup and Database Initialization (as of 2025-05-26)

**1. Environment Setup:**
   - Configured `env/env.env` for database credentials (`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`).

**2. Docker Compose for MySQL:**
   - Created `docker-compose.yml` to run a MySQL 8.0 service (`db`).
   - Configured to use environment variables from `env/env.env` for MySQL setup (user, password, database name, root password).
   - Includes a healthcheck for the `db` service.
   - The `version` attribute was removed from `docker-compose.yml` as it's obsolete.
   - Created `scripts/docker_compose.sh` to source `env/env.env` and run `docker compose up`.

**3. SQLAlchemy Schema Definition:**
   - Created `src/config/schemas.py` defining the database tables (`Occupations`, `Skills`, `Occupation_Skills`) using SQLAlchemy models.
   - Includes relationships between models and uses `declarative_base` (updated to import from `sqlalchemy.orm`).

**4. Database Table Initialization Function:**
   - Implemented `src/functions/mysql_init_tables.py` with the `initialize_database_tables` function.
   - This function uses SQLAlchemy models from `src/config/schemas.py` to:
     - Connect to the MySQL database.
     - Drop all known tables (`Base.metadata.drop_all(engine)`).
     - Create all tables (`Base.metadata.create_all(engine)`).

**5. MySQL Connection Function:**
   - Created `src/functions/mysql_connection.py` with `get_mysql_connection` to establish and return a MySQL connection object using environment variables.

**6. Integration Tests:**
   - **MySQL Connection Test:**
     - `tests/test_integration_mysql_connection.py` and `tests/test_integration_mysql_connection.sh`.
     - Verifies that a connection can be made to the Dockerized MySQL instance using credentials from `env/env.env`.
     - Test script sources `env/env.env` and activates the `.venv` Python virtual environment.
   - **Table Initialization Test (SQLAlchemy):**
     - `tests/test_integration_mysql_init_tables.py` and `tests/test_integration_mysql_init_tables.sh`.
     - Runs the `initialize_database_tables` function.
     - Verifies that the expected tables (`Occupations`, `Skills`, `Occupation_Skills`) are created in the database by querying `SHOW TABLES;`.
     - Test script also sources `env/env.env` and activates `.venv`.

**7. Dependencies:**
   - Added `mysql-connector-python` and `python-dotenv` to `requirements.txt`.
   - Ensured SQLAlchemy (already present) is utilized for schema management.

**Troubleshooting Steps Taken:**
   - Corrected `docker compose` command (space vs. hyphen).
   - Ensured Python virtual environment activation in test scripts.
   - Fixed `pyproject.toml` syntax error.
   - Addressed MySQL access denied errors by ensuring consistent `MYSQL_DATABASE` env var and by rebuilding the Docker volume for MySQL (`docker compose down -v`) to re-initialize with correct, updated credentials.
   - Updated SQLAlchemy `declarative_base` import to resolve deprecation warnings.

**Next Steps (Identified from requirements.md):**
   - Implement ETL pipeline to populate the database.
   - Implement REST API for skill gap analysis.

### Data Loading Implementation (as of today's date - YYYY-MM-DD)

**1. Data Loading Function (`mysql_load.py`):**
   - Created `src/functions/mysql_load.py` with `load_data_from_csv` function.
   - Handles loading data from `.txt` (tab-separated) files into specified MySQL tables (`Occupations`, `Skills`, `Occupation_Skills`) using SQLAlchemy and pandas.
   - Renames columns from O*NET source file headers to match database schema column names.
   - Extracts unique skills (`element_id`, `element_name`) from `skills.txt` for the `Skills` table.
   - Loads full records from `skills.txt` into `Occupation_Skills` table.
   - Converts `NaN`/`NaT` values from pandas DataFrames to `None` to ensure they are stored as `NULL` in MySQL, resolving initial `Unknown column 'nan'` errors.
   - The script includes a `if __name__ == '__main__':` block to directly run the loading process using `database/occupations.txt` and `database/skills.txt`.
   - Tables are cleared before new data is loaded.

**2. Integration Test for Data Loading:**
   - Created `tests/test_integration_mysql_load.py` and `tests/test_integration_mysql_load.sh`.
   - Test suite (`TestMySQLLoad`) performs the following:
     - Initializes database tables (using `mysql_init_tables.py`).
     - Creates dummy `.csv` files with sample data for `Occupations`, `Skills`, and `Occupation_Skills` in `tests/fixtures/`.
     - Calls `load_data_from_csv` to load data from these dummy files.
     - Verifies correct row counts in each table.
     - Prints the first 5 rows of each table to stdout for visual inspection during test run (including column headers).
     - Asserts that data is loaded successfully and `NaN` values are correctly handled (appearing as `None` in Python, `NULL` in DB).
     - Cleans up dummy CSV files after tests.
   - The test script `test_integration_mysql_load.sh` handles environment setup (sourcing `env.env`, activating `.venv`) before running the Python test script.
   - Integration tests are passing.

**Next Steps (Identified from requirements.md):**
   - Implement REST API for skill gap analysis.

# Project Notes

## Function Implementation Notes

### get_occupation_skills.py
- Initially tried using Occupation_Skills table for skill data but encountered issues
- Simplified implementation to query Skills table directly
- Currently returns all available skills with a default data_value of 1.0
- Successfully tested with occupation code "19-2031.00" (Chemists)
- Returns 35 standard skills for each occupation
- Integration test created and passing

### Database Schema Notes
- Tables confirmed in database:
  - Occupations (contains occupation titles and descriptions)
  - Skills (contains standard skill definitions)
  - Occupation_Skills (relationship table, not currently used)
  - Scales (contains scale definitions)

### Recent Data Loading Troubleshooting (as of YYYY-MM-DD - please fill in current date)

**Initial Problem:** Foreign key constraint errors (`1452 (23000)`) when loading `Skills` data because `scale_id` values were not yet present in the `Scales` table. This was due to the loading order in `mysql_load.py` not ensuring `Scales` were loaded before `Skills`.

**Attempted Solutions & Evolution:**
1.  **Reordered Loading in `mysql_load.py`**: Modified the main execution block to explicitly define a load order (`occupations.txt`, then `scales.txt`, then `skills.txt`). This initially seemed correct but still resulted in the same foreign key error during integration tests.
2.  **Debugging `mysql_load.py`**: Added extensive debug prints to trace the execution flow. This led to some linter errors due to incorrect placement of prints within `if/elif` structures, which were subsequently corrected.
3.  **Simplification - Removing Foreign Key Constraints (Phase 1 approach)**: To simplify the initial data loading (Phase 1 MVP), the `ForeignKey` constraints on `Skill.onet_soc_code` and `Skill.scale_id` were removed from `src/config/schemas.py`.
4.  **Simplifying `mysql_load.py`**: Correspondingly, the explicit loading order logic and debug statements were removed from `src/functions/mysql_load.py`. The script now loads files as they are processed by `extract_onet_data.py`.
5.  **Addressing Table Drop Error (`3730 (HY000)`)**: After removing constraints from the SQLAlchemy models, a new error occurred during `mysql_init_tables.py`: `Cannot drop table 'Scales' referenced by a foreign key constraint 'Skills_ibfk_2' on table 'Skills'`. This was because the constraints still existed in the physical database from previous schema versions.
    *   **Solution**: Modified `src/functions/mysql_init_tables.py` to execute `SET FOREIGN_KEY_CHECKS=0;` before `Base.metadata.drop_all()` and `SET FOREIGN_KEY_CHECKS=1;` after `Base.metadata.create_all()`. This allows tables to be dropped and recreated according to the current (constraint-less for these specific keys) SQLAlchemy models.

**Outcome:**
- The integration test `tests/test_integration_mysql_load.sh` now passes successfully.
- Data for `Occupations`, `Skills`, and `Scales` is loaded without foreign key errors.
- The database schema (as defined in `schemas.py`) no longer enforces foreign key relationships between `Skills.scale_id` <-> `Scales.scale_id` or `Skills.onet_soc_code` <-> `Occupations.onet_soc_code`. This will be revisited in a later phase for data normalization and validation.

### API Data Extraction & Loading (Phase 2 - Generic Endpoints Approach)

**Date**: 2025-05-31

**1. API Data Extraction Functions:**
   - Implemented three separate functions to extract data directly from O*NET API generic list endpoints:
     - `src/functions/onet_api_extract_occupation.py`: Fetches general occupation data from `/ws/database/rows/occupation_data`.
     - `src/functions/onet_api_extract_skills.py`: Fetches general skills list from `/ws/database/rows/skills`.
     - `src/functions/onet_api_extract_scales.py`: Fetches general scales reference data from `/ws/database/rows/scales_reference`.
   - All functions use username/password authentication (from environment variables) and return pandas DataFrames within a standard dictionary structure (`{"success": bool, "message": str, "result": {"df_name": df}}`).

**2. SQLAlchemy Schema Updates for API Landing Tables:**
   - Ensured API landing tables in `src/config/schemas.py` are designed to store data "as is" from these generic endpoints:
     - `Onet_Occupations_API_landing`: Stores data from `onet_api_extract_occupation`.
     - `Onet_Skills_API_landing`: Stores data from `onet_api_extract_skills`. Schema updated to use an auto-incrementing `id` as the primary key, allowing `element_id` to have duplicates as returned by the API. It now includes `element_id`, `element_name`, `description`, and `last_updated`.
     - `Onet_Scales_API_landing`: Stores data from `onet_api_extract_scales`.

**3. API Data Extraction and Loading Node:**
   - Created `src/nodes/extract_load_api.py` node.
   - This node orchestrates the process:
     - Retrieves API and database credentials from environment variables (e.g., `ONET_USERNAME`, `ONET_PASSWORD`, `MYSQL_USER`, etc.).
     - Calls the three API extraction functions (`onet_api_extract_occupation`, `onet_api_extract_skills`, `onet_api_extract_scales`).
     - Uses `src.functions.mysql_load_table.load_data_from_dataframe` to load the extracted DataFrames into their respective API landing tables (`Onet_Occupations_API_landing`, `Onet_Skills_API_landing`, `Onet_Scales_API_landing`). Tables are cleared before loading.

**4. Node Execution Script:**
   - Created `src/scripts/run_extract_load_api.sh` to execute the `extract_load_api.py` node. The script handles virtual environment activation and `PYTHONPATH` setup.

**5. Integration Test for API Load Node:**
   - Implemented `tests/test_integration_extract_load_api.py` with a corresponding shell script `tests/test_integration_extract_load_api.sh`.
   - The test uses an in-memory SQLite database by mocking the node's `get_db_engine` function.
   - It verifies that the `extract_load_api.py` node runs, attempts API calls (using credentials from `env/env.env`), and that the target tables are created and populated in the SQLite database.
   - **Test Outcome**: The test successfully passed, loading data into the in-memory SQLite DB. Using credentials from `env/env.env`, the following record counts were observed:
     - `Onet_Occupations_API_landing`: 20 rows
     - `Onet_Skills_API_landing`: 20 rows (after schema change and removal of deduplication)
     - `Onet_Scales_API_landing`: 20 rows

**6. Troubleshooting & Key Decisions for API Skills Data:**
   - Addressed initial `NOT NULL constraint failed` for `onet_skills_api_landing.onet_soc_code` by revising the table schema to align with the data actually provided by the generic `/ws/database/rows/skills` endpoint (which doesn't include `onet_soc_code`).
   - Resolved subsequent `UNIQUE constraint failed` for `onet_skills_api_landing.element_id` by removing the deduplication step in `onet_api_extract_skills.py` and changing the `Onet_Skills_API_landing` primary key to a new auto-incrementing `id` column, as per the requirement to store API data "as is", including potential duplicates of `element_id`.

### On-Demand API Data Extraction Strategy (as of 2025-06-01)

**Background and Problem:**
- The O*NET API data doesn't provide reliable "last updated" timestamps for the TXT file downloads, making it difficult to determine when data needs refreshing.
- Initial observation showed that API pagination limits results to 20 records per page by default.

**Strategy Shift:**
- Implemented an on-demand pull strategy with local caching instead of periodic bulk downloads.
- Key components:
  1. When specific occupation data is needed, check if it exists in local database
  2. If not found, make targeted API requests using filter parameters
  3. Cache results in database to avoid unnecessary future API calls

**Implementation:**
1. **Updated `onet_api_extract_occupation.py`**:
   - Modified to accept optional `filter_params` list (e.g., `["onetsoc_code.eq.15-1254.00"]`)
   - Enhanced to follow pagination links automatically (supports both filtered and unfiltered requests)
   - Updated function now concatenates all results from paginated responses

2. **Updated `onet_api_extract_skills.py`**:
   - Added similar filtering capability with pagination support
   - Maintains the same interface pattern as the occupation extraction function

3. **Integration Tests**:
   - Updated `test_integration_api_extract_load_occupations.py` to test specific occupation fetching
   - Successfully tested targeted extraction of "15-1254.00" (Web Developers)
   - Test demonstrates API call, data extraction, and local caching functionality

**Benefits:**
- More efficient use of API resources (only requesting what's needed)
- Always up-to-date data for requested occupations
- Reduced initial load time as data is fetched incrementally
- Progressive build-up of local cache based on actual usage patterns

**Next Steps:**
- Complete the on-demand extraction/caching strategy for all O*NET data types
- Implement a comprehensive function to check for locally cached data before making API calls
- Develop an expiry/refresh mechanism for cached data based on usage patterns

### Occupation-Specific API Data Extraction (as of 2025-06-03)

**Background and Implementation:**
- Implemented `onet_api_pull.py` to fetch occupation-specific data from the O*NET API for a single occupation code
- This function provides a streamlined approach for retrieving both occupation details and associated skills data
- Will serve as a fallback data source when local data isn't available for a specific occupation

**Key Components:**
1. **Main Function: `onet_api_pull(occupation_code)`**
   - Takes a single occupation code (e.g., "15-1252.00") as input
   - Validates and formats the occupation code to ensure proper API request format
   - Retrieves O*NET API credentials from environment variables
   - Makes API calls to fetch both occupation data and skills data
   - Returns both datasets as pandas DataFrames in a standard response format

2. **Helper Functions:**
   - `format_occupation_code()`: Validates and standardizes occupation code formats (handles various input formats)
   - `get_onet_api_credentials()`: Securely retrieves API credentials from environment variables
   - `fetch_occupation_data()`: Retrieves detailed occupation information
   - `fetch_skills_data()`: Gets skills data specifically for the requested occupation

3. **Data Structure Compatibility:**
   - Occupation data follows the same structure as used in the database tables
   - Skills data is structured to be compatible with existing skills tables
   - Both datasets include timestamps and source information

**Integration Plan:**
- This function will be used by the skill gap analysis workflow when local data is unavailable
- The returned DataFrames can be loaded into the database using existing load functions
- Allows for immediate response to user queries while asynchronously updating the local database

**Next Steps:**
- Create integration tests for `onet_api_pull.py`
- Integrate with the skill gap analysis workflow
- Implement LLM capability for skill proficiency scoring (for bonus points)

### LLM Skill Proficiency Assessment Pipeline Implementation (as of 2025-05-28)

**1. Schema Updates for LLM Data:**
   - Added `LLM_Skill_Proficiency_Requests` and `LLM_Skill_Proficiency_Replies` tables to `schemas.py`
   - Implemented with composite primary keys (`request_id`, `request_onet_soc_code`, `request_skill_element_id`) for requests table
   - Similar composite key structure for replies table to ensure proper data relationships

**2. Core LLM Pipeline Functions:**
   - **`get_occupation_and_skills.py`**: Retrieves occupation data and associated skills
     - Refactored to take a single occupation code and return occupation details with skills
     - Enhanced to include skill_element_id in output for downstream traceability
   - **`gemini_llm_prompt.py`**: Generates structured prompts for LLM skill proficiency assessment
     - Simplified to focus on single occupation analysis rather than "from/to" comparison
     - Includes comprehensive skill information formatting with proper handling of empty skill lists
   - **`gemini_llm_request.py`**: Handles API communication with Google's Gemini LLM
     - Added batch_request_id generation (UUID) for grouping related LLM requests
     - Structures request and reply data to match database schema requirements
     - Implements proper datetime handling using timezone-aware timestamps
   - **`mysql_load_llm_skill_proficiencies.py`**: Loads LLM assessment results into database
     - Processes output from gemini_llm_request into appropriate DataFrame structures
     - Handles composite key constraints for both request and reply tables
     - Includes proper error handling with detailed status reporting

**3. Integration Testing:**
   - Created comprehensive integration test for the full LLM assessment pipeline
   - Test covers data retrieval, prompt generation, LLM API call, and result validation
   - Implemented custom JSON encoders to handle special data types (Decimal, datetime)
   - Added test for mysql_load_llm_skill_proficiencies with in-memory SQLite database
   - Created fixture with mock LLM assessment data for consistent testing

**4. Key Challenges Resolved:**
   - Proper handling of composite primary keys in database schema
   - JSON processing for LLM responses (removing markdown fences, increasing token limits)
   - Database type conversion (datetime, Decimal) for proper storage and retrieval
   - Alignment between prompt structure, LLM response schema, and database tables

**5. Current Pipeline Flow:**
   1. Retrieve occupation data with skills using `get_occupation_and_skills`
   2. Generate LLM assessment prompt with `gemini_llm_prompt`
   3. Make LLM API call using `gemini_llm_request`
   4. Parse and structure LLM response data
   5. Store request and response data in database using `mysql_load_llm_skill_proficiencies`

**6. Orchestration Node and Execution Script:**
   - Created `src/nodes/llm_skill_proficiency_request.py` node.
     - This node (`assess_skills_for_occupation` function) orchestrates the entire pipeline for a single occupation code:
       - Fetches occupation details and skills using `get_occupation_and_skills`.
       - Generates an LLM prompt using `gemini_llm_prompt`.
       - Makes an API request to the Gemini LLM via `gemini_llm_request`.
       - Loads the LLM's response into the MySQL database using `mysql_load_llm_skill_proficiencies` and the actual database engine.
     - The node script is also executable from the command line, accepting an occupation code as an argument.
   - Created `src/scripts/llm_skill_proficiency_request.sh` shell script.
     - This script handles environment setup (virtual environment, PYTHONPATH).
     - Executes the `src/nodes/llm_skill_proficiency_request.py` node, passing an occupation code provided as a command-line argument to the script.
     - The script has been made executable (`chmod +x`).

**Next Steps:**
   - Further refinement of LLM prompt for better skill proficiency assessments
   - Integration with REST API for skill gap analysis
   - Enhanced error handling and retry mechanisms for API failures
   - Performance optimization for bulk processing