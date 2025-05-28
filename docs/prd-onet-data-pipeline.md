# Product Requirements Document: O*NET Data Pipeline & Skill Gap API

## 1. Introduction/Overview

This document outlines the requirements for an end-to-end data pipeline and RESTful API. The system will extract occupational data from the public O*NET dataset, process and store relevant information in a MySQL relational database, and expose a "skill gap" analysis feature via an API. This API will allow HR software to compare two occupations and identify skills present in the target occupation that are missing or at a lower proficiency level in the source occupation. The project aims to provide a valuable tool for career planning, employee development, and talent management.

**Goal:** To develop a robust and scalable data pipeline that ingests O*NET data (occupations, skills, and scales), enriches it using an LLM for skill proficiency, and serves skill gap analyses through a REST API.

## 2. Goals

*   **G1:** Successfully extract data from O*NET's `Occupation.txt`, `Skills.txt`, and `Scales.txt`.
*   **G2:** Design and implement a normalized relational database schema in MySQL to store the extracted and processed data.
*   **G3:** Develop an ETL (Extract, Transform, Load) pipeline that:
    *   Populates the database with occupation, skill, and scale information.
    *   Integrates an LLM to determine/refine skill proficiency levels (specifically for the 'LV' - Level scale) for each occupation-skill pairing and store this in the `Occupation_Skills` table.
*   **G4:** Implement a RESTful API endpoint `GET /skill-gap?from={occupation_code1}&to={occupation_code2}`.
*   **G5:** The API endpoint must compare two occupations based on their 'LV' (Level) scale skills and return a list of skills that represent a gap (skills in the target occupation not present or at a lower proficiency in the source occupation).
*   **G6:** Containerize all services (ETL script, API, MySQL database) using Docker and manage them with Docker Compose for easy setup and execution (`docker-compose up`).
*   **G7:** Ensure clean, modular, maintainable code with appropriate error handling and logging.
*   **G8:** Include automated tests for key components.

## 3. User Stories

*   **US1 (API Consumer - HR Software):** As an HR software system, I want to call the `/skill-gap` API with two occupation codes so that I can retrieve a list of skills (including their names, IDs, and proficiency differences) required for the target occupation that the source occupation lacks or has at a lower level, enabling me to guide employee development or assess candidate suitability.
*   **US2 (Data Engineer):** As a Data Engineer, I want the ETL process to be idempotent and robust, correctly handling data extraction, transformation (including LLM-based proficiency scoring), and loading, so that the database is reliably populated with accurate O*NET data.
*   **US3 (Data Engineer):** As a Data Engineer, I want the system to be containerized using Docker and Docker Compose, so that setup and deployment are streamlined and consistent across environments.
*   **US4 (Developer):** As a developer maintaining the system, I want clear error messages and logging from the API and ETL process, so that I can troubleshoot issues effectively.

## 4. Functional Requirements

### 4.1. Data Extraction
*   **FR1.1:** The system must download or use local copies of `Occupation Data (Occupation.txt)`, `Skills (Skills.txt)`, and `Scales (Scales.txt)` from the O*NET website/provided files.
*   **FR1.2:** All fields from these files must be parsed and made available for transformation and loading.

### 4.2. Database
*   **FR2.1:** A relational database (MySQL) must be used.
*   **FR2.2:** The schema must include at least the following tables:
    *   `Occupations`: Stores O*NET-SOC Code, Title, Description, and other relevant fields from `Occupation.txt`.
    *   `Skills`: Stores Element ID, Element Name, and other relevant fields from `Skills.txt`, representing unique skills.
    *   `Scales`: Stores Scale ID, Scale Name, Minimum, Maximum from `Scales.txt`.
    *   `Occupation_Skills`: A join table storing the relationship between occupations and skills, including `O*NET-SOC Code`, `Element ID`, `Scale ID`, and `Data Value` (proficiency level).
*   **FR2.3:** Primary keys, foreign keys, and appropriate indexes must be defined to ensure data integrity and query performance.

### 4.3. ETL Pipeline
*   **FR3.1:** The ETL script must populate the `Occupations`, `Skills`, and `Scales` tables from the respective source files.
*   **FR3.2:** The ETL script must populate the `Occupation_Skills` table by associating occupations with all their listed skills from `Skills.txt`.
*   **FR3.3:** **LLM Integration for Skill Proficiency:**
    *   For each occupation-skill pair, and specifically for skills measured on the 'LV' (Level) scale, an LLM must be used to analyze the skill in the context of the occupation.
    *   The LLM will output a `Data Value` (proficiency level, 0-7 for 'LV' scale) for the skill in that occupation.
    *   This LLM-derived `Data Value` must be stored in the `Occupation_Skills` table for the corresponding `O*NET-SOC Code`, `Element ID`, and `Scale ID` ('LV').
*   **FR3.4:** The ETL process should be runnable as a script and clear existing data (for these tables) before loading new data to ensure idempotency for development/testing.

