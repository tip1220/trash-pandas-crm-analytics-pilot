# Snowflake Load Guide

## Project

Trash Pandas Connected Reporting Pilot

## Purpose

This guide explains how to load the final connected reporting exports into Snowflake.

The project uses Python to generate, validate, and export the data.

Snowflake is used to model the warehouse-style reporting layer.

Tableau Public will use the final CSV exports for dashboarding.

The project flow is:

1. Python builds and validates the data.
2. Final CSV exports become clean reporting inputs.
3. Snowflake stores the reporting layer.
4. SQL validates the loaded data.
5. SQL views organize the data for analysis.
6. Tableau Public visualizes the final dashboard-ready exports.

---

## Why Snowflake Is Included

This project should not stop at CSV files.

Snowflake strengthens the portfolio build because it shows how the connected reporting layer could live in a cloud warehouse.

In a real sports business environment, data from ticketing, scans, CRM, group sales, merch, concessions, sponsorship, and engagement tools would flow into a warehouse.

This project models that structure with final export files.

---

## What Gets Loaded First

For the current build, load only the three final exports.

Do not load every raw or synthetic CSV yet.

### Final Exports

| File | Snowflake Table | Purpose |
|---|---|---|
| `data/exports/homestand_summary.csv` | `RAW.HOMESTAND_SUMMARY` | Homestand Intelligence page |
| `data/exports/promotion_scorecard.csv` | `RAW.PROMOTION_SCORECARD` | Promotion Performance Scorecard page |
| `data/exports/crm_follow_up_queue.csv` | `RAW.CRM_FOLLOW_UP_QUEUE` | CRM Follow-Up Queue page |

These three files are enough to prove the connected reporting layer for the current build.

---

## Snowflake Object Structure

Use one database:

`TRASH_PANDAS_CONNECTED_REPORTING`

Use three schemas:

| Schema | Purpose |
|---|---|
| `RAW` | Loaded CSV export tables |
| `ANALYTICS` | Reporting views and dashboard-ready logic |
| `QA` | Validation queries and quality-check helper objects if needed |

Use one warehouse:

`TP_REPORTING_WH`

Use one internal stage:

`RAW.TP_EXPORT_STAGE`

Use one CSV file format:

`RAW.CSV_EXPORT_FORMAT`

---

## Required SQL Files

Create the SQL files in this order:

| File | Purpose |
|---|---|
| `sql/00_snowflake_setup.sql` | Creates warehouse, database, schemas, file format, and stage |
| `sql/01_create_export_tables.sql` | Creates tables for the three final exports |
| `sql/02_load_export_tables.sql` | Loads staged CSV files into Snowflake tables |
| `sql/03_validate_export_tables.sql` | Validates row counts and key totals |
| `sql/04_create_analytics_views.sql` | Creates reporting-ready analytics views |
| `sql/05_business_question_queries.sql` | Answers business questions with SQL |

---

## Step 1: Create or Open Snowflake Account

Use a Snowflake trial or existing Snowflake account.

Recommended edition for this project:

- Standard is enough
- Enterprise is not required

Recommended cloud/region:

- Any available region is fine for portfolio work

This project does not require production infrastructure.

---

## Step 2: Open a Snowflake Worksheet

After logging into Snowflake:

1. Open Snowsight.
2. Go to Worksheets.
3. Create a new SQL worksheet.
4. Run the setup SQL from `sql/00_snowflake_setup.sql`.

The setup file should create:

- Warehouse
- Database
- Schemas
- File format
- Internal stage

---

## Step 3: Create Snowflake Tables

Run:

`sql/01_create_export_tables.sql`

This creates:

- `RAW.HOMESTAND_SUMMARY`
- `RAW.PROMOTION_SCORECARD`
- `RAW.CRM_FOLLOW_UP_QUEUE`

The tables should mirror the final export CSV files.

---

## Step 4: Upload CSV Files to Snowflake Stage

Upload these files:

- `data/exports/homestand_summary.csv`
- `data/exports/promotion_scorecard.csv`
- `data/exports/crm_follow_up_queue.csv`

Target stage:

`RAW.TP_EXPORT_STAGE`

Recommended stage paths:

| Local File | Stage Path |
|---|---|
| `homestand_summary.csv` | `@RAW.TP_EXPORT_STAGE/homestand_summary.csv` |
| `promotion_scorecard.csv` | `@RAW.TP_EXPORT_STAGE/promotion_scorecard.csv` |
| `crm_follow_up_queue.csv` | `@RAW.TP_EXPORT_STAGE/crm_follow_up_queue.csv` |

---

## Upload Option A: Snowsight

Use Snowsight if you want the easiest approach.

General workflow:

1. Go to Snowsight.
2. Open Data.
3. Choose Add Data or Load Data.
4. Choose the local CSV file.
5. Choose the target database and schema.
6. Load into the matching existing table or upload into the named stage first.
7. Confirm the file format uses comma delimiter and skips the header row.

Use this if you want fewer command-line steps.

---

## Upload Option B: SnowSQL or Snowflake CLI

Use this if you want a more technical workflow.

The upload command pattern is:

```sql
PUT file:///absolute/path/to/local/file.csv @RAW.TP_EXPORT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

Example macOS pattern:

```sql
PUT file:///Users/Tip/Desktop/trash-pandas-connected-reporting-pilot/data/exports/homestand_summary.csv @RAW.TP_EXPORT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

