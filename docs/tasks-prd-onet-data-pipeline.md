## Relevant Files

- `src/config/schemas.py` - Defines SQLAlchemy models for database tables (`Occupations`, `Skills`, `Scales`, `OnetApiOccupationData`, `OnetApiSkillsData`).
- `src/functions/mysql_init_tables.py` - Initializes database tables using SQLAlchemy models.
- `tests/test_integration_mysql_init_tables.py` - Integration tests for `mysql_init_tables.py`.
- `src/functions/extract_onet_data.py` - Extracts data from O*NET `.txt` files into pandas DataFrames.
- `tests/test_integration_extract_onet_data.py` - Integration tests for `extract_onet_data.py`.
- `src/functions/mysql_load_dataframe.py` - Loads a single pandas DataFrame into a specified MySQL table.
- `tests/test_integration_mysql_load_dataframe.py` - Integration tests for `mysql_load_dataframe.py`.
- `src/functions/textfile_to_dataframe.py` - **NEW:** Utility function to convert text files to DataFrames with proper typing.
- `src/functions/onet_api_extract_occupation.py` - **UPDATED:** Fetches O*NET-SOC occupation codes, titles, and descriptions from the API with optional filtering.
- `tests/test_integration_onet_api_extract_occupation.py` - **UPDATED:** Integration tests for `onet_api_extract_occupation.py` including filter tests.
- `src/functions/extract_onet_api_occupation_details.py` - **NEW:** Fetches detailed occupation data (description) for a list of occupation codes from the API.
- `tests/test_integration_extract_onet_api_occupation_details.py` - **NEW:** Integration tests for `extract_onet_api_occupation_details.py`.
- `src/functions/extract_onet_api_skills_data.py` - **NEW:** Parses skills data from detailed occupation API responses.
- `tests/test_integration_extract_onet_api_skills_data.py` - **NEW:** Integration tests for `extract_onet_api_skills_data.py`.
- `src/functions/get_onet_scales_reference.py` - **NEW:** Retrieves O*NET Scales Reference data (direct download or embedded).
- `tests/test_integration_get_onet_scales_reference.py` - **NEW:** Integration tests for `get_onet_scales_reference.py`.
- `src/functions/mysql_upsert_dataframe.py` - **NEW:** Upserts a pandas DataFrame into a specified MySQL table.
- `tests/test_integration_mysql_upsert_dataframe.py` - **NEW:** Integration tests for `mysql_upsert_dataframe.py`.
- `src/functions/populate_skills_reference.py` - **NEW:** Populates the Skills table from raw data tables.
- `src/functions/populate_occupation_skills.py` - **NEW:** Populates the Occupation_Skills table from raw data tables.
- `src/functions/get_occupation_and_skills.py` - **NEW:** Retrieves structured occupation data with associated skills for a specific occupation code.
- `src/functions/gemini_llm_prompt.py` - **NEW:** Generates LLM prompts for skill proficiency assessment.
- `src/functions/gemini_llm_request.py` - **NEW:** Handles API communication with Google's Gemini LLM.
- `src/functions/mysql_load_llm_skill_proficiencies.py` - **NEW:** Loads LLM assessment results into database tables.
- `tests/test_integration_llm_skill_assessment_pipeline.py` - **NEW:** Integration test for the LLM skill proficiency assessment pipeline.
- `tests/test_integration_load_llm_proficiencies.py` - **NEW:** Integration test for mysql_load_llm_skill_proficiencies.
- `tests/fixtures/fixture_llm_assessment_output.py` - **NEW:** Fixture with mock LLM assessment data for testing.
- `src/functions/llm_skill_profiler.py` - To house the LLM interaction logic for skill proficiency scoring.
- `tests/test_integration_llm_skill_profiler.py` - Integration tests for `llm_skill_profiler.py`.
- `src/nodes/extract_load.py` - Orchestrates text file data extraction and loading.
- `src/nodes/transform.py` - **NEW:** Orchestrates data transformation between raw and downstream tables.
- `src/scripts/transform.sh` - **NEW:** Shell script to run the transform node.
- `tests/test_integration_extract_load_text_files.py` - Integration tests for `extract_load_text_files.py`.
- `src/nodes/extract_load_api_data.py` - **NEW:** Orchestrates O*NET API data extraction and loading.
- `tests/test_integration_extract_load_api_data.py` - **NEW:** Integration tests for `extract_load_api_data.py`.
- `src/nodes/enrich_skill_data.py` - Orchestrates LLM enrichment of skill proficiency data.
- `tests/test_integration_enrich_skill_data.py` - Integration tests for `enrich_skill_data.py`.
- `src/functions/get_occupation_skills.py` - Retrieves occupation skills data for API.
- `tests/test_integration_get_occupation_skills.py` - Integration tests for `get_occupation_skills.py`.
- `src/functions/identify_skill_gap.py` - Contains the core logic for comparing two occupations' skills.
- `tests/test_integration_identify_skill_gap.py` - Integration tests for `identify_skill_gap.py`.
- `src/functions/onet_api_pull.py` - **NEW:** Fetches occupation and skills data from O*NET API for a specific occupation code.
- `tests/test_integration_onet_api_pull.py` - **NEW:** Integration tests for `onet_api_pull.py`.
- `src/api/main.py` - Main FastAPI/Flask application file for the REST API.
- `src/api/routers/skill_gap.py` - API router/controller for the `/skill-gap` endpoint.
- `tests/test_api_skill_gap.py` - Integration tests for the `/skill-gap` API endpoint.
- `docker-compose.yml` - Defines and configures services (MySQL, ETL, API).
- `Dockerfile.api` - Dockerfile for the API service.
- `Dockerfile.etl` - Dockerfile for the ETL service.
- `requirements.txt` - Python project dependencies.
- `env/env.env` - Environment variable configuration.
- `README.md` - Project documentation.
- `src/nodes/llm_skill_proficiency_request.py` - **NEW:** Node to orchestrate LLM skill proficiency assessment for an occupation.
- `src/scripts/llm_skill_proficiency_request.sh` - **NEW:** Shell script to execute the llm_skill_proficiency_request node.
- `tests/test_integration_get_occupation_and_skills_with_api_fallback.py` - **NEW:** Integration test for `get_occupation_and_skills` with API fallback.
- `tests/test_integration_get_occupation_and_skills_with_api_fallback.sh` - **NEW:** Shell script to run the `get_occupation_and_skills` API fallback integration test.

