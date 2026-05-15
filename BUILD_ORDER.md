# Build Order

## Project

Trash Pandas Connected Reporting Pilot

## Current Status

The core data build is complete through the Tableau-ready export layer.

Final dashboard exports have been generated and quality checked:

- `data/exports/homestand_summary.csv`
- `data/exports/promotion_scorecard.csv`
- `data/exports/crm_follow_up_queue.csv`

The next required phase is the Snowflake reporting layer.

Tableau Public comes after Snowflake setup, SQL validation, and business-question queries are documented.

---

## Completed Build Phases

### Phase 1: Project Reset

Goal:

Reframe the portfolio project from a CRM pilot to a connected reporting proof of concept.

Completed files:

- `README.md`
- `PROJECT_CHARTER.md`
- `BUSINESS_QUESTIONS.md`
- `DATA_SOURCE_MAP.md`
- `DATA_ASSUMPTIONS.md`
- `SYNTHETIC_DATA_PLAN.md`
- `SNOWFLAKE_SCHEMA_PLAN.md`
- `DASHBOARD_PLAN.md`

Status:

Complete.

---

### Phase 2: Public Data Foundation

Goal:

Build the public anchor layer for home games, promotions, and announced attendance.

Completed outputs:

- `data/processed/games_clean.csv`
- `data/processed/promotions_clean.csv`
- `data/processed/attendance_clean.csv`
- `data/public/public_source_log.csv`

Completed scripts:

- Public data prep scripts
- Public data quality checks
- Promotion quality checks

Status:

Complete.

---

### Phase 3: Synthetic Fan and Ticketing Layer

Goal:

Create internal-style fan, ticket order, and scan data that demonstrates how fan-level reporting could work.

Completed outputs:

- `data/synthetic/fans.csv`
- `data/synthetic/fan_segments.csv`
- `data/synthetic/ticket_orders.csv`
- `data/synthetic/ticket_order_items.csv`
- `data/synthetic/ticket_scans.csv`

Completed quality checks:

- Fan quality checks
- Ticket quality checks
- Scan quality checks

Status:

Complete.

---

### Phase 4: Group Sales Layer

Goal:

Add group accounts and group sales behavior for renewal and upsell reporting.

Completed outputs:

- `data/synthetic/group_accounts.csv`
- `data/synthetic/group_sales.csv`
- `data/synthetic/group_sales_generation_summary.csv`

Completed quality checks:

- Group sales quality checks

Status:

Complete.

---

### Phase 5: In-Park Spend Layer

Goal:

Add merch and concession transactions to show fan value beyond ticket purchases.

Completed outputs:

- `data/synthetic/merch_transactions.csv`
- `data/synthetic/concession_transactions.csv`

Completed quality checks:

- Merch quality checks
- Concession quality checks

Status:

Complete.

---

### Phase 6: Sponsorship Context Layer

Goal:

Add sponsorship activations as game/promotion context without claiming sponsorship ROI.

Completed outputs:

- `data/synthetic/sponsorship_activations.csv`

Completed quality checks:

- Sponsorship quality checks

Status:

Complete.

---

### Phase 7: Fan Engagement Layer

Goal:

Add synthetic engagement signals used in repeat likelihood, upgrade potential, and follow-up scoring.

Completed outputs:

- `data/synthetic/fan_engagement.csv`

Completed quality checks:

- Fan engagement quality checks

Status:

Complete.

---

### Phase 8: Follow-Up Opportunity and CRM Task Layer

Goal:

Turn connected behavior into follow-up opportunities and a balanced CRM task queue.

Completed outputs:

- `data/synthetic/follow_up_opportunities.csv`
- `data/synthetic/crm_follow_ups.csv`

Completed scripts:

- `python/16_generate_follow_up_opportunities.py`
- `python/17_rebalance_crm_follow_ups.py`

Completed quality checks:

- Follow-up quality checks

Status:

Complete.

---

### Phase 9: Tableau Export Layer

Goal:

Create dashboard-ready exports for the three final dashboard pages.

Completed exports:

- `data/exports/homestand_summary.csv`
- `data/exports/promotion_scorecard.csv`
- `data/exports/crm_follow_up_queue.csv`

Completed generation summaries:

- `data/exports/homestand_summary_generation_summary.csv`
- `data/exports/promotion_scorecard_generation_summary.csv`
- `data/exports/crm_follow_up_queue_generation_summary.csv`

Completed quality summaries:

- `data/exports/homestand_summary_quality_summary.csv`
- `data/exports/promotion_scorecard_quality_summary.csv`
- `data/exports/crm_follow_up_queue_quality_summary.csv`

Completed documentation:

- `data/exports/export_manifest.csv`

Status:

Complete.

---

## Current Required Phase

### Phase 10: Snowflake Reporting Layer

Goal:

Load the final connected reporting exports into Snowflake and create a warehouse-style reporting layer that can be queried with SQL.

This phase makes the project stronger because the work does not stop at Python-generated CSVs.

The intended project flow is:

1. Python generates and validates the data.
2. CSV exports become clean reporting inputs.
3. Snowflake stores the reporting layer.
4. SQL validates and queries the connected data.
5. Tableau Public uses dashboard-ready CSV exports for the published dashboard.

Status:

Next.

---

## Snowflake Build Order

### Step 1: Create Snowflake Load Guide

Create:

- `SNOWFLAKE_LOAD_GUIDE.md`

Purpose:

Document how to set up Snowflake, upload the final exports, load the tables, validate the data, create analytics views, and explain the portfolio story.

The guide should cover:

- Snowflake account/trial setup
- Warehouse setup
- Database setup
- Schema setup
- CSV file format setup
- Internal stage setup
- Export upload process
- `COPY INTO` load process
- Validation queries
- Analytics views
- How Tableau Public fits after Snowflake

---

### Step 2: Create Snowflake Setup SQL

Create:

- `sql/00_snowflake_setup.sql`

Purpose:

Set up the Snowflake environment.

Should include:

- Warehouse
- Database
- Schemas
- CSV file format
- Internal stage

Expected schemas:

- `RAW`
- `ANALYTICS`
- `QA`

---

### Step 3: Create Export Table SQL

Create:

- `sql/01_create_export_tables.sql`

Purpose:

Create Snowflake tables for the final exports.

Tables:

- `RAW.HOMESTAND_SUMMARY`
- `RAW.PROMOTION_SCORECARD`
- `RAW.CRM_FOLLOW_UP_QUEUE`

These tables should mirror the final CSV exports.

---

### Step 4: Create Load SQL

Create:

- `sql/02_load_export_tables.sql`

Purpose:

Load staged export files into Snowflake tables.

Files to load:

- `homestand_summary.csv`
- `promotion_scorecard.csv`
- `crm_follow_up_queue.csv`

---

### Step 5: Create Validation SQL

Create:

- `sql/03_validate_export_tables.sql`

Purpose:

Validate that Snowflake loaded the final exports correctly.

Validation targets:

- Homestand row count = 34
- Promotion scorecard row count = 233
- CRM queue row count = 15,000
- Homestand tickets sold = 1,274,234
- Homestand scanned attendance = 1,126,560
- Homestand total revenue indicator = 28,655,060.87
- CRM future revenue opportunity = 12,605,270.19

---

### Step 6: Create Analytics Views SQL

Create:

- `sql/04_create_analytics_views.sql`

Purpose:

Create reporting-ready views from the loaded Snowflake tables.

Core views:

- `ANALYTICS.V_HOMESTAND_SUMMARY`
- `ANALYTICS.V_PROMOTION_SCORECARD`
- `ANALYTICS.V_CRM_FOLLOW_UP_QUEUE`

Recommended helper views:

- `ANALYTICS.V_EXECUTIVE_HOMESTAND_OVERVIEW`
- `ANALYTICS.V_PROMOTION_RECOMMENDATION_SUMMARY`
- `ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY`

---

### Step 7: Create Business Question Queries SQL

Create:

- `sql/05_business_question_queries.sql`

Purpose:

Show SQL answers to the project’s main business questions.

Queries should answer:

1. Which homestands created the most total value?
2. Which promotions should return, be reworked, retired, or reviewed?
3. Which promotions drove attendance lift but weak revenue lift?
4. Which promotions drove in-park spend?
5. Which homestands had the most no-show recovery opportunity?
6. Which fans or accounts should be prioritized for follow-up?
7. Which CRM action buckets are driving the queue?
8. Which teams own the follow-up workload?

---

## Phase 11: Tableau Public Dashboard Build