Repeat for:

- `promotion_scorecard.csv`
- `crm_follow_up_queue.csv`

---

## Step 5: Load CSV Files Into Tables

Run:

`sql/02_load_export_tables.sql`

The load script should:

1. Truncate the target tables.
2. Copy each CSV file from the stage.
3. Use the named CSV file format.
4. Skip the header row.
5. Load all fields into the correct columns.

Expected load targets:

| Table | Expected Row Count |
|---|---:|
| `RAW.HOMESTAND_SUMMARY` | 34 |
| `RAW.PROMOTION_SCORECARD` | 233 |
| `RAW.CRM_FOLLOW_UP_QUEUE` | 15,000 |

---

## Step 6: Validate the Load

Run:

`sql/03_validate_export_tables.sql`

The validation script should confirm:

| Check | Expected Value |
|---|---:|
| Homestand rows | 34 |
| Promotion scorecard rows | 233 |
| CRM queue rows | 15,000 |
| Homestand tickets sold | 1,274,234 |
| Homestand scanned attendance | 1,126,560 |
| Homestand total revenue indicator | 28,655,060.87 |
| CRM future revenue opportunity | 12,605,270.19 |

If any result does not match, stop and check:

- Wrong file uploaded
- Header row loaded as data
- Column order mismatch
- Numeric field loaded as text
- Incorrect file format
- Duplicate load without truncating first

---

## Step 7: Create Analytics Views

Run:

`sql/04_create_analytics_views.sql`

Core views:

| View | Purpose |
|---|---|
| `ANALYTICS.V_HOMESTAND_SUMMARY` | Clean homestand reporting view |
| `ANALYTICS.V_PROMOTION_SCORECARD` | Clean promotion decision view |
| `ANALYTICS.V_CRM_FOLLOW_UP_QUEUE` | Clean CRM action queue view |

Helper views:

| View | Purpose |
|---|---|
| `ANALYTICS.V_EXECUTIVE_HOMESTAND_OVERVIEW` | Executive summary by season and homestand |
| `ANALYTICS.V_PROMOTION_RECOMMENDATION_SUMMARY` | Promotion counts and value by recommendation |
| `ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY` | CRM workload by action bucket and assigned team |

---

## Step 8: Run Business Question SQL

Run:

`sql/05_business_question_queries.sql`

This file should answer:

1. Which homestands created the most total value?
2. Which promotions should return?
3. Which promotions should be reworked?
4. Which promotions should be retired?
5. Which promotions drove attendance lift but weak revenue lift?
6. Which promotions drove in-park spend?
7. Which homestands had the most no-show recovery opportunity?
8. Which fans or accounts should be prioritized for follow-up?
9. Which CRM action buckets are driving the queue?
10. Which teams own the follow-up workload?

---

## Step 9: Tableau Public Comes After Snowflake

Tableau Public will use CSV exports instead of a live Snowflake connection.

Use these files:

- `data/exports/homestand_summary.csv`
- `data/exports/promotion_scorecard.csv`
- `data/exports/crm_follow_up_queue.csv`

This keeps the published dashboard accessible and portfolio-friendly.

Snowflake still matters because it proves the data warehouse and SQL reporting layer.

The final portfolio story should say:

The connected reporting layer was modeled in Snowflake, validated with SQL, and visualized in Tableau Public using the final dashboard-ready exports.

---

## Expected Final Snowflake Objects

### Warehouse

- `TP_REPORTING_WH`

### Database

- `TRASH_PANDAS_CONNECTED_REPORTING`

### Schemas

- `RAW`
- `ANALYTICS`
- `QA`

### Stage

- `RAW.TP_EXPORT_STAGE`

### File Format

- `RAW.CSV_EXPORT_FORMAT`

### Raw Tables

- `RAW.HOMESTAND_SUMMARY`
- `RAW.PROMOTION_SCORECARD`
- `RAW.CRM_FOLLOW_UP_QUEUE`

### Analytics Views

- `ANALYTICS.V_HOMESTAND_SUMMARY`
- `ANALYTICS.V_PROMOTION_SCORECARD`
- `ANALYTICS.V_CRM_FOLLOW_UP_QUEUE`
- `ANALYTICS.V_EXECUTIVE_HOMESTAND_OVERVIEW`
- `ANALYTICS.V_PROMOTION_RECOMMENDATION_SUMMARY`
- `ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY`

---

## Snowflake Phase Completion Checklist

The Snowflake phase is complete when:

- `SNOWFLAKE_LOAD_GUIDE.md` exists
- `sql/00_snowflake_setup.sql` exists
- `sql/01_create_export_tables.sql` exists
- `sql/02_load_export_tables.sql` exists
- `sql/03_validate_export_tables.sql` exists
- `sql/04_create_analytics_views.sql` exists
- `sql/05_business_question_queries.sql` exists
- Final exports are loaded into Snowflake
- Validation queries return expected values
- Analytics views are created
- Business question queries run successfully

---

## Project Boundary

Do not overbuild this phase.

For the current build, Snowflake only needs to hold the final reporting exports.

Loading every public and synthetic source table can be added later, but it is not required to prove the connected reporting concept.

The current goal is to show a clean reporting layer, clear SQL validation, and business-question queries.