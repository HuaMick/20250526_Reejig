# Simplified Downstream Table Design

## Overview

Based on analysis of the current data structure, we'll create two downstream tables while using the existing Occupations table:

1. `Occupations` - Existing table (already normalized, will be used as-is)
2. `SkillsReference` - Skills reference information 
3. `OccupationSkills` - Joining table connecting occupations to skills with proficiency levels

## Table Definitions

### 1. Occupations (Existing Table)

The current `Occupations` table is already well-normalized and will be used directly:

```
Occupations
----------
onet_soc_code (PK)  : String(20)
title               : String(255)
description         : Text
```

### 2. SkillsReference

This table will contain the core information about each unique skill.

```
SkillsReference
--------------
element_id (PK)     : String(20)
element_name        : String(255)
source              : String(50)   # 'text_file', 'api', or 'merged'
last_updated        : DateTime
```

### 3. OccupationSkills

This joining table will connect occupations to skills with proficiency levels.

```
OccupationSkills
---------------
id (PK)             : Integer      # Auto-increment ID
onet_soc_code       : String(20)   # References NormalizedOccupations.onet_soc_code
element_id          : String(20)   # References SkillsReference.element_id
proficiency_level   : Decimal(5,2) # Only 'LV' scale data values
source              : String(50)   # 'text_file', 'api', or 'merged'
last_updated        : DateTime
```

## Data Flow

1. The raw tables (`Occupations`, `Skills`, `Scales`) will be preserved for reference.

2. The downstream tables will be populated from the raw tables:
   - `NormalizedOccupations` from `Occupations` table
   - `SkillsReference` from unique `element_id` and `element_name` pairs in `Skills` table
   - `OccupationSkills` from `Skills` table filtered for `scale_id = 'LV'`

3. When API data becomes available:
   - Data from API tables will be merged into the downstream tables
   - `source` field will track the origin of each record

## Benefits of This Design

1. **Reduced Redundancy**: Skills information is stored only once in `SkillsReference`

2. **Simplified Queries**: No need to filter by `scale_id = 'LV'` in application code

3. **Cleaner Data Access**: 
   - Retrieve occupation details from `NormalizedOccupations`
   - Get skills list from `SkillsReference`
   - Find occupation-specific skill levels in `OccupationSkills`

4. **Data Lineage**: Source tracking fields enable understanding of data provenance

5. **Easier Updates**: When new data arrives, we can selectively update records based on preferred sources 