Goal:

Build the three-page Tableau Public dashboard using final export files.

Tableau Public will use the CSV exports because the published dashboard should stay accessible and portfolio-friendly.

Primary data sources:

1. `data/exports/homestand_summary.csv`
2. `data/exports/promotion_scorecard.csv`
3. `data/exports/crm_follow_up_queue.csv`

Dashboard pages:

1. Homestand Intelligence
2. Promotion Scorecard
3. CRM Follow-Up Queue

Build guide:

- `TABLEAU_BUILD_GUIDE.md`

Status:

Waiting on Snowflake phase.

---

## Tableau Build Order

### Step 1: Connect Final Exports

Connect these CSV files in Tableau Public:

- `homestand_summary.csv`
- `promotion_scorecard.csv`
- `crm_follow_up_queue.csv`

Use them as separate data sources.

Do not force relationships unless needed.

---

### Step 2: Build Homestand Intelligence Page

Build first because it is the executive summary.

Priority sheets:

1. KPI - Tickets Sold
2. KPI - Scanned Attendance
3. KPI - Scan Rate
4. KPI - No-Show Rate
5. KPI - Total Revenue Indicator
6. KPI - Homestand Value Index
7. Homestand Ranking Table
8. Tickets Sold vs Scanned Attendance
9. No-Show Rate by Homestand
10. Revenue Mix by Homestand
11. Recommended Focus Breakdown

---

### Step 3: Build Promotion Scorecard Page

Build second because it answers which promotions worked.

Priority sheets:

1. KPI - Promotion Count
2. KPI - Avg. Total Value Index
3. KPI - Return / Rework Count
4. Recommendation Breakdown
5. Promotion Scorecard Table
6. Total Value Index by Promo Category
7. Attendance Lift vs Revenue Lift
8. In-Park Spend Lift by Promotion
9. Repeat Buyer Signal

---

### Step 4: Build CRM Follow-Up Queue Page

Build third because it turns reporting into action.

Priority sheets:

1. KPI - Open Follow-Up Tasks
2. KPI - High Priority Tasks
3. KPI - Future Revenue Opportunity
4. KPI - Avg. Priority Score
5. Action Bucket Breakdown
6. Assigned Team Workload
7. Priority Queue Table
8. Hidden Fan Value View
9. Opportunity Type Breakdown

---

### Step 5: Add Dashboard Source Note

Use this source note on each dashboard page:

Public data is used where available. Internal-style ticketing, scan, merch, concessions, engagement, group sales, and CRM fields are synthetic and used only to demonstrate connected reporting structure.

---

### Step 6: Publish to Tableau Public

Suggested workbook title:

`Trash Pandas Connected Reporting Pilot`

After publishing:

- Add Tableau Public link to `README.md`
- Add dashboard screenshots to repo if desired
- Add final project summary
- Create LinkedIn/project write-up

---

## Remaining Project Work

### Required

- Create `SNOWFLAKE_LOAD_GUIDE.md`
- Create Snowflake SQL setup file
- Create Snowflake export table DDL
- Create Snowflake load SQL
- Create Snowflake validation SQL
- Create Snowflake analytics views
- Create business-question SQL queries
- Load final exports into Snowflake
- Validate loaded Snowflake tables
- Build Tableau Public dashboard
- Add Tableau Public link to README
- Final README polish after dashboard is published

### Recommended

- Add dashboard screenshots
- Add a short executive summary section
- Add a recruiter-facing portfolio summary
- Add a LinkedIn post draft
- Add a final project retrospective
- Add a Snowflake/SQL summary section to README after SQL files are complete

### Optional

- Load every raw/synthetic CSV into Snowflake
- Rebuild the full Python export logic as SQL views
- Add dashboard design screenshots
- Add a short walkthrough video script

---

## Final Build Logic

This project should stay focused.

Do not overbuild.

The MVP is successful when it proves this:

A team can make better decisions when ticketing, scans, promotions, merch, concessions, group sales, fan engagement, and CRM follow-up data are connected into one reporting layer.

The final project should answer:

1. What happened?
2. What worked?
3. Who should we contact next?
4. How would this reporting layer live in Snowflake?
5. Which SQL queries prove the business value?

Snowflake is now part of the required MVP.

Tableau comes after the Snowflake reporting layer is documented and validated.