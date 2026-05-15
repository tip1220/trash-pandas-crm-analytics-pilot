# Task Tracker

## Project

Trash Pandas Connected Reporting Pilot

## Last Updated

2026-05-15

## Current Project Status

The Python data generation, synthetic data modeling, quality checks, and Tableau-ready export files are complete.

The next phase is **Snowflake reporting layer setup**.

Tableau comes after Snowflake validation.

Current phase:

Snowflake load guide and SQL reporting layer.

---

## Completed Work

### 1. Project Direction Reset

Status: Complete

Completed:

- Reframed the project from Trash Pandas CRM Analytics Pilot to Trash Pandas Connected Reporting Pilot
- Shifted the project from “they need a CRM” to “they may need connected reporting”
- Defined the project as a reporting structure proof of concept
- Confirmed the project does not assume internal Trash Pandas data access
- Confirmed public, synthetic, and internal-style data boundaries
- Confirmed the audience is leadership first, then sales, marketing, recruiters, and hiring managers

Key files:

- `README.md`
- `PROJECT_CHARTER.md`
- `BUSINESS_QUESTIONS.md`
- `DATA_SOURCE_MAP.md`
- `DATA_ASSUMPTIONS.md`
- `SYNTHETIC_DATA_PLAN.md`
- `SNOWFLAKE_SCHEMA_PLAN.md`
- `DASHBOARD_PLAN.md`
- `BUILD_ORDER.md`

---

### 2. Data Source Map

Status: Complete

Completed:

- Mapped source areas across ticketing, promotions, scans, CRM, group sales, merch, concessions, sponsorship, engagement, and revenue reporting
- Defined source grain
- Defined key fields
- Defined join keys
- Defined reporting purpose
- Separated public, synthetic, and internal-only data types
- Clarified sponsorship as context only, not ROI analysis

Primary file:

- `DATA_SOURCE_MAP.md`

---

### 3. Public Data Foundation

Status: Complete

Completed:

- Built games foundation for 2023-2025 home games
- Confirmed 207 total home games
- Confirmed 69 home games per season
- Built promotion foundation
- Built public attendance foundation
- Matched public attendance where available
- Logged public data sources
- Added public data quality checks
- Added promotion quality checks

Key outputs:

- `data/processed/games_clean.csv`
- `data/processed/promotions_clean.csv`
- `data/processed/attendance_clean.csv`
- `data/public/public_source_log.csv`
- `data/processed/public_data_quality_summary.csv`
- `data/processed/promotion_quality_summary.csv`

Status notes:

- Public attendance is used as an anchor.
- Public attendance is not treated as scanned attendance.
- Unmatched public attendance rows are documented instead of forced.

---

### 4. Synthetic Fan Layer

Status: Complete

Completed:

- Generated 45,000 synthetic fans
- Generated fan segments
- Fixed lifecycle segment logic so each fan has one lifecycle segment
- Confirmed fan segment quality checks pass

Key outputs:

- `data/synthetic/fans.csv`
- `data/synthetic/fan_segments.csv`
- `data/synthetic/fan_generation_summary.csv`
- `data/synthetic/fan_quality_summary.csv`

Key scripts:

- `python/data_generation/01_generate_fans.py`
- `python/quality_checks/04_fan_quality_checks.py`

---

### 5. Synthetic Ticketing Layer

Status: Complete

Completed:

- Generated synthetic ticket orders
- Generated ticket order items
- Generated ticket scans
- Added ticket quality checks
- Added scan quality checks

Key outputs:

- `data/synthetic/ticket_orders.csv`
- `data/synthetic/ticket_order_items.csv`
- `data/synthetic/ticket_scans.csv`
- `data/synthetic/ticket_generation_summary.csv`
- `data/synthetic/ticket_scan_generation_summary.csv`
- `data/synthetic/ticket_quality_summary.csv`
- `data/synthetic/scan_quality_summary.csv`

Key scripts:

