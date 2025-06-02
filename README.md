# O*NET Data Pipeline & Skill Gap API

## Setup and Run Instructions
From project root execute in shell:
- `source env/env.env` Set env variables, see env.example
- `docker compose up`  Build and execute docker containers

docker compose has 4 services:
- db: the mysql database
- etl: loads the O*NET data then transforms the data into normalized tables
- test_runner: executes an automated test suite
- api: serves the api endpoints

Note: this project uses shell scripts, depending on your OS you may need to grant permissions to execute each shell script before your able to execute it. e.g. `chmod +x tests/test_suite/setup_test_db.sh` for Linux/macOS systems.

## Local Setup
- `sudo apt install pipx` : https://pipx.pypa.io/stable/installation/
- `pipx install virtualenv` : https://virtualenv.pypa.io/en/latest/installation.html
- `src/scripts/init_project.sh` : setup virtual env and install requirements
- `source env/env.env` : this will set your env variables
- `source .venv/bin/activate` : activate your python venv
- `docker compose up db`: this will spin up the db in a docker container
- `src/scripts/init_db.sh` : this will ensure the db is built and setup with the correct tables

## Execute automated tests locally:
From project root:
- `source env/env.env` : this will set your env variables
- `source .venv/bin/activate` : activate your python venv
- `docker compose up db`: this will spin up the db in a docker container
- `tests/test_suite/setup_test_db.sh`: this will initalise the test db with the correct tables
- `tests/test_suite/run_test_suite_using_sh.sh`: this will run the test suite.

## Project Overview
API that uses the public O*NET dataset to identify skills gap between two occupations (from_occupation, to_occupation).

For local deployment base_url = `http://localhost:8000`

API Endpoints:
- `<base_url>/health`: api health check
- `<base_url>/api/v1/skill-gap`: provide skills in to_occupation that are proficency level 0 in from_occupation
- `<base_url>/api/v1/skill-gap-by-lvl`: provide skills in to_occupation that are proficency level > from_occupation
- `<base_url>/api/v1/skill-gap-llm`: uses a large language model to determine proficiency levels, skills in to_occupation that are proficency level > from_occupation are then passed to the large language model again to provide a description/analysis of the skill gap.

Notes:
- If the occupation cannot be found the api will execute a request to onet api services to see if it can fetch the data.
- For now the api key is hardcoded and fetched from env variables on deployment. This should be updated before going live.

example request, for more examples see `notebook.ipynb`:
```python
base_url = "http://localhost:8000"
headers = {
    "X-API-Key": API_KEY
}

from_occupation = "11-1011.00"  # Web Developers
to_occupation = "11-3013.00"    # Computer Systems Analysts

response = requests.get(
    f"{base_url}/api/v1/skill-gap",
    params={"from_occupation": from_occupation, "to_occupation": to_occupation},
    headers=headers
)
print("\nBasic Skill Gap:")
pprint.pprint(response.json())
```

## Meeting the Requirements
Requirements can be found here [Take Home Assignment Requirements](docs/requirements.md)

### Database Design
*   **Requirement:** Design a relational schema using MySQL.
*   **Implementation:** Full schema details can be found: `src/config/schemas.py`

Landing tables for the Onet data include `Occupations_Landing`, `Onet_Skills_Landing`, `Onet_Scales_Landing`. etl normalizes the data from the landing tables to `Occupation_Skills` and `Skills`, `Occupations_Landing` was already normalized so has no downstream tables.
There are also `..._API_landing` landing tables for storing data when an api request is made to Onet also setup placeholder LLM landing tables to store request and reply data from the llm, atm llm request and prompt data is stored in `src/functions/llm_debug_responses`.

### ETL Pipeline
*   **Requirement:** Implement a script to populate the database via an ETL pipeline.
*   **Implementation:** An ETL process, containerized in the `etl` Docker service, handles data processing.
    *   Initial data load from O*NET text files (`Occupations.txt`, `Skills.txt`) is managed by scripts in `src/functions/` (e.g., `extract_onet_data.py`, `mysql_load_dataframe.py`) and orchestrated by the `src/nodes/extract_load.py` node.
    *   Normalization into `Skills` and `Occupation_Skills` tables is handled by the `src/nodes/transform.py` node, using functions like `populate_skills_reference.py`.
    *   On-demand data fetching from the O*NET API (if data is not in the local DB) is also part of the data strategy, with results cached locally.