### 4.4. REST API
*   **FR4.1:** Implement `GET /skill-gap` endpoint.
    *   Parameters: `from` (O*NET-SOC Code of source occupation), `to` (O*NET-SOC Code of target occupation).
*   **FR4.2:** The endpoint must use the `identify_skill_gap` logic (or similar, based on `src/functions/identify_skill_gap.py`):
    *   Retrieve 'LV' scale skill proficiency data for both occupations from the `Occupation_Skills` table (populated by ETL, including LLM refinement).
    *   A skill gap exists if:
        1.  A skill (Element ID) with `Scale ID` 'LV' is associated with the `to` occupation but not the `from` occupation.
        2.  A skill (Element ID) with `Scale ID` 'LV' is associated with both, but the `Data Value` for the `to` occupation is higher than for the `from` occupation.
*   **FR4.3:** API Response (Success - 200 OK):
    ```json
    {
      "success": true,
      "message": "Successfully identified skill gap from '[From Occupation Title]' to '[To Occupation Title]' based on 'LV' scale.",
      "result": {
        "from_occupation_title": "[From Occupation Title]",
        "to_occupation_title": "[To Occupation Title]",
        "skill_gaps": [
          {
            "element_id": "string",
            "element_name": "string",
            "scale_id": "LV",
            "from_data_value": "decimal (0.0 - 7.0, or 0 if not in 'from' occupation)",
            "to_data_value": "decimal (0.0 - 7.0)"
          }
          // ... more skills
        ]
      }
    }
    ```
*   **FR4.4:** API Error Handling:
    *   `404 Not Found`: If `from` or `to` occupation code is not found in the database. Response: `{"success": false, "message": "Error: Occupation code [code] not found.", "result": {"skill_gaps": [], ...}}`
    *   `400 Bad Request`: If `from` or `to` parameters are missing. Response: `{"success": false, "message": "Error: Missing 'from' or 'to' occupation code parameter.", "result": {"skill_gaps": [], ...}}`
    *   `500 Internal Server Error`: For any other unexpected server-side errors. Response: `{"success": false, "message": "An internal server error occurred.", "result": {"skill_gaps": [], ...}}`

### 4.5. Technical Requirements (from original assignment)
*   **FR5.1:** Use Python for ETL and API.
*   **FR5.2:** Use Docker to containerize services (MySQL, ETL script execution environment, API service).
*   **FR5.3:** Use Docker Compose to orchestrate the services. A single `docker-compose up` should start all necessary services.

## 5. Non-Goals (Out of Scope for MVP)

*   **NG1:** User interface/frontend for interacting with the API (API is for HR software consumption).
*   **NG2:** Authentication/Authorization for the API (can be added later if needed).
*   **NG3:** Support for skill gap analysis using scales other than 'LV' (Level).
*   **NG4:** Real-time updates to the O*NET data; the pipeline will run on a static dataset version.
*   **NG5:** Advanced analytics or visualizations on top of the skill gap data.

## 6. Design Considerations (Optional)

*   The existing `src/functions/identify_skill_gap.py` provides a strong foundation for the core logic.
*   The API should be stateless.
*   Consider using a lightweight Python web framework for the API (e.g., FastAPI, Flask).
*   Logging should be implemented for both the ETL process and API requests/responses.

## 7. Technical Considerations (Optional)

*   **LLM Choice:** A suitable pre-trained language model (e.g., from Hugging Face) should be chosen for skill proficiency analysis. Consider models fine-tuned for text understanding or semantic similarity. The LLM interaction will likely involve crafting prompts that provide the occupation title/description and the skill name/description, asking the LLM to output a proficiency score on the 0-7 'LV' scale.
*   **ETL Orchestration:** For simplicity, the ETL might be a single script run via `docker-compose run etl_service`. For more complex scenarios, a workflow orchestrator could be considered in the future.
*   **Database Connection Pooling:** For the API, ensure efficient database connection management.

## 8. Success Metrics

*   **SM1:** API endpoint `/skill-gap` returns accurate skill gap information as per FR4.2 and FR4.3.
*   **SM2:** ETL pipeline successfully ingests all data from `Occupation.txt`, `Skills.txt`, and `Scales.txt`, and correctly populates the `Occupation_Skills` table including LLM-derived 'LV' scale proficiency values.
*   **SM3:** All services run correctly with `docker-compose up`.
*   **SM4:** Automated tests pass for critical components (e.g., ETL data validation, API endpoint testing).
*   **SM5 (Bonus):** The LLM integration demonstrably improves the quality/granularity of skill proficiency data compared to using raw O*NET values or defaults.

## 9. Open Questions

*   **OQ1:** What is the expected frequency of ETL runs? (For now, assumed to be manual/on-demand for a static dataset).
*   **OQ2:** Are there specific performance requirements for the API (e.g., response time under X ms)? (For now, aim for reasonable performance).
*   **OQ3:** What specific pre-trained LLM will be used? What is the strategy if the chosen LLM has API rate limits or costs that need to be managed for batch processing all occupation-skill pairs?

---
This PRD provides the initial requirements. It is expected to be a living document and may be updated as the project progresses. 