### Notes

- Unit tests (if any) are typically alongside the code or in `tests/unit/`.
- Integration tests are in `tests/test_integration_<module_name>.py` and run via their `.sh` scripts.
- Use `python -m pytest` for running tests.

## Tasks

- [x] 1.0 **Phase 1: Setup & Text File ETL Foundational Components**
  - [x] 1.1 Define environment variables for DB connection (`env/env.env`).
  - [x] 1.2 Define SQLAlchemy schemas in `src/config/schemas.py` for `Occupations`, `Skills`, `Scales` tables (from text files).
  - [x] 1.3 Create function `mysql_init_tables(engine, tables_to_create: list)` in `src/functions/mysql_init_tables.py`. Inputs: SQLAlchemy engine, list of table model classes. Outputs: `{"success": bool, "message": str}`. Initializes specified tables.
  - [x] 1.4 Create integration test for `mysql_init_tables` (`tests/test_integration_mysql_init_tables.py` and `.sh` script).
  - [x] 1.5 Create function `extract_onet_data(file_mapping: dict)` in `src/functions/extract_onet_data.py`. Inputs: dict mapping file key (e.g., 'occupations') to file path. Outputs: `{"success": bool, "message": str, "result": {"occupations_df": pd.DataFrame, ...}}`. Reads O*NET `.txt` files into DataFrames.
  - [x] 1.6 Create integration test for `extract_onet_data` (`tests/test_integration_extract_onet_data.py` and `.sh` script).
  - [x] 1.7 Create function `mysql_load_dataframe(df: pd.DataFrame, table_name: str, engine, if_exists: str = 'replace')` in `src/functions/mysql_load_dataframe.py`. Inputs: DataFrame, table name, SQLAlchemy engine, if_exists strategy. Outputs: `{"success": bool, "message": str}`. Loads DataFrame to MySQL.
  - [x] 1.8 Create integration test for `mysql_load_dataframe` (`tests/test_integration_mysql_load_dataframe.py` and `.sh` script) using `Occupations` table as an example.
  - [x] 1.9 Create node `extract_load_text_files.py` in `src/nodes/`. This node will use `mysql_init_tables`, `extract_onet_data`, and `mysql_load_dataframe` to initialize tables and load all three text files (`Occupations`, `Skills`, `Scales`).
  - [x] 1.10 Create integration test for `extract_load_text_files` node (`tests/test_integration_extract_load_text_files.py` and `.sh` script).
  - [x] 1.11 Review and Refine Phase 1 functions and node for clarity, efficiency, docstrings, and adherence to rules.
  - [x] 1.12 Update `README.md` with setup/run instructions for Phase 1 text file ETL.
  - [x] 1.13 **NEW:** Create utility function `textfile_to_dataframe()` to simplify file processing.
  - [x] 1.14 **NEW:** Refactor `extract_onet_data.py` to use specialized extraction functions and the new utility.

