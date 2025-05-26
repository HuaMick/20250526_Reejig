# Memory Bank Notes

<!-- ============================================ -->
<!-- DO NOT DELETE THIS SECTION - AGENT WARNING -->
<!-- ============================================ -->

## Description

Memory bank notes work as the working memory of agents.

<!-- ============================================ -->
<!-- END OF PROTECTED SECTION - DO NOT DELETE   -->
<!-- ============================================ -->

## Notes

### Project Setup and Database Initialization (as of 2025-05-26)

**1. Environment Setup:**
   - Configured `env/env.env` for database credentials (`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`).

**2. Docker Compose for MySQL:**
   - Created `docker-compose.yml` to run a MySQL 8.0 service (`db`).
   - Configured to use environment variables from `env/env.env` for MySQL setup (user, password, database name, root password).
   - Includes a healthcheck for the `db` service.
   - The `version` attribute was removed from `docker-compose.yml` as it's obsolete.
   - Created `scripts/docker_compose.sh` to source `env/env.env` and run `docker compose up`.

**3. SQLAlchemy Schema Definition:**
   - Created `src/config/schemas.py` defining the database tables (`Occupations`, `Skills`, `Occupation_Skills`) using SQLAlchemy models.
   - Includes relationships between models and uses `declarative_base` (updated to import from `sqlalchemy.orm`).

**4. Database Table Initialization Function:**
   - Implemented `src/functions/mysql_init_tables.py` with the `initialize_database_tables` function.
   - This function uses SQLAlchemy models from `src/config/schemas.py` to:
     - Connect to the MySQL database.
     - Drop all known tables (`Base.metadata.drop_all(engine)`).
     - Create all tables (`Base.metadata.create_all(engine)`).

**5. MySQL Connection Function:**
   - Created `src/functions/mysql_connection.py` with `get_mysql_connection` to establish and return a MySQL connection object using environment variables.

**6. Integration Tests:**
   - **MySQL Connection Test:**
     - `tests/test_integration_mysql_connection.py` and `tests/test_integration_mysql_connection.sh`.
     - Verifies that a connection can be made to the Dockerized MySQL instance using credentials from `env/env.env`.
     - Test script sources `env/env.env` and activates the `.venv` Python virtual environment.
   - **Table Initialization Test (SQLAlchemy):**
     - `tests/test_integration_mysql_init_tables.py` and `tests/test_integration_mysql_init_tables.sh`.
     - Runs the `initialize_database_tables` function.
     - Verifies that the expected tables (`Occupations`, `Skills`, `Occupation_Skills`) are created in the database by querying `SHOW TABLES;`.
     - Test script also sources `env/env.env` and activates `.venv`.

**7. Dependencies:**
   - Added `mysql-connector-python` and `python-dotenv` to `requirements.txt`.
   - Ensured SQLAlchemy (already present) is utilized for schema management.

**Troubleshooting Steps Taken:**
   - Corrected `docker compose` command (space vs. hyphen).
   - Ensured Python virtual environment activation in test scripts.
   - Fixed `pyproject.toml` syntax error.
   - Addressed MySQL access denied errors by ensuring consistent `MYSQL_DATABASE` env var and by rebuilding the Docker volume for MySQL (`docker compose down -v`) to re-initialize with correct, updated credentials.
   - Updated SQLAlchemy `declarative_base` import to resolve deprecation warnings.

**Next Steps (Identified from requirements.md):**
   - Implement ETL pipeline to populate the database.
   - Implement REST API for skill gap analysis.