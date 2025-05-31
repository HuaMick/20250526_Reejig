# O*NET Data Pipeline & Skill Gap API

## 1. Project Overview

This project implements an end-to-end data pipeline and RESTful API as outlined in the [Product Requirements Document](docs/prd-onet-data-pipeline.md). The system extracts occupational data from the public O*NET dataset (text files and supplementary API calls), processes and stores relevant information in a MySQL relational database, enriches skill data with AI-driven proficiency levels, and exposes a "skill gap" analysis feature via an API. This API allows a comparison of two occupations to identify skills present in a target occupation that are missing or at a lower proficiency level in a source occupation.

The primary goal is to provide a robust and scalable tool for HR software, career planning, employee development, and talent management.

## 2. Meeting the Requirements

This project directly addresses the criteria outlined in the [Take Home Assignment Requirements](docs/requirements.md):

### 2.1. Database Design
*   **Requirement:** Design a relational schema using MySQL.
*   **Implementation:** A normalized relational database schema has been designed and implemented in MySQL. Key tables include `Occupations`, `Skills`, `Scales`, and `Occupation_Skills` to store O*NET data. An additional table, `LlmSkillAssessments`, is designed to store detailed outputs from the LLM skill proficiency analysis. SQLAlchemy is used for schema definition and management, allowing for easier migrations and modifications.

### 2.2. ETL Pipeline
*   **Requirement:** Implement a script to populate the database via an ETL pipeline.
*   **Implementation:** A Python-based ETL pipeline has been developed.
    *   **Extraction:** Data is extracted from provided O*NET text files (`Occupation.txt`, `Skills.txt`, `Scales.txt`). The O*NET API is also used on-demand to supplement data not found in the local database, particularly for the `/skill-gap` API functionality.
    *   **Transformation:** Data is cleaned, and relationships are established. A significant transformation step involves using a Large Language Model (LLM) to assess and assign proficiency levels to skills for specific occupations, focusing on the 'LV' (Level) scale.
    *   **Loading:** Transformed data is loaded into the MySQL database. The ETL process is designed to be runnable via scripts and aims for idempotency for development and testing.

### 2.3. REST API Implementation
*   **Requirement:** Implement a REST endpoint `GET /skill-gap?from={occupation_code1}&to={occupation_code2}` that compares two occupations and returns the skills required by the second occupation that are not present in the first (or are at a lower proficiency).
*   **Implementation:** A RESTful API endpoint `GET /skill-gap` has been implemented using Python (e.g., FastAPI/Flask).
    *   It accepts `from` and `to` O*NET-SOC occupation codes as query parameters.
    *   It retrieves skill data (including LLM-refined proficiency levels for the 'LV' scale) for both occupations.
    *   It identifies skill gaps based on:
        1.  Skills present in the target occupation but not the source.
        2.  Skills present in both, but where the proficiency level in the target occupation is higher.
    *   The API returns a structured JSON response detailing these gaps, as specified in the PRD.

### 2.4. Technical Requirements
*   **Python:** The ETL pipeline and API are developed in Python.
*   **Docker:** All services (MySQL database, ETL scripts, API service) are containerized using Docker.
*   **Docker Compose:** Docker Compose is used to orchestrate the services, allowing the entire stack to be run with a single `docker-compose up` command.

## 3. Key Design Decisions & Project Evolution

The project evolved through several stages, with key design decisions made along the way (reflecting insights from `docs/design.md`):

*   **Initial Setup:** Opted for a standard Python virtual environment and `requirements.txt` over Nix for broader compatibility. Initial data sources were local O*NET `.txt` files.
*   **Database:**
    *   MySQL was chosen as the RDBMS, running within a Docker container for ease of setup and consistency.
    *   SQLAlchemy was adopted for schema definition and management, providing flexibility for schema evolution.
*   **ETL Development:**
    *   Started with basic extraction and loading, then refactored into modular functions and nodes (e.g., `extract_load_text_files.py`, `transform.py`) for better organization and reusability.
    *   Recognized the importance of 'scales' (like 'Level') in differentiating skill requirements for occupations that might share skill names.
    *   Handled data edge cases, such as occupations with no initial skill records.
*   **O*NET API Integration Strategy:**
    *   Initially explored bulk data fetching from the O*NET API but encountered challenges with pagination and the volume of calls required.
    *   Shifted to an **on-demand pull strategy**: The system primarily relies on the locally stored data (from text files and previous API pulls). If the `/skill-gap` API requests data for an occupation not present or fully detailed in the local database, it then queries the O*NET API in real-time. This approach balances data comprehensiveness with API usage efficiency. Fetched API data can be cached/stored for future requests.
