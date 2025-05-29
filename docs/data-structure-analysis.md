# O*NET Data Structure Analysis

## Current Data Sources

### 1. Text Files Data (Implemented)

The current implementation processes three text files:

1. **occupations.txt** → `Occupations` table
   - Key fields: `onet_soc_code` (PK), `title`, `description`
   - Primary identifier: `onet_soc_code` (e.g., "15-1252.00")

2. **skills.txt** → `Skills` table
   - Key fields: `onet_soc_code`, `element_id`, `element_name`, `scale_id`, `data_value`, etc.
   - Composite primary key: (`onet_soc_code`, `element_id`, `scale_id`)
   - Contains skill measurements with different scale types

3. **scales.txt** → `Scales` table
   - Key fields: `scale_id` (PK), `scale_name`, `minimum`, `maximum`
   - Used to interpret skill measurements
   - Common scale: "LV" (Level) used for skill proficiency

### 2. API Data (Planned)

While API integration is pending credentials, the planned structure will include:

1. **O*NET API Occupation Data** → Will be stored in `OnetApiOccupationData` table
   - Expected to include occupation codes, titles, and descriptions
   - Similar structure to text file data but potentially with additional fields

2. **O*NET API Skills Data** → Will be stored in `OnetApiSkillsData` table
   - Expected to include skills measurements for occupations
   - Similar to text file data but potentially with different format or additional fields

## Current Data Usage Pattern

1. **Data Extraction and Loading**:
   - `extract_onet_data()` reads text files and produces DataFrames
   - Data is loaded into raw tables: `Occupations`, `Skills`, `Scales`

2. **Data Consumption**:
   - `get_occupation_skills()` retrieves skills data for a specific occupation
     - Filters for the "LV" (Level) scale specifically
     - Returns a structured response with occupation title and skills list
   - `identify_skill_gap()` compares skills between two occupations
     - Identifies missing skills or skills with higher proficiency requirements

## Observations and Opportunities for Downstream Tables

### Current Limitations

1. **Denormalized Structure**:
   - `Skills` table contains many different types of measurements mixed together
   - Filtering by `scale_id = 'LV'` is required in application code

2. **Missing Direct Functions**:
   - No dedicated function to retrieve basic occupation information
   - Skills data must always be retrieved together with occupation information

### Recommendations for Downstream Tables

1. **NormalizedOccupations Table**:
   - Purpose: Streamlined access to occupation information
   - Combine best data from text files and API sources
   - Fields: `onet_soc_code`, `title`, `description`, `source`, `last_updated`

2. **NormalizedSkills Table**:
   - Purpose: Simplified skills data focused on proficiency levels
   - Pre-filter for the most relevant scale ("LV")
   - Fields: `onet_soc_code`, `element_id`, `element_name`, `proficiency_level`, `source`, `last_updated`

This approach will:
- Keep raw data intact for reference and reloading
- Provide simplified, purpose-built tables for application functions
- Support easier querying without complex filtering
- Enable clear data lineage tracking with source and timestamp fields 