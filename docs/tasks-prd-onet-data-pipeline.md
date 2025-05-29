## Relevant Files

- `src/config/schemas.py` - Defines SQLAlchemy models for database tables (`Occupations`, `Skills`, `Scales`). (Occupation_Skills removed)
- `src/functions/mysql_init_tables.py` - Initializes database tables using SQLAlchemy models.
- `src/functions/extract_onet_data.py` - Extracts data from O*NET `.txt` files (`Occupation.txt`, `Skills.txt`, `Scales.txt`) into pandas DataFrames.
- `src/functions/mysql_load.py` - Loads data from DataFrames into MySQL tables (`Occupations`, `Skills`, `Scales`). Needs review for LLM integration and new Skills schema.
- `src/functions/llm_skill_profiler.py` - **NEW:** To house the LLM interaction logic for skill proficiency scoring.
- `tests/test_llm_skill_profiler.py` - **NEW:** Unit tests for `llm_skill_profiler.py`.
- `src/nodes/extract_load.py` - Orchestrates the initial data extraction and loading into the database.
- `src/nodes/enrich_skill_data.py` - **NEW:** Orchestrates the LLM enrichment of skill proficiency data in the `Skills` table (for 'LV' scale data_values).
- `src/functions/get_occupation_skills.py` - Retrieves occupation skills data, needs to be updated to use `Skills` table (filtering by onet_soc_code and scale_id='LV') with LLM-derived `data_value`.
- `tests/test_get_occupation_skills.py` - Unit tests for `get_occupation_skills.py` (may need update).
- `src/functions/identify_skill_gap.py` - Contains the core logic for comparing two occupations' skills (seems mostly complete for 'LV' scale, relies on input from `get_occupation_skills`).
- `tests/test_identify_skill_gap.py` - Unit tests for `identify_skill_gap.py`.
- `src/api/main.py` - **NEW:** Main FastAPI/Flask application file for the REST API.
- `src/api/routers/skill_gap.py` - **NEW:** API router/controller for the `/skill-gap` endpoint.
- `tests/test_api_skill_gap.py` - **NEW:** Integration tests for the `/skill-gap` API endpoint.
- `docker-compose.yml` - Defines and configures services (MySQL, ETL, API).
- `Dockerfile.api` - **NEW:** Dockerfile for the API service.
- `Dockerfile.etl` - **NEW:** Dockerfile for the ETL service (if ETL is run as a separate containerized script).
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

- [x] 1.0 **Phase 1 MVP: Setup & Database Schema Baseline** (PRD G2, FR2)
  - [x] 1.1 Define environment variables for DB connection (`env/env.env`).
  - [x] 1.2 Update `src/config/schemas.py` with SQLAlchemy models for `Occupations`, `Skills`, and `Scales` tables, ensuring all fields from PRD (FR2.2) are included. (Note: `Occupation_Skills` table removed; `Skills` table expanded. Foreign key constraints on `Skills.onet_soc_code` and `Skills.scale_id` deferred to Phase 2 for simplification of initial load).
  - [x] 1.3 Implement `src/functions/mysql_init_tables.py` to create/recreate tables based on schemas. (Includes logic to temporarily disable FK checks during drop/create due to existing DB constraints).
  - [x] 1.4 Define primary keys in `src/config/schemas.py` (e.g., `Skills` table composite PK: `onet_soc_code`, `element_id`, `scale_id`). Explicit foreign key constraints deferred to Phase 2 (PRD FR2.3).
  - [x] 1.5 Create integration test for table initialization (`tests/test_integration_mysql_init_tables.py` and `.sh script).

- [x] 2.0 **Phase 1 MVP: ETL Pipeline - Data Extraction & Basic Load** (PRD G1, G3 (partial), FR1, FR3.1, FR3.2, FR3.4)
  - [x] 2.1 Implement `src/functions/extract_onet_data.py` to read `Occupation.txt`, `Skills.txt`, and `Scales.txt` into pandas DataFrames, performing necessary column renaming and basic type conversions (PRD FR1.1, FR1.2).
  - [x] 2.2 Implement/Update `src/functions/mysql_load.py` (`load_data_from_dataframe` function) to:
    - [x] Load data into `Occupations` table.
    - [x] Load data into `Skills` table (from `Skills.txt`, including all fields like `onet_soc_code`, `scale_id`, `data_value`).
    - [x] Load data into `Scales` table.
    - [x] Ensure the function clears existing data before loading (PRD FR3.4).
  - [x] 2.3 Update `src/nodes/extract_load.py` to orchestrate the extraction and loading of all three files (`Occupations`, `Skills`, `Scales`). (Verification: Assumed this node calls `extract_onet_data` and then `mysql_load` appropriately for the files).
  - [x] 2.4 Create/Update integration test for the basic ETL data loading process (`tests/test_integration_mysql_load.py` and `.sh script, now passing).