*   **LLM Integration for Skill Proficiency:**
    *   Integrated a Large Language Model (Gemini) to analyze skills within the context of specific occupations and assign proficiency levels (0-7 for the 'LV' scale).
    *   This involved designing prompts to elicit structured JSON output from the LLM, detailing the skill, assigned proficiency, and justification. This significantly enriches the dataset beyond raw O*NET values.
*   **Testing:** Implemented integration tests throughout the development process to ensure reliability of individual components and the overall pipeline.

## 4. Database Schema Overview

The core database schema includes:

*   **`Occupations`**: Stores O*NET-SOC Code, Title, Description from `Occupation.txt`.
*   **`Skills`**: Stores Element ID, Element Name from `Skills.txt`.
*   **`Scales`**: Stores Scale ID, Scale Name, Min/Max from `Scales.txt`.
*   **`Occupation_Skills`**: A join table linking occupations to skills, including `Scale ID` and `Data Value` (proficiency). The `Data Value` for 'LV' scale skills is notably enriched by the LLM.
*   **`LlmSkillAssessments` (Recommended)**: A table to store the complete JSON response from the LLM for each skill proficiency assessment, useful for auditing and deeper analysis.

*(Refer to `src/config/schemas.py` for detailed SQLAlchemy models)*

## 5. API Endpoint: `GET /skill-gap`

*   **Endpoint:** `GET /skill-gap`
*   **Parameters:**
    *   `from` (string, required): O*NET-SOC Code of the source occupation.
    *   `to` (string, required): O*NET-SOC Code of the target occupation.
*   **Description:** Compares two occupations based on their 'LV' (Level) scale skills (with LLM-refined proficiency) and returns a list of skills that represent a gap.
*   **Success Response (200 OK Example from PRD):**
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
*   **Error Handling:** Includes `404 Not Found` for invalid occupation codes and `400 Bad Request` for missing parameters, as detailed in the PRD.

## 6. Setup and Execution

1.  **Prerequisites:**
    *   Docker
    *   Docker Compose
2.  **Environment Variables:**
    *   Ensure an `env/env.env` file is configured with necessary variables (e.g., database credentials, API keys for O*NET if rate limits are a concern for extensive use, LLM API key). Example:
        ```env
        MYSQL_USER=youruser
        MYSQL_PASSWORD=yourpassword
        MYSQL_DATABASE=onet_data
        MYSQL_HOST=mysql_db
        # Add other necessary API keys if any
        GEMINI_API_KEY=your_gemini_api_key
        ```
3.  **Build and Run:**
    *   Navigate to the project root directory.
    *   Execute: `docker-compose up --build`
    *   This command will:
        *   Build the Docker images for the API service and any ETL/worker services.
        *   Start the MySQL database container.
        *   Start the API service.
        *   Run any initial ETL scripts defined as services in `docker-compose.yml`.
4.  **Initial Data Load (if applicable as a separate step):**
    *   If the main ETL process is a separate script/node, it might be run via:
        `docker-compose run etl_service_name` (replace `etl_service_name` with the actual service name in `docker-compose.yml`).
5.  **Accessing the API:**
    *   Once services are running, the API should be accessible (e.g., `http://localhost:8000/skill-gap?from=...&to=...` - port may vary based on `docker-compose.yml` configuration).

## 7. Assumptions Made

*   The provided O*NET text files (`Occupation.txt`, `Skills.txt`, `Scales.txt`) are available and form the baseline dataset.
*   The O*NET API is accessible for supplementary data fetching.
*   An API key for the chosen LLM (e.g., Google Gemini) is available and configured for skill proficiency assessment.
*   The primary focus for skill gap analysis is the 'LV' (Level) scale.

## 8. Meeting Evaluation Criteria & Bonus Points

*   **Clean, Modular, Maintainable Code:** Efforts were made to structure the code into functions and nodes, promoting modularity. Python best practices were followed.
*   **Well-Structured, Normalized Schema:** The database schema is designed with normalization in mind, using SQLAlchemy for clear definitions and relationships.
*   **API Returns Accurate Skill Gap Results:** The API logic is designed to accurately identify skill gaps based on presence and proficiency levels, enhanced by LLM insights.
*   **Ease of Setup and Clear Instructions:** This README and Docker Compose aim to provide straightforward setup.
*   **Error Handling and Logging:** Basic error handling is implemented in the API, and logging considerations are noted in the PRD (though full implementation depth may vary).

*   **Bonus Point: Automated Tests:** Integration tests have been developed for key components of the ETL pipeline and potentially for API endpoints, ensuring reliability.
*   **Bonus Point: LLM to Extract Skill Proficiency:** A core feature of this project is the integration of an LLM to determine and refine skill proficiency levels, adding significant value to the skill gap analysis.

---
This project aims to deliver a functional and robust solution to the take-home assignment, demonstrating skills in data engineering, API development, and modern AI integration.
