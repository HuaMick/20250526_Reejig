## Relevant Files

- `src/config/schemas.py` - Defines SQLAlchemy models for database tables (`Occupations`, `Skills`, `Occupation_Skills`, `Scales`).
- `src/functions/mysql_init_tables.py` - Initializes database tables using SQLAlchemy models.
- `src/functions/extract_onet_data.py` - Extracts data from O*NET `.txt` files (`Occupation.txt`, `Skills.txt`, `Scales.txt`) into pandas DataFrames.
- `src/functions/mysql_load.py` - Loads data from DataFrames into MySQL tables (`Occupations`, `Skills`, `Occupation_Skills`, `Scales`). Needs review for LLM integration.
- `src/functions/llm_skill_profiler.py` - **NEW:** To house the LLM interaction logic for skill proficiency scoring.
- `tests/test_llm_skill_profiler.py` - **NEW:** Unit tests for `llm_skill_profiler.py`.
- `src/nodes/extract_load.py` - Orchestrates the initial data extraction and loading into the database.
- `src/nodes/enrich_skill_data.py` - **NEW:** Orchestrates the LLM enrichment of skill proficiency data in the `Occupation_Skills` table.
- `src/functions/get_occupation_skills.py` - Retrieves occupation skills data, needs to be updated to use `Occupation_Skills` table with LLM-derived 'LV' scale `data_value`.
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

- [x] 1.0 **Setup & Database Schema Finalization** (PRD G2, FR2)
  - [x] 1.1 Define environment variables for DB connection (`env/env.env`). (Covered in `memory_bank/notes.md`)
  - [x] 1.2 Update `src/config/schemas.py` with SQLAlchemy models for `Occupations`, `Skills`, `Occupation_Skills`, and `Scales` tables, ensuring all fields from PRD (FR2.2) are included (e.g., `onet_soc_code`, `title`, `description` for `Occupations`; `element_id`, `element_name` for `Skills`; `scale_id`, `scale_name`, `minimum`, `maximum` for `Scales`; `onet_soc_code`, `element_id`, `scale_id`, `data_value` for `Occupation_Skills`). (Covered in `memory_bank/notes.md`, `Scales` table confirmed)
  - [x] 1.3 Implement `src/functions/mysql_init_tables.py` to create/recreate tables based on schemas. (Covered in `memory_bank/notes.md`)
  - [ ] 1.4 Ensure primary keys, foreign keys, and necessary indexes are correctly defined in `src/config/schemas.py` (PRD FR2.3).
  - [x] 1.5 Create integration test for table initialization (e.g., `tests/test_integration_mysql_init_tables.py`). (Covered in `memory_bank/notes.md`)

- [ ] 2.0 **ETL Pipeline Implementation: Data Extraction & Basic Load** (PRD G1, G3 (partial), FR1, FR3.1, FR3.2, FR3.4)
  - [x] 2.1 Implement `src/functions/extract_onet_data.py` to read `Occupation.txt`, `Skills.txt`, and `Scales.txt` into pandas DataFrames, performing necessary column renaming and basic type conversions (PRD FR1.1, FR1.2). (`extract_onet_data.py` exists and processes these files)
  - [x] 2.2 Implement/Update `src/functions/mysql_load.py` (`load_data_from_dataframe` function) to:
    - [x] Load data into `Occupations` table. (`mysql_load.py` and `extract_load.py` handle this)
    - [x] Load unique skills into `Skills` table. (`mysql_load.py` and `extract_load.py` handle this)
    - [x] Load data into `Scales` table. (`extract_load.py` handles this by calling `load_data_from_dataframe` for `scales.txt`)
    - [x] Load data into `Occupation_Skills` table from `Skills.txt` (associating occupations with skills, including `Scale ID` and `Data Value` as available in the source file). (`mysql_load.py` and `extract_load.py` handle this for `Occupation_Skills`)
    - [x] Ensure the function clears existing data before loading (PRD FR3.4). (`mysql_load.py` has `clear_existing` logic, default True, and `session.query(model).delete()`)
  - [x] 2.3 Update `src/nodes/extract_load.py` to orchestrate the extraction and loading of all three files (`Occupations`, `Skills`, `Scales`, and `Occupation_Skills`). (This node exists and handles these tables)
  - [x] 2.4 Create integration test for the basic ETL data loading process (e.g., `tests/test_integration_mysql_load.py`). (Covered in `memory_bank/notes.md`)

