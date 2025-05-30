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
```
    - [x] 4.3 Create function get_occupation_and_skills for getting and structuring the data that needs to be passed to 4.2 (generating the prompt for the llm).    
    - [x] 4.4 Update the @Schema @mysql_init_tables and @mysql_load_tables to initialize tables in the database to store the LLM responses.
    - [x] 4.5 Create function mysql_load_llm_skill_proficiencies to load LLM assessment results into the database.
    - [x] 4.6 Create integration tests for the LLM skill proficiency assessment pipeline.
    - [x] 4.7 Align documentation with the implemented LLM response schema.
    - [x] 4.8 Create node `llm_skill_proficiency_request.py` to orchestrate the pipeline for a single occupation.
    - [x] 4.9 Create shell script `llm_skill_proficiency_request.sh` to execute the node.

- [ ] 5.0 **Phase 5: REST API for Skill Gap Analysis (Incorporating On-Demand API Fetching & Caching)**
  - [ ] 5.1 Create function `ensure_occupation_data_is_present(onet_soc_code: str, engine)` that:
    - Checks local DB for the given `onet_soc_code`.
    - If data is missing or incomplete:
        - Calls `onet_api_pull(onet_soc_code)` to fetch occupation and skills data.
        - Loads the fetched data into the appropriate tables.
        - Returns a success/failure status.
  - [ ] 5.2 Create function `ensure_skills_data_is_present(onet_soc_code: str, engine)` that:
    - Checks local DB for the given `onet_soc_code`.
    - If data is missing or incomplete:
        - Calls `onet_api_pull(onet_soc_code)` to fetch occupation and skills data.
        - Loads the fetched data into the appropriate tables.
        - Returns a success/failure status.
  - [ ] 5.3 Create function `get_skills_gap(from_onet_soc_code: str, to_onet_soc_code: str)`:
    - **IMPLEMENTATION NOTE:** This is to meet the requirements as per the requirements spec.
    ```python
    # parameters: from_onet_soc_code, to_onet_soc_code
    # returns: [skill_name,...] # list of skills required by the second occupation that are not present in the first
    ```
  - [ ] 5.4 Refactor function `get_skills_gap_by_lvl(from_onet_soc_code: str, to_onet_soc_code: str)` to ensure it works with the latest schema:
    - **IMPLEMENTATION NOTE:** Felt this was way more valuable than just a list of missing skills and made more sense so I implemented this as well.
    ```python
    # parameters: from_onet_soc_code, to_onet_soc_code
    # returns: [{element_id:..., skill_name:..., proficiency_level:...},{}] # list of skills required by the second occupation that the first occupation either does not have or the level is lower then the second occupation.
    ```
  - [ ] 5.5 Set up FastAPI framework in `src/api/main.py`.
  - [ ] 5.6 Update function `get_occupation_skills(onet_soc_code: str, scale_id_filter: str, engine)` to:
    - Call `ensure_occupation_data_is_present()` for the `onet_soc_code`.  (Note: consider if `ensure_skills_data_is_present` is also needed here or if `ensure_occupation_data_is_present` covers skills adequately for this function's purpose).
    - If successful, retrieve occupation skills data from local tables.
  - [ ] 5.7 Create integration test for the updated `get_occupation_skills`.
  - [ ] 5.8 Review `identify_skill_gap.py` (or alternative files for `get_skills_gap` / `get_skills_gap_by_lvl`) and ensure it properly processes the output from the relevant skill fetching/comparison functions.
  - [ ] 5.9 Create/Update integration test for `identify_skill_gap` (or the new gap functions).
  - [ ] 5.10 Implement `GET /skill-gap` endpoint in `src/api/routers/skill_gap.py`. This endpoint should utilize the functions from 5.3 and/or 5.4.
  - [ ] 5.11 Create integration test for `/skill-gap` API endpoint.

- [ ] 6.0 **Phase 6: Containerization, Final Testing, and Documentation**
  - [ ] 6.1 Update `docker-compose.yml` for all services (DB, API, ETL nodes as services/jobs).
  - [ ] 6.2 Create/Update `Dockerfile.api`, `Dockerfile.etl`.
  - [ ] 6.3 Finalize `requirements.txt`.
  - [ ] 6.4 Ensure all integration tests pass in Docker environment.
  - [ ] 6.5 Update `README.md` (full setup, schema, data flow, API examples, design decisions).
  - [ ] 6.6 Implement comprehensive error handling and logging across all components. 