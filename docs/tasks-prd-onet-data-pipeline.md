## Relevant Files

- `src/config/schemas.py` - Defines SQLAlchemy models for database tables (`Occupations`, `Skills`, `Scales`, `OnetApiOccupationData`, `OnetApiSkillsData`).
- `src/functions/mysql_init_tables.py` - Initializes database tables using SQLAlchemy models.
- `tests/test_integration_mysql_init_tables.py` - Integration tests for `mysql_init_tables.py`.
- `src/functions/extract_onet_data.py` - Extracts data from O*NET `.txt` files into pandas DataFrames.
- `tests/test_integration_extract_onet_data.py` - Integration tests for `extract_onet_data.py`.
- `src/functions/mysql_load_dataframe.py` - Loads a single pandas DataFrame into a specified MySQL table.
- `tests/test_integration_mysql_load_dataframe.py` - Integration tests for `mysql_load_dataframe.py`.
- `src/functions/extract_onet_api_occupation_codes.py` - **NEW:** Fetches all O*NET-SOC occupation codes and titles from the API.
- `tests/test_integration_extract_onet_api_occupation_codes.py` - **NEW:** Integration tests for `extract_onet_api_occupation_codes.py`.
- `src/functions/extract_onet_api_occupation_details.py` - **NEW:** Fetches detailed occupation data (description) for a list of occupation codes from the API.
- `tests/test_integration_extract_onet_api_occupation_details.py` - **NEW:** Integration tests for `extract_onet_api_occupation_details.py`.
- `src/functions/extract_onet_api_skills_data.py` - **NEW:** Parses skills data from detailed occupation API responses.
- `tests/test_integration_extract_onet_api_skills_data.py` - **NEW:** Integration tests for `extract_onet_api_skills_data.py`.
- `src/functions/get_onet_scales_reference.py` - **NEW:** Retrieves O*NET Scales Reference data (direct download or embedded).
- `tests/test_integration_get_onet_scales_reference.py` - **NEW:** Integration tests for `get_onet_scales_reference.py`.
- `src/functions/mysql_upsert_dataframe.py` - **NEW:** Upserts a pandas DataFrame into a specified MySQL table.
- `tests/test_integration_mysql_upsert_dataframe.py` - **NEW:** Integration tests for `mysql_upsert_dataframe.py`.
- `src/functions/llm_skill_profiler.py` - To house the LLM interaction logic for skill proficiency scoring.
- `tests/test_integration_llm_skill_profiler.py` - Integration tests for `llm_skill_profiler.py`.
- `src/nodes/extract_load_text_files.py` - Orchestrates text file data extraction and loading.
- `tests/test_integration_extract_load_text_files.py` - Integration tests for `extract_load_text_files.py`.
- `src/nodes/extract_load_api_data.py` - **NEW:** Orchestrates O*NET API data extraction and loading.
- `tests/test_integration_extract_load_api_data.py` - **NEW:** Integration tests for `extract_load_api_data.py`.
- `src/nodes/enrich_skill_data.py` - Orchestrates LLM enrichment of skill proficiency data.
- `tests/test_integration_enrich_skill_data.py` - Integration tests for `enrich_skill_data.py`.
- `src/functions/get_occupation_skills.py` - Retrieves occupation skills data for API.
- `tests/test_integration_get_occupation_skills.py` - Integration tests for `get_occupation_skills.py`.
- `src/functions/identify_skill_gap.py` - Contains the core logic for comparing two occupations' skills.
- `tests/test_integration_identify_skill_gap.py` - Integration tests for `identify_skill_gap.py`.
- `src/api/main.py` - Main FastAPI/Flask application file for the REST API.
- `src/api/routers/skill_gap.py` - API router/controller for the `/skill-gap` endpoint.
- `tests/test_api_skill_gap.py` - Integration tests for the `/skill-gap` API endpoint.
- `docker-compose.yml` - Defines and configures services (MySQL, ETL, API).
- `Dockerfile.api` - Dockerfile for the API service.
- `Dockerfile.etl` - Dockerfile for the ETL service.
- `requirements.txt` - Python project dependencies.
- `env/env.env` - Environment variable configuration.
- `README.md` - Project documentation.

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