- `python/data_generation/02_generate_ticket_orders.py`
- `python/data_generation/03_generate_ticket_scans.py`
- `python/quality_checks/05_ticket_quality_checks.py`
- `python/quality_checks/06_scan_quality_checks.py`

Final modeled totals:

- Ticket orders: 343,165
- Tickets sold: 1,274,234
- Scanned attendance: 1,126,560
- No-show tickets: 147,674

---

### 6. Group Sales Layer

Status: Complete

Completed:

- Generated synthetic group accounts
- Generated synthetic group sales
- Appended group orders, order items, and scans into ticketing layer
- Added group sales quality checks

Key outputs:

- `data/synthetic/group_accounts.csv`
- `data/synthetic/group_sales.csv`
- `data/synthetic/group_sales_generation_summary.csv`
- `data/synthetic/group_quality_summary.csv`

Key scripts:

- `python/data_generation/04_generate_group_sales.py`
- `python/quality_checks/07_group_quality_checks.py`

Final modeled totals:

- Group accounts: 1,200
- Group sales: 3,600
- Group tickets: 190,669
- Group revenue: 2,603,410.24

---

### 7. Merch Layer

Status: Complete

Completed:

- Generated synthetic merch transactions
- Linked 60-75% of merch transactions to `fan_id`
- Added merch quality checks

Key outputs:

- `data/synthetic/merch_transactions.csv`
- `data/synthetic/merch_generation_summary.csv`
- `data/synthetic/merch_quality_summary.csv`

Key scripts:

- `python/data_generation/05_generate_merch_transactions.py`
- `python/quality_checks/08_merch_quality_checks.py`

Final modeled totals:

- Merch transactions: 45,557
- Merch net sales: 1,765,481.28
- Fan match share: 68.43%

---

### 8. Concession Layer

Status: Complete

Completed:

- Generated synthetic concession transactions
- Linked 35-55% of concession transactions to `fan_id`
- Added concession quality checks

Key outputs:

- `data/synthetic/concession_transactions.csv`
- `data/synthetic/concession_generation_summary.csv`
- `data/synthetic/concession_quality_summary.csv`

Key scripts:

- `python/data_generation/06_generate_concession_transactions.py`
- `python/quality_checks/09_concession_quality_checks.py`

Final modeled totals:

- Concession transactions: 314,165
- Concession net sales: 5,570,004.38
- Fan match share: 45.82%

---

### 9. Sponsorship Context Layer

Status: Complete

Completed:

- Generated synthetic sponsorship activations
- Treated sponsorship as context only
- Did not calculate sponsorship ROI
- Added sponsorship quality checks

Key outputs:

- `data/synthetic/sponsorship_activations.csv`
- `data/synthetic/sponsorship_activation_generation_summary.csv`
- `data/synthetic/sponsorship_quality_summary.csv`

Key scripts:

- `python/data_generation/07_generate_sponsorship_activations.py`
- `python/quality_checks/10_sponsorship_quality_checks.py`

Final modeled totals:

- Sponsorship activations: 93
- Games with sponsor activation: 86
- Unique sponsors: 64

---

### 10. Fan Engagement Layer

Status: Complete

Completed:

- Generated synthetic fan engagement rows
- Included email, SMS, web, in-park QR, survey, merch offer, concession offer, group interest, and premium interest signals
- Added fan engagement quality checks

Key outputs:

- `data/synthetic/fan_engagement.csv`
- `data/synthetic/fan_engagement_generation_summary.csv`
- `data/synthetic/fan_engagement_quality_summary.csv`

Key scripts:

- `python/data_generation/08_generate_fan_engagement.py`
- `python/quality_checks/11_fan_engagement_quality_checks.py`

Final modeled totals:

- Fan engagement rows: 135,112
- Unique engaged fans: 20,505
- Average engagement score: 26.54

Status note:

- App, social, and offer-response signals were not modeled for current build.
- The current build still has enough behavioral signal from email, SMS, QR, survey, web, and offer-click activity.

---

### 11. Follow-Up Opportunity Layer

Status: Complete

Completed:

- Generated follow-up opportunity pool
- Generated CRM follow-up tasks
- Rebalanced CRM queue across service, sales, marketing, and group sales
- Added follow-up quality checks

Key outputs:

- `data/synthetic/follow_up_opportunities.csv`
- `data/synthetic/crm_follow_ups.csv`
- `data/synthetic/follow_up_generation_summary.csv`
- `data/synthetic/follow_up_quality_summary.csv`

Key scripts:

- `python/data_generation/09_generate_follow_up_opportunities.py`
- `python/data_generation/10_rebalance_crm_follow_ups.py`
- `python/quality_checks/12_follow_up_quality_checks.py`

Final modeled totals:

- Follow-up opportunities: 52,416
- CRM follow-up tasks: 15,000
- Service tasks: 5,890
- Sales tasks: 4,000
- Marketing tasks: 4,000
- Group sales tasks: 1,110

---

### 12. Homestand Summary Export

Status: Complete

Completed:

- Built Tableau-ready homestand summary export
- Added quality checks
- Confirmed export reconciles to source files

Key outputs:

- `data/exports/homestand_summary.csv`
- `data/exports/homestand_summary_generation_summary.csv`
- `data/exports/homestand_summary_quality_summary.csv`

Key scripts:

- `python/export_builds/01_build_homestand_summary.py`
- `python/quality_checks/13_homestand_summary_quality_checks.py`

Final modeled totals:

- Homestand rows: 34
- Total games: 207
- Tickets sold: 1,274,234
- Scanned attendance: 1,126,560
- Total revenue indicator: 28,655,060.87

---

### 13. Promotion Scorecard Export

Status: Complete

Completed:

- Built Tableau-ready promotion scorecard export
- Added quality checks
- Added promotion recommendations: return, rework, retire, review

Key outputs:

- `data/exports/promotion_scorecard.csv`
- `data/exports/promotion_scorecard_generation_summary.csv`
- `data/exports/promotion_scorecard_quality_summary.csv`

Key scripts:

- `python/export_builds/02_build_promotion_scorecard.py`
- `python/quality_checks/14_promotion_scorecard_quality_checks.py`

Final modeled totals:

- Promotion rows: 233
- Return recommendations: 6
- Rework recommendations: 47
- Retire recommendations: 7
- Review recommendations: 173
- Average total value index: 43.05

---

### 14. CRM Follow-Up Queue Export

Status: Complete

Completed:

- Built Tableau-ready CRM follow-up queue export
- Fixed entity mapping bug where blank fan/account IDs appeared as NaN
- Added quality checks
- Confirmed fan/account entity logic passes clean

Key outputs:

- `data/exports/crm_follow_up_queue.csv`
- `data/exports/crm_follow_up_queue_generation_summary.csv`
- `data/exports/crm_follow_up_queue_quality_summary.csv`

Key scripts:

- `python/export_builds/03_build_crm_follow_up_queue.py`
- `python/quality_checks/15_crm_follow_up_queue_quality_checks.py`

Final modeled totals:

- Queue rows: 15,000
- Fan tasks: 13,890
- Account tasks: 1,110
- High priority tasks: 13,923
- Medium priority tasks: 1,077
- Total future revenue opportunity: 12,605,270.19
- Average priority score: 93.78

---

### 15. Export Manifest

Status: Complete

Completed:

- Created manifest documenting final dashboard-ready exports
- Defined each export grain, dashboard use, source type, and description

Key output:

- `data/exports/export_manifest.csv`

---

### 16. Documentation Updates

Status: In progress

Completed:

- Updated README for connected reporting story
- Updated dashboard plan around final exports
- Added Tableau build guide
- Updated build order for dashboard phase

Needs correction:

- Documentation needs Snowflake phase added before Tableau build
- README needs Snowflake reporting layer section after SQL files are created
- Build order should identify Snowflake as the next required phase, not optional

Key files:

- `README.md`
- `DASHBOARD_PLAN.md`
- `TABLEAU_BUILD_GUIDE.md`
- `BUILD_ORDER.md`
- `TASK_TRACKER.md`

---

## Current Required Phase