- [ ] 3.0 **Phase 1 Refinement & Cleanup**
  - [ ] 3.1 Review `src/functions/extract_onet_data.py`, `src/functions/mysql_load.py`, and `src/nodes/extract_load.py` for clarity, efficiency, and adherence to `functions.mdc` guidelines (e.g., standard return formats, docstrings, one function per file if not already the case).
  - [ ] 3.2 Ensure all existing integration tests (`mysql_init_tables`, `mysql_load`) are robust and cover key success/failure scenarios for the current (Phase 1) scope.
  - [ ] 3.3 Verify `README.md` includes basic setup and run instructions for the Phase 1 ETL data pipeline.

- [ ] 4.0 **Phase 2: Database Normalization & Validation**
  - [ ] 4.1 Re-introduce and test Foreign Key constraints in `src/config/schemas.py` for `Skills.onet_soc_code` -> `Occupations.onet_soc_code` and `Skills.scale_id` -> `Scales.scale_id`.
  - [ ] 4.2 Update `src/functions/mysql_init_tables.py` to handle schema creation with these constraints (may not need changes if `SET FOREIGN_KEY_CHECKS=0` is sufficient, but verify).
  - [ ] 4.3 Update `src/functions/mysql_load.py` and `src/nodes/extract_load.py` to ensure data is loaded in an order that respects these constraints (e.g., Occupations and Scales before Skills). This might involve re-introducing a controlled loading order.
  - [ ] 4.4 Update integration tests to verify data integrity with foreign key constraints enabled.

- [ ] 5.0 **Phase 2: ETL Pipeline Enhancement - LLM Integration for Skill Proficiency** (PRD G3 (LLM part), FR3.3)
  - [ ] 5.1 Research and select a suitable pre-trained LLM for analyzing skill proficiency.
  - [ ] 5.2 Create `src/functions/llm_skill_profiler.py`.
  - [ ] 5.3 Create unit tests for `src/functions/llm_skill_profiler.py`.
  - [ ] 5.4 Create `src/nodes/enrich_skill_data.py`.
  - [ ] 5.5 Create/Update integration tests for LLM enrichment.

- [ ] 6.0 **Phase 3: REST API Implementation: Skill Gap Endpoint** (PRD G4, G5, FR4)
  - [ ] 6.1 Choose and set up a Python web framework.
  - [ ] 6.2 Update `src/functions/get_occupation_skills.py`.
  - [ ] 6.3 Create/Update unit tests for `src/functions/get_occupation_skills.py`.
  - [ ] 6.4 Review `src/functions/identify_skill_gap.py`.
  - [ ] 6.5 Create unit tests for `src/functions/identify_skill_gap.py`.
  - [ ] 6.6 Create API main application file (`src/api/main.py`).
  - [ ] 6.7 Implement `GET /skill-gap` endpoint (`src/api/routers/skill_gap.py`).
  - [ ] 6.8 Implement logging for API.
  - [ ] 6.9 Create integration tests for `/skill-gap` API endpoint.

- [ ] 7.0 **Phase 4: Containerization, Advanced Testing, and Documentation** (PRD G6, G7, G8)
  - [ ] 7.1 Update `docker-compose.yml` (API service, ETL service if separate).
  - [ ] 7.2 Create `Dockerfile.api`.
  - [ ] 7.3 Create `Dockerfile.etl` (if separate).
  - [ ] 7.4 Ensure all dependencies in `requirements.txt`.
  - [ ] 7.5 Update integration test shell scripts for Docker environment.
  - [ ] 7.6 Ensure all automated tests pass.
  - [ ] 7.7 Update `README.md` (full setup, schema, design, assumptions, API examples).
  - [ ] 7.8 Implement comprehensive error handling and logging. 