- [ ] 3.0 **ETL Pipeline Enhancement: LLM Integration for Skill Proficiency** (PRD G3 (LLM part), FR3.3)
  - [ ] 3.1 Research and select a suitable pre-trained LLM for analyzing skill proficiency (e.g., from Hugging Face, considering models for text understanding/semantic similarity). (PRD OQ3)
  - [ ] 3.2 Create `src/functions/llm_skill_profiler.py` with a function that takes occupation details (title/description) and skill details (name/description) and returns an 'LV' scale proficiency score (0-7) using the chosen LLM.
    - [ ] 3.2.1 Implement LLM API call/interaction logic.
    - [ ] 3.2.2 Implement prompt engineering to guide the LLM.
    - [ ] 3.2.3 Handle potential LLM errors or rate limits gracefully.
  - [ ] 3.3 Create unit tests for `src/functions/llm_skill_profiler.py` (e.g., `tests/test_llm_skill_profiler.py`), possibly mocking LLM calls.
  - [ ] 3.4 Create and implement the new `src/nodes/enrich_skill_data.py` node to:
    - [ ] After initial data load (Task 2.0), iterate through occupation-skill pairs in `Occupation_Skills` table that have `Scale ID` = 'LV'.
    - [ ] For each pair, call the function from `llm_skill_profiler.py` to get the LLM-derived `Data Value`.
    - [ ] Update the `Data Value` in the `Occupation_Skills` table with the LLM-derived score for these 'LV' scale entries.
  - [ ] 3.5 Create/Update integration tests for the ETL pipeline to verify LLM enrichment (e.g., check if `Data Value` for 'LV' skills in `Occupation_Skills` are updated).

- [ ] 4.0 **REST API Implementation: Skill Gap Endpoint** (PRD G4, G5, FR4)
  - [ ] 4.1 Choose and set up a Python web framework (e.g., FastAPI or Flask). Add to `requirements.txt`.
  - [ ] 4.2 Update `src/functions/get_occupation_skills.py`:
    - [ ] Query the `Occupation_Skills` table (instead of `Skills` table directly).
    - [ ] Filter for skills with `Scale ID` = 'LV'.
    - [ ] Retrieve the `Data Value` (proficiency) from `Occupation_Skills` (which now includes LLM-refined values).
    - [ ] Ensure function returns data in the format expected by `identify_skill_gap.py` (list of skill dicts with `element_id`, `element_name`, `data_value`).
    - [x] (Partial) Existing `get_occupation_skills.py` retrieves occupation title. (Needs update for skills part)
  - [ ] 4.3 Create/Update unit tests for `src/functions/get_occupation_skills.py`.
  - [x] 4.4 Review `src/functions/identify_skill_gap.py` to ensure it correctly processes input from the updated `get_occupation_skills.py` and matches PRD FR4.2. (Function exists and logic for 'LV' seems aligned, assumes correct input format)
  - [ ] 4.5 Create unit tests for `src/functions/identify_skill_gap.py` if not already sufficient.
  - [ ] 4.6 Create API main application file (e.g., `src/api/main.py`).
  - [ ] 4.7 Implement the `GET /skill-gap` endpoint in a router/controller (e.g., `src/api/routers/skill_gap.py`):
    - [ ] Takes `from` and `to` occupation codes as query parameters.
    - [ ] Calls `get_occupation_skills` for both occupation codes.
    - [ ] Passes the results to `identify_skill_gap`.
    - [ ] Formats the response according to PRD FR4.3 (success) and FR4.4 (errors: 404, 400, 500).
  - [ ] 4.8 Implement logging for API requests and responses (PRD G7).
  - [ ] 4.9 Create integration tests for the `/skill-gap` API endpoint (e.g., `tests/test_api_skill_gap.py`), covering success and error cases.

- [ ] 5.0 **Containerization, Testing, and Documentation** (PRD G6, G7, G8)
  - [x] 5.1 Update `docker-compose.yml`:
    - [x] Define MySQL service (already exists based on `memory_bank/notes.md`).
    - [ ] Define API service, using `Dockerfile.api`.
    - [ ] Define ETL service (if run as a separate containerized script using `Dockerfile.etl`) or ensure ETL can be run within the API container environment if preferred.
    - [x] Ensure services use environment variables from `env/env.env`. (Covered in `memory_bank/notes.md`)
  - [ ] 5.2 Create `Dockerfile.api` for the API service.
  - [ ] 5.3 Create `Dockerfile.etl` if the ETL process is a separate containerized service.
  - [x] 5.4 Ensure all necessary dependencies are in `requirements.txt`. (Partially done, will need new ones for API framework and LLM SDKs)
  - [ ] 5.5 Create/Update integration test shell scripts (`tests/test_integration_*.sh`) to run all tests within the Docker environment or against Dockerized services.
  - [ ] 5.6 Ensure all automated tests (unit and integration) pass (PRD G8, SM4).
  - [ ] 5.7 Update `README.md` with:
    - [x] Clear setup instructions using `docker-compose up`. (Partially covered by `scripts/docker_compose.sh` in notes, but main README needs it)
    - [ ] Description of schema and design choices (PRD Submission Requirements).
    - [ ] Assumptions made (PRD Submission Requirements).
    - [ ] Sample requests for testing the API (PRD Submission Requirements).
  - [ ] 5.8 Implement basic error handling and logging across components (PRD G7, Evaluation Criteria). 