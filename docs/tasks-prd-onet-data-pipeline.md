## Relevant Files

- `src/config/schemas.py` - Defines SQLAlchemy models for database tables (`Occupations`, `Skills`, `Scales`, `OnetApiOccupationData`, `OnetApiSkillsData`).
- `src/functions/mysql_init_tables.py` - Initializes database tables using SQLAlchemy models.
- `src/functions/extract_onet_data.py` - Extracts data from O*NET `.txt` files (`Occupation.txt`, `Skills.txt`, `Scales.txt`) into pandas DataFrames.
- `src/functions/mysql_load.py` - Loads data from DataFrames into MySQL tables (`Occupations`, `Skills`, `Scales`).
- `src/functions/extract_onet_api_data.py` - **NEW:** Extracts data from O*NET Web Services API for `Occupation_Data` and `Skills` into pandas DataFrames. Will use `onet_api.mdc` for guidance.
- `tests/test_extract_onet_api_data.py` - **NEW:** Unit tests for `extract_onet_api_data.py`.
- `src/functions/mysql_upsert_api_data.py` - **NEW:** Upserts data from API-sourced DataFrames into `OnetApiOccupationData` and `OnetApiSkillsData` tables.
- `tests/test_mysql_upsert_api_data.py` - **NEW:** Unit tests for `mysql_upsert_api_data.py`.
- `src/functions/llm_skill_profiler.py` - To house the LLM interaction logic for skill proficiency scoring.
- `tests/test_llm_skill_profiler.py` - Unit tests for `llm_skill_profiler.py`.
- `src/nodes/extract_load_text_files.py` - Orchestrates the initial data extraction from text files and loading into the database (formerly `extract_load.py`).
- `src/nodes/extract_load_api_data.py` - **NEW:** Orchestrates the O*NET API data extraction and loading/upserting into the database.
- `src/nodes/enrich_skill_data.py` - Orchestrates the LLM enrichment of skill proficiency data in the `Skills` table (for 'LV' scale data_values).
- `src/functions/get_occupation_skills.py` - Retrieves occupation skills data, needs to be updated to use `Skills` table (filtering by onet_soc_code and scale_id='LV') with LLM-derived `data_value`.
- `tests/test_get_occupation_skills.py` - Unit tests for `get_occupation_skills.py` (may need update).
- `src/functions/identify_skill_gap.py` - Contains the core logic for comparing two occupations' skills (seems mostly complete for 'LV' scale, relies on input from `get_occupation_skills`).
- `tests/test_identify_skill_gap.py` - Unit tests for `identify_skill_gap.py`.
- `src/api/main.py` - Main FastAPI/Flask application file for the REST API.
- `src/api/routers/skill_gap.py` - API router/controller for the `/skill-gap` endpoint.
- `tests/test_api_skill_gap.py` - Integration tests for the `/skill-gap` API endpoint.
- `docker-compose.yml` - Defines and configures services (MySQL, ETL, API).
- `Dockerfile.api` - Dockerfile for the API service.
- `Dockerfile.etl` - Dockerfile for the ETL service (if ETL is run as a separate containerized script).
- `requirements.txt` - Python project dependencies.
- `env/env.env` - Environment variable configuration.
- `README.md` - Project documentation, setup, and API usage instructions.
- `tests/test_integration_*.py` - Existing and new integration tests.
- `tests/test_integration_*.sh` - Shell scripts for running integration tests.

### Notes

- Unit tests should typically be placed alongside the code files they are testing or in a corresponding `tests/unit` subdirectory.
- Integration tests are typically in the `tests/` directory.
- Use `pytest` (or `python -m pytest`) to run tests. Test discovery should find tests matching `test_*.py` patterns.

## Tasks

- [x] 1.0 **Phase 1: Setup & Database Schema Baseline (Text Files)** (PRD G2, FR2)
  - [x] 1.1 Define environment variables for DB connection (`env/env.env`).
  - [x] 1.2 Update `src/config/schemas.py` with SQLAlchemy models for `Occupations`, `Skills`, and `Scales` tables (from text files), ensuring all fields from PRD (FR2.2) are included.
  - [x] 1.3 Implement `src/functions/mysql_init_tables.py` to create/recreate tables based on schemas for text file data.
  - [x] 1.4 Define primary keys in `src/config/schemas.py` for text file tables.
  - [x] 1.5 Create integration test for table initialization (`tests/test_integration_mysql_init_tables.py` and `.sh` script).

