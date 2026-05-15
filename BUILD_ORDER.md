# Build Order

## Purpose

This file defines the build sequence for the Trash Pandas Connected Reporting Pilot.

The project should be built in a controlled order:

1. Lock the business logic.
2. Prepare public data.
3. Generate synthetic internal-style data.
4. Build Snowflake tables and views.
5. Export Tableau-ready files.
6. Build the Tableau Public dashboard.
7. Package the project for portfolio review.

Snowflake should not be opened until the planning files, public data, synthetic data plan, and first CSV outputs are ready.

---

## Current Project Direction

Project name:

Trash Pandas Connected Reporting Pilot

Primary technical platform:

Snowflake

Supporting tools:

- Python
- SQL
- Tableau Public
- Excel
- GitHub
- VS Code

Primary business question:

Which games and promotions created the most total fan value beyond attendance, and which fans or accounts should sales and marketing follow up with first?

MVP dashboard pages:

1. Homestand Intelligence
2. Promotion Performance Scorecard
3. CRM Follow-Up Queue

---

## Phase 1: Project Reset

Status: Complete

Tasks:

- Rename project from CRM Analytics Pilot to Connected Reporting Pilot
- Rename GitHub repo
- Update local repo folder
- Update remote URL
- Create updated folder structure
- Create planning files
- Commit project reset

Key files:

- PROJECT_CHARTER.md
- BUSINESS_QUESTIONS.md
- DATA_SOURCE_MAP.md
- DATA_ASSUMPTIONS.md
- SYNTHETIC_DATA_PLAN.md
- SNOWFLAKE_SCHEMA_PLAN.md
- DASHBOARD_PLAN.md
- BUILD_ORDER.md

---

## Phase 2: Planning Documents

Status: In progress

Goal:

Create the planning foundation before writing data scripts or opening Snowflake.

Required files:

| File | Purpose |
|---|---|
| PROJECT_CHARTER.md | Defines the project purpose, scope, audience, and MVP |
| BUSINESS_QUESTIONS.md | Locks the business questions |
| DATA_SOURCE_MAP.md | Maps business sources, grain, fields, and joins |
| DATA_ASSUMPTIONS.md | Documents public, synthetic, and derived data assumptions |
| SYNTHETIC_DATA_PLAN.md | Defines synthetic data rules and scoring logic |
| SNOWFLAKE_SCHEMA_PLAN.md | Defines Snowflake architecture and table/view plan |
| DASHBOARD_PLAN.md | Defines Tableau dashboard pages and metrics |
| BUILD_ORDER.md | Defines the build sequence |

Completion criteria:

- Each file clearly supports the connected reporting story
- Public, synthetic, and derived data are clearly separated
- MVP boundaries are documented
- Business questions are tied to dashboard outputs
- Snowflake structure is planned before opening the trial

---

## Phase 3: Public Data Prep

Goal:

Prepare the public schedule, promotion, and attendance foundation for 2023-2025 home games.

Public data files:

| File | Folder | Purpose |
|---|---|---|
| games.csv | data/public | Game schedule and home-game context |
| promotions.csv | data/public | Promotion names and promo categories |
| attendance.csv | data/public | Announced attendance where available |

Required fields for games.csv:

| Field | Notes |
|---|---|
| game_id | Project-generated key |
| season | 2023, 2024, or 2025 |
| game_date | Game date |
| home_away | Home only for MVP |
| opponent | Opposing team |
| day_of_week | Derived from game date |
| start_time | If available |
| homestand_id | Manually assigned |
| game_number_in_homestand | Manual or derived |
| month | Derived from game date |
| weekend_flag | Friday, Saturday, or Sunday |

Required fields for promotions.csv:

| Field | Notes |
|---|---|
| promo_id | Project-generated key |
| game_id | Connected game |
| promo_name | Public promotion name |
| promo_category | Standardized category |
| promo_type | Theme, giveaway, fireworks, etc. |
| primary_promo_flag | Identifies main promo |
| sponsor_attached_flag | Context only |
| giveaway_flag | Promo tag |
| fireworks_flag | Promo tag |
| theme_night_flag | Promo tag |
| family_flag | Promo tag |
| dog_day_flag | Promo tag |
| jersey_auction_flag | Promo tag |

Required fields for attendance.csv:

| Field | Notes |
|---|---|
| attendance_id | Project-generated key |
| game_id | Connected game |
| game_date | Game date |
| announced_attendance | Public attendance anchor |
| attendance_source | Source note |
| attendance_note | Reconciliation note |

Completion criteria:

- 2023-2025 home games are collected
- Each home game has a game_id
- Homestand IDs are assigned
- Promotions are standardized into categories
- Announced attendance is separated from scanned attendance
- Public data limitations are documented

---

## Phase 4: Python Public Data Cleaning

Goal:

Use Python to clean and standardize public data before generating synthetic records.

Python scripts:

| Script | Purpose |
|---|---|
| 01_clean_public_games.py | Clean schedule and create game fields |
| 02_clean_public_promotions.py | Standardize promotion data |
| 03_clean_public_attendance.py | Clean announced attendance |
| 99_public_data_quality_checks.py | Validate public data files |

Outputs:

| File | Folder |
|---|---|
| games_clean.csv | data/processed |
| promotions_clean.csv | data/processed |
| attendance_clean.csv | data/processed |
| public_data_quality_summary.csv | data/processed |

Completion criteria:

- No missing game_id values
- No duplicate game_id values
- Home games only in MVP files
- Promo records connect to valid game_id values
- Attendance records connect to valid game_id values
- Homestand IDs are populated

---

## Phase 5: Synthetic Data Generation

Goal:

Generate realistic internal-style business data around the public game schedule.

Synthetic files:

| File | Purpose |
|---|---|
| fans.csv | Fan account base |
| fan_segments.csv | Fan segment assignments |
| ticket_orders.csv | Ticket order headers |
| ticket_order_items.csv | Ticket/order item details |
| ticket_scans.csv | Scan and no-show behavior |
| group_accounts.csv | Group account base |
| group_sales.csv | Group sales records |
| merch_transactions.csv | Merch purchase behavior |
| concession_transactions.csv | Concession purchase behavior |
| sponsorship_activations.csv | Sponsor context |
| fan_engagement.csv | Engagement signals |
| follow_up_opportunity_pool.csv | Qualified opportunities |
| crm_follow_up_tasks.csv | Prioritized task queue |

Python scripts:

| Script | Purpose |
|---|---|
| 04_generate_fans.py | Generate fan account base |
| 05_generate_fan_segments.py | Assign fan segments |
| 06_generate_ticket_orders.py | Generate ticket demand |
| 07_generate_ticket_order_items.py | Generate ticket details |
| 08_generate_ticket_scans.py | Generate scan/no-show behavior |
| 09_generate_group_accounts.py | Generate group accounts |
| 10_generate_group_sales.py | Generate group purchases |
| 11_generate_merch_transactions.py | Generate merch behavior |
| 12_generate_concession_transactions.py | Generate concession behavior |
| 13_generate_sponsorship_activations.py | Generate sponsorship context |
| 14_generate_fan_engagement.py | Generate engagement records |
| 15_generate_follow_up_opportunity_pool.py | Generate opportunity pool |
| 16_generate_crm_follow_up_tasks.py | Generate CRM queue |
| 99_synthetic_data_quality_checks.py | Validate synthetic outputs |

Completion criteria:

- Fan behavior varies across segments
- Not every fan attends every game
- Merch match rate follows 60-75% fan_id match rule
- Concession match rate follows 35-55% fan_id match rule
- Ticket sales and scanned attendance are distinct
- No-show logic supports recovery targeting
- Group accounts are scored separately
- Synthetic data is clearly labeled

---

## Phase 6: Snowflake Trial Setup

Goal:

Open the Snowflake trial only after the CSV outputs and SQL plan are ready.

Snowflake setup tasks:

- Create Snowflake trial account
- Create database
- Create RAW schema
- Create STAGING schema
- Create ANALYTICS schema
- Create EXPORTS schema
- Create warehouse
- Create file format for CSV loading
- Load public and synthetic CSVs

Database:

TRASH_PANDAS_CONNECTED_REPORTING

Schemas:

- RAW
- STAGING
- ANALYTICS
- EXPORTS

Completion criteria:

- Snowflake account is active
- Database and schemas exist
- RAW tables are created
- CSV files are loaded
- Initial row counts are validated

---

## Phase 7: Snowflake RAW Layer

Goal:

Load source CSV files into RAW tables with minimal transformation.

SQL folder:

sql/raw

SQL files:

| File | Purpose |
|---|---|
| 01_create_raw_tables.sql | Create RAW tables |
| 02_load_raw_tables.sql | Load CSV files into RAW tables |
| 03_raw_row_count_checks.sql | Validate row counts |

Completion criteria:

- Each CSV has a matching RAW table
- Row counts match source files
- No source file is missing
- Synthetic tables are named clearly

---

## Phase 8: Snowflake STAGING Layer

Goal:

Clean, standardize, and prepare data for joins.

SQL folder:

sql/staging

SQL files:

| File | Purpose |
|---|---|
| 01_create_staging_tables.sql | Create STAGING tables |
| 02_build_staging_tables.sql | Insert cleaned data |
| 03_staging_key_checks.sql | Validate keys and required fields |

Completion criteria:

- Data types are cleaned
- Dates are properly cast
- Primary keys are unique
- Join keys are populated
- Invalid records are flagged or excluded
- Fan-linked merch and concession records have valid fan IDs when matched