- [x] 2.0 **Phase 2: Data Ingestion - O*NET API Integration Functions (Supporting Bulk and On-Demand/Filtered Fetching)**
  - [x] 2.1 **MODIFIED (On-Demand):** Update function `onet_api_extract_occupation(username: str, password: str, filter_params: Optional[list] = None, ...)` in `src/functions/onet_api_extract_occupation.py`.
    - Inputs: API creds, optional list of filter strings (e.g., `["onetsoc_code.eq.CODE"]`).
    - Logic: If `filter_params` are provided, include them in the API request. Continues to support pagination for all results (filtered or unfiltered).
    - Outputs: `{"success": bool, "message": str, "result": {"occupation_df": pd.DataFrame}}`.
    - **IMPLEMENTATION NOTE:** Successfully updated to handle pagination and concatenate results from all pages.
  - [x] 2.1.1 **NEW (On-Demand):** Create integration test specifically for filtered `onet_api_extract_occupation` to verify it correctly fetches single or specific records based on filters (e.g., by `onetsoc_code`).
    - **IMPLEMENTATION NOTE:** Successfully tested with `["onetsoc_code.eq.15-1254.00"]` filter to fetch Web Developers occupation.
  - [x] 2.2 Create/Update integration test for bulk `onet_api_extract_occupation` (and its loading) (`tests/test_integration_api_extract_load_occupations.py` and `.sh`).
  - [x] 2.4 **NEW (On-Demand):** Design and implement similar `filter_params` and specific filter tests for `onet_api_extract_skills` and `onet_api_extract_scales` functions.
    - [x] 2.4.1 Update `onet_api_extract_skills` to accept `filter_params` and add integration test for filtered skill extraction.
      - **IMPLEMENTATION NOTE:** Updated function to accept filters and handle pagination similarly to the occupation extraction.
      - **IMPLEMENTATION NOTE:** Scales are static reference data that doesn't need occupation-specific filtering.
  - [x] 2.5 Create function `onet_api_extract_skills_data(occupation_details_df: pd.DataFrame)` in `src/functions/onet_api_extract_skills_data.py`. (This function parses XML details; may need adjustment if detailed occupation data is fetched differently in on-demand flow).
  - [x] 2.7 Create function `get_onet_scales_reference(url: str)` in `src/functions/get_onet_scales_reference.py`.
  - [x] 2.11 Define SQLAlchemy schemas for the API data landing tables in `src/config/schemas.py`.
  - [x] 2.13 Create node `extract_load_api.py` in `src/nodes/`. This node is for *bulk* API data extraction using the updated functions (without filters or with broad filters if ever needed for bulk).
  - [x] 2.14 Create integration test for `extract_load_api.py` node.
  - [x] 2.15 **NEW (On-Demand):** Document the on-demand pull strategy with caching in `memory_bank/notes.md`.
    - **IMPLEMENTATION NOTE:** Added detailed notes on the strategy shift to on-demand pulling with local caching.
  - [x] 2.16 **NEW:** Create `onet_api_pull.py` function to fetch occupation and skills data for a specific occupation code.
    - **IMPLEMENTATION NOTE:** Function successfully implemented with proper error handling, data formatting, and compatibility with existing database schema.

