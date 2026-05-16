# Task Tracker

## Project

Trash Pandas Connected Reporting Pilot

## Last Updated

2026-05-16

## Current Project Status

The Python data generation, synthetic data modeling, quality checks, Tableau-ready export files, and Snowflake reporting layer are complete.

The current phase is **Tableau Public dashboard build**.

Current phase:

Tableau Public dashboard build using the final export files.

Snowflake status:

Complete.

Completed Snowflake files:

- `SNOWFLAKE_LOAD_GUIDE.md`
- `SNOWFLAKE_SCHEMA_PLAN.md`
- `sql/00_snowflake_setup.sql`
- `sql/01_create_export_tables.sql`
- `sql/02_load_export_tables.sql`
- `sql/03_validate_export_tables.sql`
- `sql/04_create_analytics_views.sql`
- `sql/05_business_question_queries.sql`

Tableau comes after Snowflake validation.

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

- App, social, and offer-response signals were not modeled for the current build.
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

### 16. Snowflake Reporting Layer

Status: Complete

Completed:

- Created Snowflake load guide
- Created Snowflake schema plan
- Created warehouse, database, schemas, file format, and internal stage
- Created raw export tables for the three final reporting exports
- Loaded final exports into Snowflake
- Validated row counts and key totals
- Created analytics views
- Created business-question SQL queries
- Confirmed Snowflake layer supports the project’s connected reporting story

Key files:

- `SNOWFLAKE_LOAD_GUIDE.md`
- `SNOWFLAKE_SCHEMA_PLAN.md`
- `sql/00_snowflake_setup.sql`
- `sql/01_create_export_tables.sql`
- `sql/02_load_export_tables.sql`
- `sql/03_validate_export_tables.sql`
- `sql/04_create_analytics_views.sql`
- `sql/05_business_question_queries.sql`

Snowflake validation targets:

- Homestand row count: 34
- Promotion scorecard row count: 233
- CRM queue row count: 15,000
- Homestand tickets sold: 1,274,234
- Homestand scanned attendance: 1,126,560
- Homestand total revenue indicator: 28,655,060.87
- CRM future revenue opportunity: 12,605,270.19

---

### 17. Documentation Updates

Status: In progress

Completed:

- Updated README for connected reporting story
- Updated dashboard plan around final exports
- Added Tableau build guide
- Updated build order for dashboard phase
- Added Snowflake schema plan
- Added Snowflake load guide
- Added Snowflake SQL files to repo

Still needed:

- Add Tableau Public link after dashboard is published
- Add dashboard screenshots after dashboard is built
- Add final portfolio polish after dashboard is published

Key files:

- `README.md`
- `DASHBOARD_PLAN.md`
- `TABLEAU_BUILD_GUIDE.md`
- `BUILD_ORDER.md`
- `TASK_TRACKER.md`
- `SNOWFLAKE_LOAD_GUIDE.md`
- `SNOWFLAKE_SCHEMA_PLAN.md`

---

## Current Required Phase

### Phase 18: Tableau Public Dashboard Build

Status: Next

Goal:

Build the three-page Tableau Public dashboard using the final dashboard-ready export files.

Primary data sources:

1. `data/exports/homestand_summary.csv`
2. `data/exports/promotion_scorecard.csv`
3. `data/exports/crm_follow_up_queue.csv`

Dashboard pages:

1. Homestand Intelligence
2. Promotion Performance Scorecard
3. CRM Follow-Up Queue

Status note:

The Snowflake reporting layer has been created, loaded, validated, and documented. Tableau Public will use the final CSV exports so the published dashboard remains accessible and portfolio-friendly.

---

## Tableau Phase

### Phase 18: Tableau Public Dashboard Build

Status: Next

Goal:

Build the three-page Tableau Public dashboard using final export files.

Primary data sources:

1. `data/exports/homestand_summary.csv`
2. `data/exports/promotion_scorecard.csv`
3. `data/exports/crm_follow_up_queue.csv`

Dashboard pages:

1. Homestand Intelligence
2. Promotion Performance Scorecard
3. CRM Follow-Up Queue

Primary guide:

- `TABLEAU_BUILD_GUIDE.md`

Status note:

Tableau Public will use CSV exports.

Snowflake has already been used as the warehouse/reporting layer and SQL validation layer.

---

## Current To-Do List

### Priority 1: Build Tableau Public Dashboard

Status: Next

Primary files:

- `data/exports/homestand_summary.csv`
- `data/exports/promotion_scorecard.csv`
- `data/exports/crm_follow_up_queue.csv`

Dashboard pages:

1. Homestand Intelligence
2. Promotion Performance Scorecard
3. CRM Follow-Up Queue

---

### Priority 2: Add Tableau Link to README

Status: Waiting on Tableau dashboard

Tasks:

- Publish Tableau Public workbook
- Copy Tableau Public link
- Add link to README
- Commit README update

---

### Priority 3: Add Dashboard Screenshots

Status: Waiting on Tableau dashboard

Recommended folder:

- `images/`

Suggested files:

- `images/homestand_intelligence.png`
- `images/promotion_scorecard.png`
- `images/crm_follow_up_queue.png`

---

### Priority 4: Final Portfolio Polish

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

### Priority 5: LinkedIn Post

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

Current build status:

- Data generation: Complete
- Quality checks: Complete
- Final exports: Complete
- Snowflake reporting layer: Complete
- SQL files: Complete
- Tableau dashboard: Not started
- Final portfolio polish: Not started

---

## Next Immediate Step

Build the Tableau Public dashboard.

Start with:

- `TABLEAU_BUILD_GUIDE.md`

Use these final export files:

1. `data/exports/homestand_summary.csv`
2. `data/exports/promotion_scorecard.csv`
3. `data/exports/crm_follow_up_queue.csv`

Do not change the Snowflake layer unless the dashboard build reveals a field issue.