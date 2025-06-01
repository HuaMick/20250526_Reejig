# O*NET Skills Gap API README

This document provides an overview of the O*NET Skills Gap API, its functionalities, and instructions for running and interacting with it. This API is a component of the larger O*NET Data Pipeline project.

## Table of Contents

- [Overview](#overview)
- [API Endpoints](#api-endpoints)
  - [Health Checks](#health-checks)
  - [Diagnostics](#diagnostics)
  - [Skill Gap Analysis](#skill-gap-analysis)
- [Running the API](#running-the-api)
  - [Locally](#locally)
  - [Using Docker](#using-docker)
- [Environment Variables](#environment-variables)
- [Error Handling](#error-handling)
- [API Project Structure](#api-project-structure)
- [Dependencies](#dependencies)
- [How to Interact (for Agents)](#how-to-interact-for-agents)
- [Contribution Guidelines](#contribution-guidelines)
- [License](#license)

## Overview

The O*NET Skills Gap API provides endpoints to:
1.  Perform health checks.
2.  Diagnose database connectivity and retrieve table information.
3.  Analyze skill gaps between two occupations based on O*NET data.

It is built using FastAPI and interacts with a MySQL database populated by the O*NET ETL processes.

## API Endpoints

All API endpoints are prefixed with `/api/v1`.

### Health Checks

-   `GET /`: Root endpoint for a basic health check.
    -   **Response:** `{"status": "healthy", "message": "O*NET Skills Gap API is running"}`
-   `GET /health`: Dedicated health check endpoint.
    -   **Response:** `{"status": "healthy"}`

### Diagnostics

-   `GET /db-diagnostics` (defined in `src/api/routers/db.py`):
    -   **Purpose:** Diagnoses the database connection and lists all tables along with their row counts.
    -   **Response (Success):**
        ```json
        {
            "status": "success",
            "message": "Database connection successful and tables listed.",
            "tables": [
                {"name": "table1_name", "rows": 100},
                {"name": "table2_name", "rows": 50}
            ]
        }
        ```
    -   **Response (Error):**
        ```json
        {
            "detail": "Database connection failed: <error_message>"
        }
        ```
        (Status Code: 500 or 503)

### Skill Gap Analysis

Defined in `src/api/routers/skill_gap.py`.

1.  `GET /skill-gap`:
    -   **Purpose:** Analyzes the basic skill gap, identifying skills present in the target occupation but missing in the source occupation.
    -   **Query Parameters:**
        -   `from_occupation` (string, required): Source O*NET-SOC code (e.g., '11-1011.00').
        -   `to_occupation` (string, required): Target O*NET-SOC code (e.g., '11-2021.00').
    -   **Response (Success):**
        ```json
        {
            "from_occupation": {
                "code": "11-1011.00",
                "title": "Chief Executives"
            },
            "to_occupation": {
                "code": "11-2021.00",
                "title": "Marketing Managers"
            },
            "skill_gaps": [
                "Skill Name 1",
                "Skill Name 2"
            ]
        }
        ```
    -   **Response (Error - e.g., occupation not found):**
        ```json
        {
            "detail": "Occupation with code 11-xxxx.xx not found."
        }
        ```
        (Status Code: 404)

2.  `GET /skill-gap-by-lvl`:
    -   **Purpose:** Analyzes detailed skill gaps, including proficiency levels. It identifies skills where the target occupation requires a higher proficiency level than the source occupation, or skills entirely missing from the source.
    -   **Query Parameters:**
        -   `from_occupation` (string, required): Source O*NET-SOC code.
        -   `to_occupation` (string, required): Target O*NET-SOC code.
    -   **Response (Success):**
        ```json
        {
            "from_occupation": {
                "code": "11-1011.00",
                "title": "Chief Executives"
            },
            "to_occupation": {
                "code": "11-2021.00",
                "title": "Marketing Managers"
            },
            "skill_gaps": [
                {
                    "skill_name": "Complex Problem Solving",
                    "element_id": "2.B.1.a",
                    "from_proficiency": 3.5,
                    "to_proficiency": 4.0
                },
                {
                    "skill_name": "New Skill Required",
                    "element_id": "2.C.3.b",
                    "from_proficiency": null, // or 0, depending on implementation
                    "to_proficiency": 3.0
                }
            ]
        }
        ```
    -   **Response (Error):** Similar to `/skill-gap`, with appropriate error messages and status codes (e.g., 404, 500).

## Running the API

### Locally

1.  **Prerequisites:**
    -   Python 3.10+
    -   MySQL server running and accessible.
    -   Required Python packages (see `requirements.txt`).
2.  **Environment Setup:**
    -   Ensure the `env/env.env` file is populated with the correct database credentials and API settings (see [Environment Variables](#environment-variables)).
3.  **Activate Virtual Environment:**
    ```bash
    source .venv/bin/activate 
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run the API:**
    The API is run using Uvicorn. From the project root directory:
    ```bash
    python src/api/main.py
    ```
    By default, it will run on `0.0.0.0:8000`. The host and port can be configured via environment variables `API_HOST` and `API_PORT`.

### Using Docker

The API can be run as a service using Docker Compose, which also manages the MySQL database and ETL services.

1.  **Prerequisites:**
    -   Docker and Docker Compose installed.
2.  **Environment Setup:**
    -   Ensure the `env/env.env` file is populated. The `docker-compose.yml` file references these variables.
3.  **Build and Run:**
    Navigate to the project root directory (where `docker-compose.yml` is located).
    The `src/scripts/docker_compose.sh` script sources the environment variables and starts the services:
    ```bash
    bash src/scripts/docker_compose.sh
    ```
    Alternatively, you can run Docker Compose directly:
    ```bash
    # Ensure environment variables from env/env.env are loaded into your shell
    # or define them directly for the command.
    docker compose up --build
    ```
    To run in detached mode:
    ```bash
    docker compose up --build -d
    ```
    The API service is named `api` in `docker-compose.yml` and will be accessible on port 8000 of the host machine by default.

## Environment Variables

The API relies on several environment variables, typically defined in `env/env.env`.

-   `MYSQL_HOST`: Hostname of the MySQL server.
-   `MYSQL_PORT`: Port of the MySQL server (default: 3306).
-   `MYSQL_USER`: MySQL username.
-   `MYSQL_PASSWORD`: MySQL password.
-   `MYSQL_DATABASE`: Name of the MySQL database.
-   `ONET_USERNAME`: (If used by underlying functions for on-demand API calls) O*NET API username.
-   `ONET_PASSWORD`: (If used by underlying functions for on-demand API calls) O*NET API password.
-   `API_HOST`: Host for the API server (default: `0.0.0.0`).
-   `API_PORT`: Port for the API server (default: `8000`).

## Error Handling

The API uses custom exception handlers defined in `src/config/api_exception_handles.py`.
-   Standard HTTP exceptions (e.g., 400, 404, 500) are returned with JSON bodies detailing the error.
-   Specific error types like `ValueError`, `TypeError`, `FileNotFoundError`, `ConnectionError` are mapped to appropriate HTTP status codes and messages.
-   Logging is implemented to record errors.

## API Project Structure

Key files and directories related to the API within the `src/` folder:

```
src/
├── api/
│   ├── main.py           # FastAPI application entry point
│   ├── README.md         # This file
│   └── routers/
│       ├── skill_gap.py  # Router for skill gap analysis endpoints
│       └── db.py         # Router for database diagnostic endpoints
├── config/
│   ├── api_exception_handles.py # Custom exception handling logic
│   └── schemas.py        # SQLAlchemy schemas (referenced by functions used by API)
├── functions/            # Contains business logic functions called by the API routers
│   ├── get_skills_gap.py
│   ├── get_skills_gap_by_lvl.py
│   └── mysql_connection.py
│   └── ... (other relevant functions)
└── scripts/
    └── docker_compose.sh # Script to run docker-compose with env vars
env/
└── env.env               # Environment variable definitions
```

## Dependencies

Major dependencies include:
-   FastAPI: For building the API.
-   Uvicorn: ASGI server to run FastAPI.
-   SQLAlchemy: For database interaction (via functions).
-   Pydantic: For data validation and settings management.
-   python-dotenv: For loading environment variables.

Refer to `requirements.txt` for a complete list of dependencies.

## How to Interact (for Agents)

When interacting with this API:

1.  **Base URL:** Assume the API is running and accessible. The base URL will typically be `http://localhost:8000/api/v1/` or the equivalent if deployed elsewhere.
2.  **Endpoints:** Utilize the endpoints described in the [API Endpoints](#api-endpoints) section.
3.  **Parameters:** Pay close attention to required query parameters like `from_occupation` and `to_occupation` for the skill gap endpoints. These are O*NET-SOC codes.
4.  **Responses:** Expect JSON responses. Successful responses will generally have a 2xx status code. Errors will have 4xx or 5xx status codes with a JSON body containing a "detail" field.
5.  **Idempotency:** `GET` requests are idempotent.
6.  **Error Handling:** If you receive a non-2xx response, parse the "detail" field from the JSON error response to understand the issue. Common issues might include invalid O*NET-SOC codes (404) or server-side problems (5xx).

**Example Agent Task:** "Find the skill gaps between a 'Software Developer' (15-1252.00) and a 'Data Scientist' (15-2051.00)."
-   **Action:** Send a `GET` request to `/api/v1/skill-gap?from_occupation=15-1252.00&to_occupation=15-2051.00`.
-   **Action (Detailed):** Send a `GET` request to `/api/v1/skill-gap-by-lvl?from_occupation=15-1252.00&to_occupation=15-2051.00`.

## Contribution Guidelines

(To be defined - e.g., code style, branch strategy, testing requirements)

## License

(To be defined - e.g., MIT, Apache 2.0)
