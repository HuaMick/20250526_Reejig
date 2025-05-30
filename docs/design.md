## Design Decisions
- Removed nix from the project template. For this porject will opt for the more standard virtual env and requirements.txt with pip.

- The two data files are not super large, so have saved them as txt files in the data folder for now. We can look at fetching this data dynamically at a later stage after we have poc up and running.

- Had gemini scan the files and recommend a schema for me. looks okay for now. Will review latter after we get the data into a db.

- For this project the MySQL instance can sit inside the docker container.

- Successfully implemented the MYSQL instance with integration tests passing on the connection.

- Will build the database schema using python SQL Alchemy, this will allow me to quickly revist the schema and rebuild it if needed.

- Added a extract and load node after passing all integration tests. 

- I've noticed the scales in testing. Roles such as chemist and software engineer seem to have the same skills, so will need to incorporate scales into the skills gap analysis.

- Testing showed that the data has some edges, some of the occupations dont have any records in the skills table. Will update the skills gap functions to call this out.

- I was able to get the skills gap working after some debugging. Now that I have this stage of the POC working its time to look back and rework the pipeline to meet more of the requirements.

- I've implemented a downstream normalization for skills table, this will allow me to land my data, and then have the normalized tables downstream.

- I've refactored the landing tables and loading to be more modular this should help when I start to pull data from the API, I've yet to recieve my API credentials yet so will wait for that.

- I've successfully extracted the occupations data using the API. I'll need to update schema and refactor the load pipeline. Once I've established I can successfully load I'll create the other functions to extract the other datasets via the API. 

- I've successfully extracted all the datasets via the api, however have noticed that the api only returns 20 records per a page. Doesn't make sense to make so many api calls to populate the dataset when we have a large number of the records via the text files. Seems like the API supports filtering (to be tested) which would allow us to design the app as a middleware, but the requirements seem to imply we want to store the data. I'll have the api supplement any missing data 

- I've realised the API filtering doesn't support a not in list of ids. Theres a datestamp, but the extracts I loaded dont have a datestamp. To meet the requirement if a pipeline that uses the API, will need to design a pull pipeline rather then a push, that gets the data ifs not already available. For these requirements I think this architecture makes more sense them spaming the API to try and load hundreds of records.

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
