# Data Flow: Raw to Downstream Tables

## Overview

This document describes the flow of data from raw O*NET data tables to the simplified downstream tables used for application consumption.

## Table Structure

### Raw Data Tables

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Occupations │     │   Skills    │     │   Scales    │
├─────────────┤     ├─────────────┤     ├─────────────┤
│onet_soc_code│     │onet_soc_code│     │  scale_id   │
│    title    │     │ element_id  │     │ scale_name  │
│ description │     │element_name │     │   minimum   │
└─────────────┘     │  scale_id   │     │   maximum   │
                    │ data_value  │     └─────────────┘
                    │   n_value   │
                    │    ...      │
                    └─────────────┘
```

### Downstream Tables

```
┌─────────────┐     ┌───────────────────┐     ┌─────────────────┐
│ Occupations │     │ SkillsReference   │     │ OccupationSkills │
├─────────────┤     ├───────────────────┤     ├─────────────────┤
│onet_soc_code│     │    element_id     │     │       id        │
│    title    │     │   element_name    │     │  onet_soc_code  │
│ description │     │      source       │     │   element_id    │
└─────────────┘     │   last_updated    │     │proficiency_level│
                    └───────────────────┘     │     source      │
                                              │  last_updated   │
                                              └─────────────────┘
```

## Data Transformation Process

1. **Occupations Table**:
   - Used directly without transformation (already normalized)
   - Primary key: `onet_soc_code`

2. **Skills Table → SkillsReference**:
   - Extract unique `element_id` and `element_name` pairs
   - Add `source` and `last_updated` metadata
   - Primary key: `element_id`

3. **Skills Table → OccupationSkills**:
   - Filter records where `scale_id = 'LV'` (skill level scale)
   - Extract `onet_soc_code`, `element_id`, and `data_value` (renamed to `proficiency_level`)
   - Add `source` and `last_updated` metadata
   - Primary key: Auto-incrementing `id`
   - Unique constraint: `(onet_soc_code, element_id)`

## Data Flow Diagram

```
┌───────────┐      ┌────────────────────┐
│  O*NET    │      │                    │
│ Text Files├──────► Raw Data Tables    │
└───────────┘      │                    │
                   └──────────┬─────────┘
                              │
                              ▼
                   ┌────────────────────┐
                   │populate_downstream_│
                   │     tables()      │
                   └──────────┬─────────┘
                              │
                              ▼
                   ┌────────────────────┐
                   │                    │
                   │ Downstream Tables  │
                   │                    │
                   └──────────┬─────────┘
                              │
                              ▼
┌───────────┐      ┌────────────────────┐
│           │      │ Application        │
│  User     ◄──────┤ Functions:         │
│ Requests  │      │ - get_occupation() │
└───────────┘      │ - get_occupation_  │
                   │   skills()         │
                   └────────────────────┘
```

## Benefits of This Design

1. **Simplified Data Access**:
   - No need to filter by `scale_id = 'LV'` in application code
   - Direct access to skill proficiency levels

2. **Improved Performance**:
   - Smaller, more focused tables
   - Pre-filtered data reduces query complexity and execution time

3. **Clearer Data Structure**:
   - Separation of skill reference data from skill measurements
   - Explicit representation of occupation-skill relationships

4. **Data Lineage**:
   - Source tracking enables understanding of data provenance
   - Timestamp tracking for data freshness assessment 