### REST API Implementation
*   **Requirement:** Implement a REST endpoint `GET /skill-gap?from={occupation_code1}&to={occupation_code2}`.
*   **Implementation:** A FastAPI application (`src/api/main.py`) serves the API endpoints.
    *   `GET /api/v1/skill-gap`: Compares two occupations, returning skills in the target occupation not present (or at proficiency 0) in the source.
    *   `GET /api/v1/skill-gap-by-lvl`: Provides a more detailed comparison, showing skills where the target occupation requires a higher proficiency level.
    *   The API leverages functions like `get_occupation_and_skills.py` (with API fallback) and `identify_skill_gap.py`.

### Technical Stack & Setup
*   **Requirement:** Use Python, Docker, and Docker Compose for a single `docker-compose up` execution.
*   **Implementation:**
    *   Python is used for all ETL scripts (`src/functions/`, `src/nodes/`) and the FastAPI application (`src/api/`).
    *   Services (`db`, `etl`, `api`, `test_runner`) are containerized using `Dockerfile.api`, `Dockerfile.etl`, etc.
    *   `docker-compose.yml` orchestrates all services, enabling setup with a single `docker-compose up` command.

### Bonus Features
*   **Automated Tests:**
    *   **Implementation:** A comprehensive suite of integration tests (`tests/test_suite/`) validates individual components and end-to-end functionality. Tests are executed via shell scripts (e.g., `run_test_suite_using_sh.sh`) within a dedicated test environment managed by `docker-compose`.
*   **LLM for Skill Proficiency & Gap Analysis:**
    *   **Implementation:** Google's Gemini LLM is used to:
        1.  Derive skill proficiency levels for occupations (`src/functions/llm_skill_profiler.py`).
        2.  Provide qualitative descriptions for identified skill gaps via the `GET /api/v1/skill-gap-llm` endpoint (`src/functions/get_skills_gap_by_lvl_llm.py`).

## 3. Design Decisions & Project Evolution

This project was build using AI-assisted agentic programing techniques. Core to this is the `docs/prd-onet-data-pipeline.md`, `docs/tasks-prd-onet-data-pipeline.md` and `.cursor/rules` which were all used as context for the AI agent. An iterative approach to AI coding was taken, building function by function and extensively testing using integration tests each time.

The project evolved through several key design decisions:
*   **Initial Setup & ETL:** Opted for a standard Python virtual environment and `requirements.txt` over Nix. Data from O*NET text files was initially loaded into a Dockerized MySQL database using SQLAlchemy for schema management. This established the foundational ETL pipeline.
*   **API Integration & Data Strategy:** Encountering limitations with bulk API data (20 records/page), the strategy shifted from bulk extraction to an on-demand "pull" mechanism. If data isn't in the local database, it's fetched via the O*NET API, served to the user, and then cached locally. We can load the txt files as a base of data and then supplement it with the API. This balances API usage with responsiveness.
*   **Normalization & Data Modeling:** Downstream tables (`Skills`, `Occupation_Skills`) were created to normalize raw data, improving data integrity and query efficiency for skill gap analysis.
*   **Skill Gap Logic:** Analysis revealed that skill proficiency levels (LV scale) are crucial for meaningful skill gap identification, as occupations all have the same 35 skills unless we filter out where proficiency lvl is 0.
*   **Skill Gap Logic using lvl:** Felt the base skill gap wasn't very value add, so added one that allowed the comparison of lvl.
*   **Skill Gap Logic using LLM:** Requirements requested we derive proficiency lvl using the LLM, this was implemented, but we also extended it to use the derived lvl for from and to to generate gap descriptions. LLM used here was Google's Gemini.
*   **Testing:** A dedicated test environment and a suite of integration tests were established. Due to issues with `pytest` running the full suite, a shell script executing individual test scripts sequentially was implemented.

For a detailed log of design decisions, please see `docs/design.md`.
You may also find insights in project tasks, see implementation notes, refer to `docs/tasks-prd-onet-data-pipeline.md`.

### Out of Scope / Future Considerations

While the core requirements were met, the following areas were identified as out of scope for the current implementation or earmarked for future development if time permitted:

*   **Cloud Deployment (Phase 9 - Optional):** Full deployment to a cloud environment (e.g., GCP Cloud Run) including CI/CD pipeline setup, monitoring, and alerting was considered optional and not implemented. Would of been nice to deploy this and have an actual end point we could hit, however deploying mysql to cloud required a lot of infastructure setup, and would require another night of work. Decided time would be better spend on testing and ensureing kk is able to clone this and run it on his machine smoothly.

*   **API Data Normalization Pipeline (Phase 10 - Out of Scope):** Would be good to have ETL pipeline pull the fetched data from the api though to the normalized tables. In reality I would wait for further feedback before implementing this, given this is most akin to a POC. Also doing this doesn't really demonstrate any additional skills that I havn't shown already.