### Phase 17: Snowflake Reporting Layer

Status: Next

Goal:

Load the final connected reporting exports into Snowflake and create a real warehouse-style reporting layer that can be queried with SQL.

This phase exists because the project should not stop at Python-generated CSVs.

Snowflake gives the project a stronger business intelligence portfolio story:

1. Python generates and validates the data.
2. CSV exports become clean reporting inputs.
3. Snowflake stores the reporting layer.
4. SQL validates and queries the connected data.
5. Tableau Public uses dashboard-ready CSV exports because Tableau Public is file/extract oriented.

---

## Snowflake Work To Do

### 17.1 Create Snowflake Load Guide

Status: Not started

Create:

- `SNOWFLAKE_LOAD_GUIDE.md`

Guide should cover:

- Snowflake trial/account setup
- Warehouse/database/schema setup
- Creating a stage
- Creating CSV file format
- Uploading final exports
- Loading CSVs into tables
- Running validation queries
- Creating analytics views
- How this fits the portfolio story

---

### 17.2 Create Snowflake SQL Setup File

Status: Not started

Create:

- `sql/00_snowflake_setup.sql`

Purpose:

- Create warehouse
- Create database
- Create schemas
- Create CSV file format
- Create internal stage

Expected schemas:

- `RAW`
- `ANALYTICS`
- `QA`

---

### 17.3 Create Export Table DDL

Status: Not started

Create:

- `sql/01_create_export_tables.sql`

Purpose:

Create Snowflake tables for:

- `RAW.HOMESTAND_SUMMARY`
- `RAW.PROMOTION_SCORECARD`
- `RAW.CRM_FOLLOW_UP_QUEUE`

These tables should mirror the three final export CSVs.

---

### 17.4 Create Load SQL

Status: Not started

Create:

- `sql/02_load_export_tables.sql`

Purpose:

Load staged CSV files into Snowflake tables.

Files to load:

- `homestand_summary.csv`
- `promotion_scorecard.csv`
- `crm_follow_up_queue.csv`

---

### 17.5 Create Validation SQL

Status: Not started

Create:

- `sql/03_validate_export_tables.sql`

Purpose:

Validate Snowflake row counts and key totals.

Validation should check:

- Homestand row count = 34
- Promotion scorecard row count = 233
- CRM queue row count = 15,000
- Homestand tickets sold = 1,274,234
- Homestand scanned attendance = 1,126,560
- Homestand total revenue indicator = 28,655,060.87
- CRM future revenue opportunity = 12,605,270.19

---

### 17.6 Create Analytics Views

Status: Not started

Create:

- `sql/04_create_analytics_views.sql`

Purpose:

Create final reporting views:

- `ANALYTICS.V_HOMESTAND_SUMMARY`
- `ANALYTICS.V_PROMOTION_SCORECARD`
- `ANALYTICS.V_CRM_FOLLOW_UP_QUEUE`

Optional helper views:

- `ANALYTICS.V_EXECUTIVE_HOMESTAND_OVERVIEW`
- `ANALYTICS.V_PROMOTION_RECOMMENDATION_SUMMARY`
- `ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY`

---

### 17.7 Create Business Question Queries

Status: Not started

Create:

- `sql/05_business_question_queries.sql`

Purpose:

Show SQL answers to core business questions:

- Which homestands created the most total value?
- Which promotions should return, rework, retire, or review?
- Which promotions drove attendance lift but weak revenue lift?
- Which promotions drove in-park spend?
- Which games or homestands had no-show recovery opportunities?
- Which fans/accounts should be prioritized for follow-up?
- Which action buckets are driving the CRM queue?
- Which teams own the follow-up workload?

---

## Tableau Phase

### Phase 18: Tableau Public Dashboard Build

Status: Waiting on Snowflake phase

Goal:

Build the three-page Tableau Public dashboard using final export files.

Primary data sources:

1. `data/exports/homestand_summary.csv`
2. `data/exports/promotion_scorecard.csv`
3. `data/exports/crm_follow_up_queue.csv`

