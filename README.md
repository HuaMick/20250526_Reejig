# O*NET Data Pipeline & Skill Gap API

## Setup and Run Instructions

From project root execute in shell: 
  1. `source env/env.env` Set env variables, see env.example
  2. `docker compose up`  Build and execute docker containers

docker compose has 4 services:
db: the mysql database
etl: loads the O*NET data then transforms the data into normalized tables
test_runner: executes an automated test suite
api: serves the api endpoints

Note: this project uses shell scripts, depending on your OS you may need to grant permissions to execute each shell script before your able to execute it. e.g. `chmod +x tests/test_suite/setup_test_db.sh` for Linux/macOS systems.

## Execute automated tests:

From project root: 
1. `tests/test_suite/setup_test_db.sh`
2. `tests/test_suite/run_test_suite.sh`

## Project Overview

API that uses the public O*NET dataset to identify skills gap between two occupations (from_occupation, to_occupation).

For local deployment base_url = http://localhost:8000

API Endpoints:
<base_url>/health: api health check
<base_url>/api/v1/skill-gap: provide skills in to_occupation that are proficency level 0 in from_occupation 
<base_url>/api/v1/skill-gap-by-lvl: provide skills in to_occupation that are proficency level > from_occupation
<base_url>/api/v1/skill-gap-llm: uses a large language model to determine proficiency levels, skills in to_occupation that are proficency level > from_occupation are then passed to the large language model again to provide a description/analysis of the skill gap.

## Meeting the Requirements
Requirements can be found here [Take Home Assignment Requirements](docs/requirements.md)

### 2.1. Database Design
*   **Requirement:** Design a relational schema using MySQL.
*   **Implementation:** Full schema details can be found: src/config/schemas.py

Landing tables for the Onet data include `Occupations_Landing`, `Onet_Skills_Landing`, `Onet_Scales_Landing`. etl normalizes the data from the landing tables to `Occupation_Skills` and `Skills`, `Occupations_Landing` was already normalized has no downstream tables.
There are also `..._API_landing` landing tables for storing data when an api request is made to Onet and LLM landing tables to store request and reply data from the llm.

## 3. Design Decisions & Project Evolution

This project was build using AI-assisted agentic programing techniques. Core to this is the docs/prd-onet-data-pipeline.md and the docs/tasks-prd-onet-data-pipeline.md which was used to inform the AI models as well as prebuild .cursor/rules which were adapted from other projects.

The project evolved through several key design decisions:
*   **Initial Setup & ETL:** Opted for a standard Python virtual environment and `requirements.txt` over Nix. Data from O*NET text files was initially loaded into a Dockerized MySQL database using SQLAlchemy for schema management. This established the foundational ETL pipeline.
*   **API Integration & Data Strategy:** Encountering limitations with bulk API data (20 records/page), the strategy shifted from bulk extraction to an on-demand "pull" mechanism. If data isn't in the local database, it's fetched via the O*NET API, served to the user, and then cached locally. This balances API usage with responsiveness.
*   **Normalization & Data Modeling:** Downstream tables (`Skills`, `Occupation_Skills`) were created to normalize raw data, improving data integrity and query efficiency for skill gap analysis.
*   **Skill Gap Logic:** Analysis revealed that skill proficiency levels (LV scale) are crucial for meaningful skill gap identification, as many occupations share the same base skills. The API offers endpoints for both a basic skill gap (skills present in target, absent in source) and a more nuanced gap by proficiency level.
*   **LLM Integration:** To meet bonus requirements, Google's Gemini LLM was integrated to assess skill proficiencies and provide descriptive analysis of skill gaps, offering richer insights.
*   **Testing:** A dedicated test environment and a suite of integration tests were established. Due to issues with `pytest` running the full suite, a shell script executing individual test scripts sequentially was implemented.

For a detailed log of design decisions, please see [docs/design.md](docs/design.md).
You may also find insights in project tasks, see implementation notes, refer to [docs/tasks-prd-onet-data-pipeline.md](docs/tasks-prd-onet-data-pipeline.md).

### Out of Scope / Future Considerations

While the core requirements were met, the following areas were identified as out of scope for the current implementation or earmarked for future development if time permitted:

*   **Cloud Deployment (Phase 9 - Optional):** Full deployment to a cloud environment (e.g., GCP Cloud Run) including CI/CD pipeline setup, monitoring, and alerting was considered optional and not implemented.
*   **API Data Normalization Pipeline (Phase 10 - Out of Scope):** A dedicated ETL pipeline to normalize data fetched on-demand from the O*NET API into the core database tables was marked as out of scope. Currently, API-fetched data is cached in landing tables but not fully integrated into the normalized schema through an automated pipeline. This was deferred as the on-demand fetching with caching met immediate needs, and further product design input would be beneficial for a full normalization pipeline.