- [ ] 2.0 **Phase 2: Data Ingestion - O*NET API Integration Functions**
  - [ ] 2.1 Define SQLAlchemy schemas in `src/config/schemas.py` for API data: `OnetApiOccupationData` and `OnetApiSkillsData`. Include source/timestamp fields.
  - [ ] 2.2 Update `mysql_init_tables` function in `src/functions/mysql_init_tables.py` to optionally accept a list of specific table model classes to create/recreate, and update its integration test.
  - [ ] 2.3 Create function `extract_onet_api_occupation_codes(api_username: str, api_key: str, client_name: str, base_url: str)` in `src/functions/extract_onet_api_occupation_codes.py`. Inputs: API creds, client name, base URL. Outputs: `{"success": bool, "message": str, "result": {"occupation_codes_df": pd.DataFrame}}`. Fetches all O*NET-SOC codes and titles. (Ref: `onet_api.mdc` Sec 3.1)
  - [ ] 2.4 Create integration test for `extract_onet_api_occupation_codes` (`tests/test_integration_extract_onet_api_occupation_codes.py` and `.sh`).
  - [ ] 2.5 Create function `extract_onet_api_occupation_details(occupation_codes_df: pd.DataFrame, api_username: str, api_key: str, client_name: str, base_url: str)` in `src/functions/extract_onet_api_occupation_details.py`. Inputs: DataFrame of codes, API creds, client name, base URL. Outputs: `{"success": bool, "message": str, "result": {"occupation_details_df": pd.DataFrame}}`. Fetches details for each code. (Ref: `onet_api.mdc` Sec 3.2)
  - [ ] 2.6 Create integration test for `extract_onet_api_occupation_details` (`tests/test_integration_extract_onet_api_occupation_details.py` and `.sh`).
  - [ ] 2.7 Create function `extract_onet_api_skills_data(occupation_details_json_list: list, occupation_codes: list)` in `src/functions/extract_onet_api_skills_data.py`. Inputs: list of JSON responses from occupation detail API calls, list of corresponding O*NET-SOC codes. Outputs: `{"success": bool, "message": str, "result": {"skills_api_df": pd.DataFrame}}`. Parses skills from API responses. (Ref: `onet_api.mdc` Sec 3.3)
  - [ ] 2.8 Create integration test for `extract_onet_api_skills_data` (`tests/test_integration_extract_onet_api_skills_data.py` and `.sh`). (Requires sample API JSON responses for testing without live calls).
  - [ ] 2.9 Create function `get_onet_scales_reference(url: str)` in `src/functions/get_onet_scales_reference.py`. Inputs: URL to `Scales_Reference.txt`. Outputs: `{"success": bool, "message": str, "result": {"scales_df": pd.DataFrame}}`. Downloads or uses embedded data. (Ref: `onet_api.mdc` Sec 3.4)
  - [ ] 2.10 Create integration test for `get_onet_scales_reference` (`tests/test_integration_get_onet_scales_reference.py` and `.sh`).
  - [ ] 2.11 Create function `mysql_upsert_dataframe(df: pd.DataFrame, table_name: str, engine, primary_key_cols: list)` in `src/functions/mysql_upsert_dataframe.py`. Inputs: DataFrame, table name, SQLAlchemy engine, list of PK columns for conflict resolution. Outputs: `{"success": bool, "message": str}`. Upserts DataFrame to MySQL.
  - [ ] 2.12 Create integration test for `mysql_upsert_dataframe` (`tests/test_integration_mysql_upsert_dataframe.py` and `.sh`) using `OnetApiOccupationData` as an example.
  - [ ] 2.13 Create node `extract_load_api_data.py` in `src/nodes/`. This node will use `mysql_init_tables` (for API tables), `extract_onet_api_occupation_codes`, `extract_onet_api_occupation_details`, `extract_onet_api_skills_data`, and `mysql_upsert_dataframe` to extract and load/upsert API data into `OnetApiOccupationData` and `OnetApiSkillsData`.
  - [ ] 2.14 Create integration test for `extract_load_api_data` node (`tests/test_integration_extract_load_api_data.py` and `.sh` script).