---

## Phase 9: Snowflake ANALYTICS Layer

Goal:

Build views that answer the project’s business questions.

SQL folder:

sql/analytics

Required views:

| View | Purpose |
|---|---|
| VW_GAME_CONNECTED_SUMMARY | Game-level connected performance |
| VW_HOMESTAND_SUMMARY | Homestand performance |
| VW_PROMOTION_SCORECARD | Promotion recommendation logic |
| VW_FAN_TOTAL_VALUE_SUMMARY | Fan-level value summary |
| VW_HIDDEN_HIGH_VALUE_FANS | Fans missed by ticket-only reporting |
| VW_CRM_FOLLOW_UP_QUEUE | Prioritized follow-up queue |
| VW_GROUP_ACCOUNT_PRIORITY | Group renewal and upsell |
| VW_NO_SHOW_RECOVERY_TARGETS | Valuable no-show recovery |
| VW_MERCH_CONCESSION_FAN_BEHAVIOR | In-park spend behavior |
| VW_DATA_SOURCE_COVERAGE | Data connection summary |

Completion criteria:

- Game-level metrics are calculated
- Promotion recommendation labels are created
- Fan-level value metrics are created
- Follow-up queue is prioritized
- Group accounts have separate scoring
- Hidden high-value fans are identified
- No-show recovery targets are filtered correctly

---

## Phase 10: Snowflake EXPORTS Layer

Goal:

Create flat Tableau-ready outputs.

SQL folder:

sql/exports

Exports:

| Export | Dashboard |
|---|---|
| TABLEAU_GAME_CONNECTED_SUMMARY | Homestand Intelligence |
| TABLEAU_HOMESTAND_SUMMARY | Homestand Intelligence |
| TABLEAU_PROMOTION_SCORECARD | Promotion Scorecard |
| TABLEAU_CRM_FOLLOW_UP_QUEUE | CRM Follow-Up Queue |
| TABLEAU_GROUP_ACCOUNT_PRIORITY | CRM Follow-Up Queue |
| TABLEAU_FAN_VALUE_SEGMENTS | Fan segment analysis |

Completion criteria:

- Exports are flat and easy to use in Tableau
- Field names are dashboard-friendly
- Synthetic fields are labeled clearly
- CSV exports are saved to data/tableau_exports

---

## Phase 11: Tableau Public Build

Goal:

Build three Tableau Public dashboard pages.

Dashboard pages:

1. Homestand Intelligence
2. Promotion Performance Scorecard
3. CRM Follow-Up Queue

Completion criteria:

- Each page has a clear business question
- KPIs match the business logic
- Filters are useful but not excessive
- Synthetic data note is visible
- Dashboard tells an executive-ready story
- Screenshots are saved to screenshots folder

---

## Phase 12: Documentation and Portfolio Packaging

Goal:

Prepare the project for GitHub, recruiters, and potential sports business conversations.

Files to finalize:

| File | Purpose |
|---|---|
| README.md | Main project story |
| docs/executive_summary.md | Leadership-facing summary |
| docs/methodology.md | Data and modeling approach |
| docs/limitations.md | Public vs synthetic limitations |
| docs/portfolio_story.md | Recruiter-facing narrative |

README sections:

- Project title
- One-sentence pitch
- Business problem
- Why connected reporting matters
- Tools used
- Data sources
- Public vs synthetic data note
- Snowflake architecture
- Dashboard pages
- Key business questions
- Key insights
- Limitations
- Future improvements

Completion criteria:

- README explains the project clearly
- Screenshots are included
- Synthetic data is clearly disclosed
- Snowflake workflow is documented
- Dashboard links are included
- GitHub repo is clean

---

## Phase 13: Final Review

Goal:

Make sure the project is credible, focused, and useful.

Review checklist:

- Does the project answer the main business question?
- Does the project avoid fake certainty?
- Are public and synthetic data clearly separated?
- Does the Snowflake structure make sense?
- Do the dashboards support real business decisions?
- Is the scope realistic for a portfolio project?
- Would a recruiter understand the technical value?
- Would a sports executive understand the business value?

---

## MVP Build Order Summary

1. Finish planning documents
2. Collect public data
3. Clean public data with Python
4. Generate synthetic internal-style data
5. Run quality checks
6. Open Snowflake trial
7. Build RAW layer
8. Build STAGING layer
9. Build ANALYTICS views
10. Build EXPORTS tables
11. Export Tableau-ready CSVs
12. Build Tableau Public dashboard
13. Finalize README and portfolio documentation

---

## Next Immediate Build Step

After this planning phase is complete, the next hands-on step is public data prep.

Start with:

data/public/games.csv

Then build:

data/public/promotions.csv

Then build:

data/public/attendance.csv

Do not start synthetic data generation until the public game foundation is clean.