- [x] 3.0 **Phase 3: Database Normalization & Downstream Consumption Tables**
  - [x] 3.1 Analyze data from both sources (text files and API) to understand their structure and relationships.
  - [x] 3.2 Design and implement simplified downstream tables from existing raw data tables.
    - [x] 3.2.1 Reuse existing `Occupations` table instead of creating a new normalized table.
    - [x] 3.2.2 Create `Skills` table to store unique skills information.
    - [x] 3.2.3 Create `Occupation_Skills` table as a joining table between occupations and skills.
  - [x] 3.3 Create data transformation functions to populate downstream tables from raw data tables.
    - [x] 3.3.1 Create `populate_skills_reference()` function to populate Skills table from raw data.
    - [x] 3.3.2 Create `populate_occupation_skills()` function to populate Occupation_Skills table from raw data.
    - [x] 3.3.3 Create `transform.py` node to chain these functions together.
    - [x] 3.3.4 Create shell script `transform.sh` to run the transform node.
  - [x] 3.4 Update `schemas.py` to ensure all table definitions match the actual database structure.
  - [x] 3.5 Create `get_occupation` function to retrieve occupation data from downstream tables.
  - [x] 3.6 Refactor `get_occupation_skills` function to pull data from downstream tables.
  - [x] 3.7 Create integration tests for downstream tables and updated functions.
    - [x] 3.7.1 Create integration test for `populate_skills_reference()`.
    - [x] 3.7.2 Create integration test for `populate_occupation_skills()`.
    - [x] 3.7.3 Update integration test for `get_occupation()` and `get_occupation_skills()`.
  - [x] 3.8 Document simplified data model showing flow from raw to downstream tables.

- [x] 4.0 **Phase 4: LLM Integration for Skill Proficiency (Bonus Points)**
  - [x] 4.1 Create function gemini_llm_request, it should take a prompt and return the llm response.
  - [x] 4.2 Create function generate_llm_skill_proficiency_prompt for generating the prompt for the llm.         
        
    ```python
    parameters:
    occupation_data={onet_id:..., name:..., skills:[{skill_element_id, skill_name:..., proficiency_level:...}], }

    returns: """
      1.  Analyze the skills of the `to_occupation` object provided in the input.
      2.  For each skill listed in `to_occupation.skills`, determine a proficiency level.
          The proficiency level should be categorized (e.g., Novice, Beginner, Intermediate,
          Advanced, Expert) and optionally assigned a numerical score on a defined scale
          (e.g., 1-5, the prompt can specify this scale).
      3.  Provide a detailed justification/explanation for each assigned proficiency level. This explanation should be in the context of the `to_occupation`'s typical
          duties and responsibilities.
      4.  If a `from_occupation` object is provided, the LLM should consider its skills and
          proficiencies as context. This might involve commenting on skill transferability,
          gaps, or how experience in the `from_occupation` might influence the learning
          curve or proficiency in the `to_occupation`'s skills.
      5.  Structure its entire response as a single, valid JSON object. The required schema
          for this JSON object is as follows:
          ```json
          {
            "skill_proficiency_assessment": {
              "llm_onet_soc_code": "string (O*NET code of the occupation being assessed, i.e., to_occupation)",
              "llm_occupation_name": "string (Name of the occupation being assessed)",
              "assessed_skills": [
                {
                  "llm_skill_name": "string (Name of the skill, from to_occupation.skills.skill_name)",
                  "llm_assigned_proficiency_description": "string (e.g., 'Intermediate', 'Advanced', 'Expert')",
                  "llm_assigned_proficiency_level": "number | null (e.g., 3.5 on a 1-7 scale)",
                  "llm_explanation": "string (LLM's detailed reasoning for the assigned proficiency, considering the occupation's demands. If from_occupation was provided, this may include comparative notes.)"
                }
                // ... This array will contain one object for each skill in to_occupation.skills
              ]
            },
          }
          ```
    """
    ```
    - [x] 4.3 Create function get_occupation_and_skills for getting and structuring the data that needs to be passed to 4.2 (generating the prompt for the llm).    
    - [x] 4.4 Update the @Schema @mysql_init_tables and @mysql_load_tables to initialize tables in the database to store the LLM responses.
    - [x] 4.5 Create function mysql_load_llm_skill_proficiencies to load LLM assessment results into the database.
      - **IMPLEMENTATION NOTE:** This should store the full LLM response JSON in the `LlmSkillAssessments` table while extracting the specific proficiency levels (from `llm_assigned_proficiency_level` field) to update the corresponding records in the `Occupation_Skills` table for the 'LV' scale.
    - [x] 4.6 Create integration tests for the LLM skill proficiency assessment pipeline.
    - [x] 4.7 Align documentation with the implemented LLM response schema.
    - [x] 4.8 Create node `llm_skill_proficiency_request.py` to orchestrate the pipeline for a single occupation.
    - [x] 4.9 Create shell script `llm_skill_proficiency_request.sh` to execute the node.