- [x] 2.0 **Phase 1: ETL Pipeline - Text File Data Extraction & Basic Load** (PRD G1, G3 (partial), FR1, FR3.1, FR3.2, FR3.4)
  - [x] 2.1 Implement `src/functions/extract_onet_data.py` to read `Occupation.txt`, `Skills.txt`, and `Scales.txt` into pandas DataFrames.
  - [x] 2.2 Implement/Update `src/functions/mysql_load.py` to load data into `Occupations`, `Skills`, `Scales` tables from text file DataFrames.
  - [x] 2.3 Create `src/nodes/extract_load_text_files.py` to orchestrate the extraction and loading of all three text files.
  - [x] 2.4 Create/Update integration test for the basic ETL data loading process from text files (`tests/test_integration_mysql_load.py` and `.sh` script).

- [x] 3.0 **Phase 1: Refinement & Cleanup**
  - [x] 3.1 Review `src/functions/extract_onet_data.py`, `src/functions/mysql_load.py`, and `src/nodes/extract_load_text_files.py` for clarity, efficiency, and adherence to `functions.mdc` guidelines.
  - [x] 3.2 Ensure all existing integration tests (`mysql_init_tables`, `mysql_load`) are robust and cover key success/failure scenarios for Phase 1 scope.
  - [x] 3.3 Verify `README.md` includes basic setup and run instructions for the Phase 1 ETL data pipeline (text files).

- [ ] 4.0 **Phase 2: Data Ingestion - O*NET API Integration**
  - [ ] 4.1 Define SQLAlchemy schemas in `src/config/schemas.py` for new tables to store API data: `OnetApiOccupationData` and `OnetApiSkillsData`. These tables will mirror the structure of `Occupation_Data.txt` and `Skills.txt` respectively, as closely as the API allows. Consider adding source/timestamp fields.
  - [ ] 4.2 Update `src/functions/mysql_init_tables.py` to include creation of `OnetApiOccupationData` and `OnetApiSkillsData` tables. Ensure this function can be run without re-creating existing text-file based tables if not desired.
  - [ ] 4.3 Create `src/functions/extract_onet_api_data.py`:
    - [ ] 4.3.1 Implement logic to connect to O*NET API (handle auth, headers, clientname - refer to `.cursor/rules/onet_api.mdc`).
    - [ ] 4.3.2 Implement function to fetch all occupation codes and titles (paginated) as per section 3.1 of `onet_api.mdc`.
    - [ ] 4.3.3 Implement function to fetch detailed occupation data (description) for each occupation code, creating a DataFrame for `OnetApiOccupationData` (section 3.2 of `onet_api.mdc`).
    - [ ] 4.3.4 Implement function to parse skills data from detailed occupation reports, creating a DataFrame for `OnetApiSkillsData` (section 3.3 of `onet_api.mdc`). Log missing fields as per rule.
    - [ ] 4.3.5 Implement function to get `Scales_Reference.txt` data (direct download/embedded as per section 3.4 of `onet_api.mdc`) if not already robustly handled by text file ETL. This might be used to validate/supplement API skill scale data.
  - [ ] 4.4 Create unit tests for `src/functions/extract_onet_api_data.py` (`tests/test_extract_onet_api_data.py`), mocking API calls.
  - [ ] 4.5 Create `src/functions/mysql_upsert_api_data.py`:
    - [ ] 4.5.1 Implement function to take DataFrames from `extract_onet_api_data.py` and upsert data into `OnetApiOccupationData` table.
    - [ ] 4.5.2 Implement function to take DataFrames from `extract_onet_api_data.py` and upsert data into `OnetApiSkillsData` table.
    - [ ] (Consider whether to clear tables before upsert or perform true upsert logic based on primary keys).
  - [ ] 4.6 Create unit tests for `src/functions/mysql_upsert_api_data.py` (`tests/test_mysql_upsert_api_data.py`).
  - [ ] 4.7 Create `src/nodes/extract_load_api_data.py` to orchestrate the API data extraction and loading/upserting process.
  - [ ] 4.8 Create/Update integration test for the API data loading process (`tests/test_integration_api_load.py` and `.sh` script).

