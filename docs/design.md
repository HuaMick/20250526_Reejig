## Design Decisions
- Removed nix from the project template. For this porject will opt for the more standard virtual env and requirements.txt with pip.

- The two data files are not super large, so have saved them as txt files in the data folder for now. We can look at fetching this data dynamically at a later stage after we have poc up and running.

- Had gemini scan the files and recommend a schema for me. looks okay for now. Will review latter after we get the data into a db.

- For this project the MySQL instance can sit inside the docker container.

- Successfully implemented the MYSQL instance with integration tests passing on the connection.

- Will build the database schema using python SQL Alchemy, this will allow me to quickly revist the schema and rebuild it if needed.

## Project Plan

### 1. Project Setup
- Initialize project structure with Python virtual environment
- Create requirements.txt with necessary dependencies
- Set up Docker and Docker Compose configuration
- Create basic project documentation

### 2. Database Design & Implementation
- Design MySQL schema for:
  - Occupations table (O*NET occupation data)
  - Skills table (O*NET skills data)
  - Occupation-Skills relationship table
- Create database initialization scripts
- Set up database migrations

### 3. ETL Pipeline Development
- Create data download module for O*NET datasets
- Implement data extraction scripts for:
  - Occupation.txt
  - Skills.txt
- Develop data transformation logic
- Create data loading scripts into MySQL
- Add error handling and logging
- Implement data validation checks

### 4. REST API Development
- Set up FastAPI/Flask application structure
- Implement database connection layer
- Create API endpoints:
  - GET /skill-gap endpoint with query parameters
  - Health check endpoint
- Add input validation
- Implement error handling
- Add API documentation (Swagger/OpenAPI)

### 5. Docker Configuration
- Create Dockerfile for API service
- Create Dockerfile for ETL service
- Configure Docker Compose for:
  - MySQL database
  - API service
  - ETL service
- Set up networking between containers
- Configure volume mounts for data persistence

### 6. Testing
- Write unit tests for:
  - ETL pipeline
  - API endpoints
  - Database operations
- Create integration tests
- Set up CI pipeline (optional)

### 7. Documentation
- Create detailed README.md with:
  - Setup instructions
  - API documentation
  - Database schema documentation
  - Sample API requests
- Document assumptions and design decisions
- Add inline code documentation

### 8. Final Steps
- Code review and cleanup
- Performance optimization
- Security review
- Final testing in local environment