- [x] 5.0 **Phase 5: REST API for Skill Gap Analysis (Incorporating On-Demand API Fetching & Caching)**
  - [x] 5.1 Check and Update if needed that function `get_occupation` returns a fail status if it cant find the `onet_soc_code`.
  - [x] 5.2 Check and Update if needed that function `get_occupation_skills` returns a empty list if it cant find any skills for the `onet_soc_code`.
  - [x] 5.3 Update the `get_occupation_and_skills` to leverage the  onet_api_extract_occupation and onet_api_extract_skills functions if either get_occupation fails to find a onet_soc_code or if get_occupation_skills returns an empty list. 
    - **IMPLEMENTATION NOTE:** This implements the on-demand API fetching with caching strategy discussed in the PRD. The system first looks for data in local tables; if not found, it fetches from the API, uses it for the immediate request, and also stores it for future use.
  - [x] 5.4 Create an integration test that tests 5.1-5.3. We should only need to execute get_occupation_and_skills for onet_soc_code='11-2021.00'. Assume the below sql has been executed for the purposes of this test.

```sql
-- DELETE FROM onet_data.onet_occupations_landing
-- WHERE onet_soc_code='11-2021.00';
-- DELETE FROM onet_data.occupation_skills 
-- WHERE onet_soc_code='11-2021.00';
```
  - [x] 5.5 Create function `get_skills_gap(from_onet_soc_code: str, to_onet_soc_code: str)`:
    - **IMPLEMENTATION NOTE:** Successfully implemented to identify skills present in target occupation but missing in source occupation. Function filters out skills with proficiency level 0 to ensure meaningful comparisons. Integration tests verify functionality with different occupation combinations.
    
    ```python
    # parameters: from_onet_soc_code, to_onet_soc_code
    # returns: [skill_name,...] # list of skills required by the second occupation that are not present in the first
    ```
    
  - [x] 5.6 Implement function `get_skills_gap_by_lvl(from_onet_soc_code: str, to_onet_soc_code: str)` to ensure it works with the latest schema:
    - **IMPLEMENTATION NOTE:** Successfully implemented to identify both missing skills and skills with higher proficiency requirements in the target occupation. Function utilizes get_occupation_and_skills with API fallback capability and the identify_skill_gap function for detailed analysis. Comprehensive integration tests verify all functionality.
    
    ```python
    # parameters: from_onet_soc_code, to_onet_soc_code
    # returns: [{element_id:..., skill_name:..., from_proficiency_level:..., to_proficiency_level:...},{}] # list of skills required by the second occupation that the first occupation either does not have or where the proficiency level is lower than in the second occupation.
    ```
  - [x] 5.7 Set up FastAPI framework in `src/api/main.py`.
    - **IMPLEMENTATION NOTE:** Successfully implemented FastAPI app with proper configuration, CORS middleware, environment variable loading, and health check endpoints. Created a script to run the API server with proper environment setup.
  
  - [x] 5.8 Update function `get_occupation_skills(onet_soc_code: str, scale_id_filter: str, engine)` to:
    - Call `ensure_occupation_data_is_present()` for the `onet_soc_code`.  (Note: consider if `ensure_skills_data_is_present` is also needed here or if `ensure_occupation_data_is_present` covers skills adequately for this function's purpose).
    - If successful, retrieve occupation skills data from local tables.
    - **IMPLEMENTATION NOTE:** This functionality was already implemented in previous tasks through the `get_occupation_and_skills` function, which includes API fallback and ensures data presence.
  
  - [x] 5.9 Create integration test for the updated `get_occupation_skills`.
    - **IMPLEMENTATION NOTE:** Integration tests for `get_occupation_and_skills` with API fallback were implemented in previous tasks.
  
  - [x] 5.10 Review `identify_skill_gap.py` (or alternative files for `get_skills_gap` / `get_skills_gap_by_lvl`) and ensure it properly processes the output from the relevant skill fetching/comparison functions.
    - **IMPLEMENTATION NOTE:** The `identify_skill_gap` function was already implemented and properly processes the output from skill fetching functions. It was integrated with the enhanced `get_skills_gap_by_lvl` function.
  
  - [x] 5.11 Create/Update integration test for `identify_skill_gap` (or the new gap functions).
    - **IMPLEMENTATION NOTE:** Comprehensive integration tests were created for both `get_skills_gap` and `get_skills_gap_by_lvl` functions in previous tasks.
  
  - [x] 5.12 Implement separate endpoints for skill gap analysis in `src/api/routers/skill_gap.py`:
    - `GET /skill-gap` endpoint for basic skill gap (skill names only)
    - `GET /skill-gap-by-lvl` endpoint for detailed skill gap with proficiency levels
    - Both endpoints should transform the internal skill gap data structure to match exactly the API response format specified in the PRD's FR4.3.
    - **IMPLEMENTATION NOTE:** Successfully refactored the API to use separate endpoints for basic and detailed skill gap analysis. The `/skill-gap` endpoint returns a simple list of skill names, while the `/skill-gap-by-lvl` endpoint provides detailed proficiency information. This provides clearer API design and makes future changes easier.
  
  - [x] 5.13 Create integration test for `/skill-gap` API endpoint.
    - **IMPLEMENTATION NOTE:** Created comprehensive integration tests in `tests/test_api_skill_gap.py` that verify all functionality of the endpoint, including basic skill gap, proficiency-level skill gap, same occupation comparison, and error handling for invalid occupation codes.

- [ ] 6.0 **Phase 6: Automated Testing Suite**
  - [ ] 6.1 Setup a test env with a postgresql database, this can act as a clean room for our automated tests to run in.
  - [ ] 6.2 Review existing integration tests and adapt them for the automated testing suite.
    - Review each test and determine if it should be included or moved to tests/archive folder
    - Update tests to work in isolation by leveraging existing functions to create mock assets
    - Ensure tests use consistent mock occupation data so they can be used for end-to-end testing
  - [ ] 6.3 Review functions and create any missing integration tests.
  - [ ] 6.4 Test each integration test in isolation using the test env with the postgresql database.
  - [ ] 6.5 Review all functions and see if we can remove any redundancies and make the code simpler and shorter if possible. See if the config api_exception_handles can be used to remove unnecessary exception handling.
  - [ ] 6.6 Rerun all the integration functions.
  - [ ] 6.7 Create an end to end integration test, this test should chain database creation, table initiation, loading the data to generating the skill gaps. Will leave the llm component out for now as that has not been implemented yet.

- [x] 7.0 **Phase 7: Containerization, Final Testing, and Documentation**
  - [x] 7.1 Update `docker-compose.yml` for all services (DB, API, ETL nodes as services/jobs).
    - **IMPLEMENTATION NOTE:** Enhanced the existing Docker Compose file to include API and ETL services alongside the MySQL database. Added proper dependency configuration to ensure services start in the correct order, with the ETL pipeline running after the database is healthy, and the API server dependent on the database. Set up appropriate networking, environment variables, and volume mounts.
  
  - [x] 7.2 Create/Update `Dockerfile.api`, `Dockerfile.etl`.
    - **IMPLEMENTATION NOTE:** Created Dockerfile.api for the REST API service using a Python 3.12 slim image, with appropriate environment variable configuration and uvicorn server setup. Created Dockerfile.etl for the ETL pipeline with a shell script that runs the full data processing sequence (extract_load_text_files, extract_load_api, transform) and exits when complete.
  
  - [x] 7.3 Ensure all integration tests pass in Docker environment.
  
  - [ ] 7.4 Test the API when deployed locally.
    - **NOTE TO DEVELOPER:** Deploy the application locally using Docker and manually test the API endpoints to ensure they're working correctly with real data.

  - [ ] 7.5 Update `README.md` (full setup, schema, data flow, API examples, design decisions).

- [ ] 8.0 **Phase 8: Cloud Deployment (OPTIONAL)**
  - [ ] 8.1 Create cloud deployment configuration for GCP Cloud Run
    - [ ] Prepare production-ready Docker image with proper security hardening
    - [ ] Set up environment variables for GCP Cloud Run deployment
    - [ ] Configure proper networking and security settings
  - [ ] 8.2 Set up CI/CD pipeline for automated deployment
    - [ ] Configure GitHub Actions or Cloud Build workflow
    - [ ] Implement testing as part of the deployment pipeline
    - [ ] Set up monitoring and alerting
  - [ ] 8.3 Document cloud deployment process and maintenance procedures
    - [ ] Create deployment runbook
    - [ ] Document rollback procedures
    - [ ] Add monitoring dashboard setup instructions

- [ ] 9.0 **Phase 9: LLM-Enhanced Skill Gap Analysis (OPTIONAL)**
  - [ ] 9.1 Create a new function `get_skills_gap_with_llm_descriptions` that:
    - Uses the existing LLM skill assessment to get proficiency data for both occupations
    - Compares LLM-assigned proficiency levels to identify gaps
    - Generates detailed descriptions for each gap via additional LLM calls
  - [ ] 9.2 Enhance the API endpoint to optionally include LLM-generated gap descriptions
    - Add a query parameter (e.g., `?include_llm_descriptions=true`) to request the enhanced output
    - Implement a fallback to standard gap analysis if LLM processing fails
  - [ ] 9.3 Update documentation to include this advanced feature
    - Add examples of both standard and LLM-enhanced API responses
    - Document performance and cost considerations
  - [ ] 9.4 Create integration tests for the LLM-enhanced skill gap analysis 

- [ ] 10.0 **Phase 10: API Data Normalization Pipeline (OUT OF SCOPE)**
  - [ ] 10.1 Design and implement an ETL pipeline for API data
    - Create transformation functions to convert API landing table data to normalized schema
    - Implement deduplication and data quality checks
    - Add incremental loading capability to avoid duplicating data
  - [ ] 10.2 Create scheduling for periodic API data normalization
    - Implement a schedule to run the normalization pipeline at regular intervals
    - Add logging and monitoring for the scheduled process
  - [ ] 10.3 Create integration tests for the normalization pipeline
    - Test data transformation accuracy
    - Test incremental loading functionality
    - Test error handling and recovery
  - [ ] 10.4 Update documentation with details on the normalization process
    - **IMPLEMENTATION NOTE:** While the on-demand API fetching with caching currently stores data in landing tables, a full ETL pipeline to normalize this data into the core tables would be a valuable future enhancement. This was deprioritized as we've already demonstrated API data fetching capability, and the current implementation is sufficient for the skill gap analysis features. Additionally, this would benefit from further product design input before implementation.
        