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

- I've refactored the landing tables and loading to be more modular this should help when I start to pull data from the API, I've yet to recieve my API credentials yet so will wait for that. I don't really know what I'm going to get from the API so it would be good to implement this so I can maximise my understanding of all the data I can get from the different sources. 

- I've successfully extracted the occupations data using the API. I'll need to update schema and refactor the load pipeline. Once I've established I can successfully load I'll create the other functions to extract the other datasets via the API. 

- I've successfully extracted all the datasets via the api, however have noticed that the api only returns 20 records per a page. Doesn't make sense to make so many api calls to populate the dataset when we have a large number of the records via the text files. Seems like the API supports filtering (to be tested) which would allow us to design the app as a middleware, but the requirements seem to imply we want to store the data. I'll have the api supplement any missing data 

- I've realised the API filtering doesn't support a not in list of ids. Theres a datestamp, but the extracts I loaded dont have a datestamp. To meet the requirement if a pipeline that uses the API, will need to design a pull pipeline rather then a push, that gets the data ifs not already available. For these requirements I think this architecture makes more sense them spaming the API to try and load hundreds of records. Gemini has suggested we park this, and work on during phase 5 which I think makes sense.

- I've implemented the API calls just to verify my assumptions around their behaviour. Makes sense for the api to scan the database and then leverage the api if it cant find the code. We want the api calls to return the data directly to the analysis so we can respond to the user as fast as possible, then we can store the data in the database for future requests.

- I've started looking at the LLM functionality. I'm not sure how the LLM will repond to this so would be good to implement this in some way so I can understand if it can reliably fit in with the skills gap analysis.

- I've successfully been able to use the onet data to generate a prompt to gemini and have it return a structured json. 

- Further analysis of the skills dataset is showing that all occupations have the same skills unless a LV filter is applied excluding lvl 0. Confirms my suspicion that we need to use the LVL in some way here, otherwise there is no value add. Will still proceed with a implementation that adheres to requirements (will just strictly exclude 0) as well as a implementation for what I think would be more value add. The agent should be able to assist me with implementing both so it wont cost much. Given its the weekend, it would be better do just go both directions and note this in the readme then reaching out for clarification.

```sql
select onet_soc_code, count(distinct element_id )
from onet_data.onet_skills_landing
group by 1 -- all records showing 35 skills
```

```sql
select onet_soc_code, count(distinct element_id )
from onet_data.onet_skills_landing
where scale_id = "LV"
and data_value != 0
group by 1
```

- I've implemented both a skills gap and a skills gap by lvl feature. I also reflected on how we could use the LLM here, theres some interesting possibilities, however its probably more important to finish off the deployment and then loop back so I've added my ideas as a bonus implementation phase in the task list. 

- I've reflected on the API pull feature for data, it would ideally have a pipeline for the data to move from the API landing tables into the normalized tables. However I don't think I should bother with this for this assessment as it doesn't really demonstrate any additional capability I havn't already shown, also ussually i would want to get more feedback from the product designer before implementing this, we already implemented and proved we can hit the api and collect data. I'll add it to the tasks list and mark it as optional future implementation.

- I've setup a proper test env with a database. All the current integration tests I've been using for development hit the one database (which is sort of dev and prod at the same time atm). However all the functions have no way to swap out the db so I'll need to refactor the functions to swap in the test db config somehow.

- I've finished refactoring the functions, had limited success with the agent here, so was a bit of pain. I've commenced testing each of the integration tests, (again limited success with the agent here, but its done the bulk of the work for me so far, so cant complain too much.)

- I've setup a test_suite after reviewing all the integration tests (except for the llm ones). I'm running short on time so will push toward docker deployment and api setup. For some reason one of the tests keep failing when using pytest to run the suite, however when executing the tests one by one in order they all pass. Rather then get hung up on this I've opted to just create a shell script that just executes everything in order using it's allocated sh script rather then using pyest.