Dashboard pages:

1. Homestand Intelligence
2. Promotion Scorecard
3. CRM Follow-Up Queue

Primary guide:

- `TABLEAU_BUILD_GUIDE.md`

Status note:

Tableau Public will use CSV exports.

Snowflake will be used as the warehouse/reporting layer and SQL validation layer.

---

## Current To-Do List

### Priority 1: Build Snowflake Load Guide

Status: Not started

File:

- `SNOWFLAKE_LOAD_GUIDE.md`

---

### Priority 2: Create Snowflake SQL Files

Status: Not started

Files:

- `sql/00_snowflake_setup.sql`
- `sql/01_create_export_tables.sql`
- `sql/02_load_export_tables.sql`
- `sql/03_validate_export_tables.sql`
- `sql/04_create_analytics_views.sql`
- `sql/05_business_question_queries.sql`

---

### Priority 3: Load Final Exports Into Snowflake

Status: Not started

Files to load:

- `data/exports/homestand_summary.csv`
- `data/exports/promotion_scorecard.csv`
- `data/exports/crm_follow_up_queue.csv`

---

### Priority 4: Run Snowflake Validation Queries

Status: Not started

Validation target:

- Row counts match exported CSVs
- Key totals match Python export quality checks
- Analytics views return expected results

---

### Priority 5: Build Tableau Public Dashboard

Status: Waiting on Snowflake phase

Tasks:

- Connect `homestand_summary.csv`
- Connect `promotion_scorecard.csv`
- Connect `crm_follow_up_queue.csv`
- Build Homestand Intelligence page
- Build Promotion Scorecard page
- Build CRM Follow-Up Queue page
- Add source note to each dashboard
- Publish workbook to Tableau Public

---

### Priority 6: Add Tableau Link to README

Status: Waiting on Tableau dashboard

Tasks:

- Publish Tableau Public workbook
- Copy Tableau Public link
- Add link to README
- Commit README update

---

### Priority 7: Add Dashboard Screenshots

Status: Waiting on Tableau dashboard

Recommended folder:

- `images/`

Suggested files:

- `images/homestand_intelligence.png`
- `images/promotion_scorecard.png`
- `images/crm_follow_up_queue.png`

---

### Priority 8: Final Portfolio Polish

Status: Not started

Tasks:

- Add final executive summary
- Add dashboard screenshots
- Add Tableau Public link
- Add Snowflake/SQL summary
- Confirm synthetic data disclaimer is clear
- Confirm no claim of internal Trash Pandas access

Potential file:

- `PORTFOLIO_WRITEUP.md`

---

### Priority 9: LinkedIn Post

Status: Not started

Potential file:

- `LINKEDIN_POST_DRAFT.md`

Focus:

- Coach-to-analyst story
- Sports business reporting
- Connected data
- Snowflake + SQL + Tableau
- GitHub project link
- Tableau dashboard link

---

## Current Build Definition

The current build is complete when:

- Python-generated source and synthetic files exist
- Final exports exist
- Final exports pass quality checks
- Snowflake reporting layer is built
- SQL validation queries pass
- Business-question SQL file exists
- Tableau Public dashboard is published
- README links to Tableau Public
- README clearly explains public vs synthetic data
- README explains Snowflake/SQL reporting layer

Current current build status:

- Data generation: Complete
- Quality checks: Complete
- Final exports: Complete
- Snowflake reporting layer: Not started
- SQL files: Not started
- Tableau dashboard: Not started
- Final portfolio polish: Not started

---

## Next Immediate Step

Create the Snowflake load guide.

Start with:

- `SNOWFLAKE_LOAD_GUIDE.md`

Then create SQL files in this order:

1. `sql/00_snowflake_setup.sql`
2. `sql/01_create_export_tables.sql`
3. `sql/02_load_export_tables.sql`
4. `sql/03_validate_export_tables.sql`
5. `sql/04_create_analytics_views.sql`
6. `sql/05_business_question_queries.sql`

Do not start Tableau until Snowflake setup and SQL validation are documented.