- [ ] 3.0 **Phase 3: Database Normalization & Consumption Views**
  - [ ] 3.1 Design and define SQL queries or SQLAlchemy views for `OccupationsView` and `SkillsView` that merge data from text-file and API tables. Document the merge logic (e.g., prioritizing sources, filling gaps).
  - [ ] 3.2 Update `mysql_init_tables` or create a new function (e.g., `manage_database_views`) to create/refresh these views in `src/functions/`.
  - [ ] 3.3 Create integration test for view creation/refresh logic.
  - [ ] 3.4 Implement and test Foreign Key constraints for `Skills.onet_soc_code` -> `Occupations.onet_soc_code` and `Skills.scale_id` -> `Scales.scale_id`. Apply to API tables if appropriate. Update `mysql_load_dataframe` and `mysql_upsert_dataframe` to handle potential FK issues or ensure correct loading order if constraints are immediate.
  - [ ] 3.5 Update integration tests to verify data integrity with FKs and test view content.

- [ ] 4.0 **Phase 4: LLM Integration for Skill Proficiency**
  - [ ] 4.1 Research and select/configure LLM for skill proficiency analysis.
  - [ ] 4.2 Create function `llm_skill_profiler(skill_data: pd.DataFrame, text_column: str)` in `src/functions/llm_skill_profiler.py`. Inputs: DataFrame with skill info (e.g., from `SkillsView`), column name with text for LLM. Outputs: `{"success": bool, "message": str, "result": {"llm_scores_df": pd.DataFrame}}` with original data + LLM scores.
  - [ ] 4.3 Create integration test for `llm_skill_profiler` (`tests/test_integration_llm_skill_profiler.py` and `.sh`). (May require mocking LLM calls for CI/CD).
  - [ ] 4.4 Create node `enrich_skill_data.py` in `src/nodes/`. This node will:
    - [ ] 4.4.1 Read data (e.g., from `SkillsView`, filtering for `scale_id` = 'LV').
    - [ ] 4.4.2 Call `llm_skill_profiler`.
    - [ ] 4.4.3 Upsert LLM-derived `data_value` back into a relevant table or a new `LLMSkillScores` table using `mysql_upsert_dataframe`.
  - [ ] 4.5 Create integration test for `enrich_skill_data` node (`tests/test_integration_enrich_skill_data.py` and `.sh`).

- [ ] 5.0 **Phase 5: REST API for Skill Gap Analysis**
  - [ ] 5.1 Set up FastAPI framework in `src/api/main.py`.
  - [ ] 5.2 Create function `get_occupation_skills(onet_soc_code: str, scale_id_filter: str, engine)` in `src/functions/get_occupation_skills.py`. Inputs: occupation code, scale ID to filter (e.g., 'LV'), SQLAlchemy engine. Outputs: `{"success": bool, "message": str, "result": {"skills_df": pd.DataFrame}}`. Uses `SkillsView` or LLM-enriched data.
  - [ ] 5.3 Create integration test for `get_occupation_skills` (`tests/test_integration_get_occupation_skills.py` and `.sh`).
  - [ ] 5.4 Review `identify_skill_gap.py`. Ensure it takes two DataFrames (from `get_occupation_skills`) as input and outputs `{"success": bool, "message": str, "result": {"skill_gap_df": pd.DataFrame}}`.
  - [ ] 5.5 Create/Update integration test for `identify_skill_gap` (`tests/test_integration_identify_skill_gap.py` and `.sh`).
  - [ ] 5.6 Implement `GET /skill-gap` endpoint in `src/api/routers/skill_gap.py` using the functions above.
  - [ ] 5.7 Create integration test for `/skill-gap` API endpoint (`tests/test_api_skill_gap.py` and `.sh`).

- [ ] 6.0 **Phase 6: Containerization, Final Testing, and Documentation**
  - [ ] 6.1 Update `docker-compose.yml` for all services (DB, API, ETL nodes as services/jobs).
  - [ ] 6.2 Create/Update `Dockerfile.api`, `Dockerfile.etl`.
  - [ ] 6.3 Finalize `requirements.txt`.
  - [ ] 6.4 Ensure all integration tests pass in Docker environment.
  - [ ] 6.5 Update `README.md` (full setup, schema, data flow, API examples, design decisions).
  - [ ] 6.6 Implement comprehensive error handling and logging across all components. 