- [ ] 5.0 **Phase 3: Database Normalization & Creation of Consumption Views/Tables**
  - [ ] 5.1 Define schema and implement creation of downstream normalized tables or materialized views that combine data from text-file sources and API sources. For example:
    - [ ] 5.1.1 A consolidated `OccupationsView` that intelligently merges data from `Occupations` (text file) and `OnetApiOccupationData`.
    - [ ] 5.1.2 A consolidated `SkillsView` that intelligently merges data from `Skills` (text file) and `OnetApiSkillsData`, potentially prioritizing one source over another or filling gaps.
  - [ ] 5.2 Update `src/functions/mysql_init_tables.py` or create a new function/node to manage the creation/refresh of these normalized views/tables.
  - [ ] 5.3 Re-introduce and test Foreign Key constraints in `src/config/schemas.py` for original `Skills.onet_soc_code` -> `Occupations.onet_soc_code` and `Skills.scale_id` -> `Scales.scale_id`. Apply similar constraints to API tables if appropriate.
  - [ ] 5.4 Update `src/functions/mysql_load.py` (for text files) and `src/functions/mysql_upsert_api_data.py` (for API) to ensure data is loaded/upserted in an order that respects FK constraints if they are enforced during these operations.
  - [ ] 5.5 Update integration tests to verify data integrity with foreign key constraints enabled and to test the creation and content of normalized views/tables.

- [ ] 6.0 **Phase 4: ETL Pipeline Enhancement - LLM Integration for Skill Proficiency** (PRD G3 (LLM part), FR3.3)
  - [ ] 6.1 Research and select a suitable pre-trained LLM for analyzing skill proficiency.
  - [ ] 6.2 Create `src/functions/llm_skill_profiler.py` to interact with the LLM. This function might take skill descriptions or contexts and return proficiency scores.
  - [ ] 6.3 Create unit tests for `src/functions/llm_skill_profiler.py`.
  - [ ] 6.4 Create `src/nodes/enrich_skill_data.py`. This node will:
    - [ ] 6.4.1 Read data from the `SkillsView` (or relevant source table for skills that need enrichment, e.g., those with `scale_id` = 'LV').
    - [ ] 6.4.2 For each relevant skill, call `llm_skill_profiler.py` to get an LLM-derived `data_value`.
    - [ ] 6.4.3 Update the appropriate table (e.g., a new column in `SkillsView` or back into `Skills`/`OnetApiSkillsData` if direct update is preferred, or a new `LLMSkillScores` table) with the LLM scores.
  - [ ] 6.5 Create/Update integration tests for LLM enrichment process.

- [ ] 7.0 **Phase 5: REST API Implementation: Skill Gap Endpoint** (PRD G4, G5, FR4)
  - [ ] 7.1 Choose and set up a Python web framework (e.g., FastAPI, Flask) in `src/api/`.
  - [ ] 7.2 Update `src/functions/get_occupation_skills.py` to use the normalized/enriched skill data (e.g., from `SkillsView` or the table updated by LLM) for retrieving skills relevant to the `/skill-gap` endpoint (likely focusing on `scale_id`='LV').
  - [ ] 7.3 Create/Update unit tests for `src/functions/get_occupation_skills.py`.
  - [ ] 7.4 Review `src/functions/identify_skill_gap.py`. Ensure it correctly uses data from `get_occupation_skills`.
  - [ ] 7.5 Create unit tests for `src/functions/identify_skill_gap.py`.
  - [ ] 7.6 Create API main application file (`src/api/main.py`).
  - [ ] 7.7 Implement `GET /skill-gap` endpoint in `src/api/routers/skill_gap.py`. This endpoint will use `get_occupation_skills` and `identify_skill_gap`.
  - [ ] 7.8 Implement logging for API.
  - [ ] 7.9 Create integration tests for `/skill-gap` API endpoint (`tests/test_api_skill_gap.py`).

- [ ] 8.0 **Phase 6: Containerization, Advanced Testing, and Documentation** (PRD G6, G7, G8)
  - [ ] 8.1 Update `docker-compose.yml` to include the API service and any ETL services/nodes if they are to be run as separate containerized scripts/jobs.
  - [ ] 8.2 Create `Dockerfile.api` for the API service.
  - [ ] 8.3 Create `Dockerfile.etl` if ETL processes (text file, API, LLM enrichment) are containerized separately.
  - [ ] 8.4 Ensure all dependencies are correctly listed in `requirements.txt`.
  - [ ] 8.5 Update integration test shell scripts (`.sh`) to work within a Dockerized environment if necessary (e.g., using `docker-compose exec`).
  - [ ] 8.6 Ensure all automated tests (unit and integration) pass consistently.
  - [ ] 8.7 Update `README.md` with comprehensive information: full setup instructions (local and Docker), detailed database schema (including new API and view tables), data flow diagrams, design decisions, assumptions, and clear API usage examples for the `/skill-gap` endpoint.
  - [ ] 8.8 Implement comprehensive error handling and logging across all components (ETL functions, nodes, API). 