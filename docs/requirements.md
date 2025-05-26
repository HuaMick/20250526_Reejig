# Senior Data Engineer - Take Home Assignment

## Objective
Develop an end-end data pipeline to:
1. **Extract**: Retrieve data from the public O*NET dataset
2. **Transform and Load**: Process the extracted data and store relevant information in a relational database
3. **Serve**: Expose specific data through a RESTful API

O*NET provides rich data on occupations, including skills, tasks, and requirements. Your task is to ingest data about occupations and their associated skills, and expose this data via a REST API. In particular, your API should support comparing two occupations to identify skill gaps between them.

## Data Sources
1. [Occupation.txt](https://www.onetcenter.org/dictionary/29.2/text/occupation_data.html)
2. [Skills.txt](https://www.onetcenter.org/dictionary/29.2/text/skills.html)

## Task Requirements

### 1. Database Design
- Design a relational schema using MySQL

### 2. ETL Pipeline
- Implement a script to populate the database via an ETL pipeline

### 3. REST API Implementation
- Implement a REST endpoint to serve skill gaps:
  ```
  GET /skill-gap?from={occupation_code1}&to={occupation_code2}
  ```
  - Compares two occupations and returns the skills required by the second occupation that are not present in the first

## Technical Requirements
- Use Python for the ETL and API
- Use Docker to containerize your services
- Use Docker Compose to run your MySQL database, ETL script, and API service as independent services
- Ensure everything runs with a single `docker-compose up`

## Submission Requirements
Include the following in your submission:
- Code for the ETL pipeline and API
- README file with:
  - Clear setup instructions
  - Description of your schema and design choices
  - Assumptions made
  - Sample requests for testing the API

## Evaluation Criteria
- Clean, modular, and maintainable code
- Well structured, normalized schema with appropriate relationships
- API returns accurate skill gap results
- Ease of setup and clear instructions
- Error handling and logging

## Bonus Points
- Includes automated tests
- LLM to extract skill proficiency for occupation-skill association

Please ensure your solution runs successfully in a local environment. As part of the technical interview, we will walk through and review your implementation together.