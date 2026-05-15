# Snowflake Schema Plan

## Project

Trash Pandas Connected Reporting Pilot

## Purpose

This file defines the Snowflake reporting-layer design for the Trash Pandas Connected Reporting Pilot.

The goal is to show how separate business reports can be loaded into a cloud warehouse, validated with SQL, organized into reporting views, and used to answer leadership-level business questions.

This file explains **what the Snowflake structure should look like**.

The separate `SNOWFLAKE_LOAD_GUIDE.md` will explain **how to load the files and run the workflow**.

---

## Portfolio Story

The project follows this flow:

1. Python generates and validates public and synthetic data.
2. Final CSV exports are created for connected reporting.
3. Snowflake stores those exports in a warehouse-style reporting layer.
4. SQL validates the loaded tables.
5. SQL views prepare the data for analysis.
6. Tableau Public visualizes the final dashboard-ready exports.

Snowflake is included to prove that this is not just a CSV project.

It is a connected reporting pilot with a warehouse layer, SQL validation, business-question queries, and dashboard-ready outputs.

---

## Current Build Scope

For the current build, Snowflake will load the three final reporting exports:

| Export File | Snowflake Table | Grain |
|---|---|---|
| `data/exports/homestand_summary.csv` | `RAW.HOMESTAND_SUMMARY` | One row per homestand |
| `data/exports/promotion_scorecard.csv` | `RAW.PROMOTION_SCORECARD` | One row per promotion per game |
| `data/exports/crm_follow_up_queue.csv` | `RAW.CRM_FOLLOW_UP_QUEUE` | One row per CRM follow-up task |

This current build does **not** load every raw public or synthetic source table into Snowflake.

That can be added later.

The first goal is to prove that the final connected reporting layer can be loaded, validated, queried, and organized inside Snowflake.

---

## Database Design

Use one database:

`TRASH_PANDAS_CONNECTED_REPORTING`

Purpose:

Store the connected reporting pilot tables, validation layer, and analytics views.

---

## Warehouse Design

Use one warehouse:

`TP_REPORTING_WH`

Recommended setting:

- Size: `XSMALL`
- Auto suspend: `60` seconds
- Auto resume: `TRUE`

Reason:

This is a portfolio project with lightweight CSV files. An XSMALL warehouse is enough.

---

## Schema Design

Use three schemas:

| Schema | Purpose |
|---|---|
| `RAW` | Stores loaded CSV export tables |
| `ANALYTICS` | Stores reporting-ready views |
| `QA` | Stores validation logic, check queries, or future QA tables |

---

## Object Naming Rules

Use uppercase Snowflake object names.

### Database

`TRASH_PANDAS_CONNECTED_REPORTING`

### Warehouse

`TP_REPORTING_WH`

### Schemas

- `RAW`
- `ANALYTICS`
- `QA`

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

### Stage

`RAW.TP_EXPORT_STAGE`

### File Format

`RAW.CSV_EXPORT_FORMAT`

---

## Data Layer Model

### Layer 1: Final Export Files

Local CSV exports created by Python:

- `homestand_summary.csv`
- `promotion_scorecard.csv`
- `crm_follow_up_queue.csv`

These are stored locally in:

`data/exports/`

---

### Layer 2: Snowflake Internal Stage

Files are uploaded to:

`RAW.TP_EXPORT_STAGE`

Purpose:

Hold CSV files before loading them into Snowflake tables.

---

### Layer 3: RAW Tables

The staged CSVs load into:

- `RAW.HOMESTAND_SUMMARY`
- `RAW.PROMOTION_SCORECARD`
- `RAW.CRM_FOLLOW_UP_QUEUE`

Purpose:

Preserve the export data as loaded from the final CSV files.

RAW tables should stay close to the export structure.

---

### Layer 4: ANALYTICS Views

Analytics views clean up names, enforce useful field ordering, and prepare the data for SQL analysis.

Core views:

- `ANALYTICS.V_HOMESTAND_SUMMARY`
- `ANALYTICS.V_PROMOTION_SCORECARD`
- `ANALYTICS.V_CRM_FOLLOW_UP_QUEUE`

Helper views:

- `ANALYTICS.V_EXECUTIVE_HOMESTAND_OVERVIEW`
- `ANALYTICS.V_PROMOTION_RECOMMENDATION_SUMMARY`
- `ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY`

Purpose:

Make the reporting layer easier to query and explain.

---

### Layer 5: Business Question Queries

SQL queries answer the core project questions:

- Which homestands created the most total value?
- Which promotions should return, be reworked, retired, or reviewed?
- Which promotions created attendance lift but weak revenue lift?
- Which promotions drove in-park spend?
- Which homestands had the most no-show recovery opportunity?
- Which fans or accounts should be prioritized for follow-up?
- Which action buckets drive the CRM queue?
- Which teams own the follow-up workload?

These queries live in:

`sql/05_business_question_queries.sql`

---

## Final Export Table: RAW.HOMESTAND_SUMMARY

### Purpose

Stores one row per homestand with connected business metrics.

This table supports the Homestand Intelligence dashboard page.

### Grain

One row per homestand.

### Primary Key Logic

Logical key:

- `season`
- `homestand_id`

### Core Fields

| Field | Purpose |
|---|---|
| `season` | Season year |
| `homestand_id` | Homestand identifier |
| `homestand_start_date` | First game date in homestand |
| `homestand_end_date` | Last game date in homestand |
| `game_count` | Number of games in homestand |
| `opponents` | Opponents played during homestand |
| `tickets_sold` | Synthetic ticket demand |
| `scanned_attendance` | Synthetic attendance conversion |
| `scan_rate` | Scanned attendance divided by tickets sold |
| `no_show_ticket_quantity` | Tickets sold but not scanned |
| `no_show_rate` | No-show quantity divided by tickets sold |
| `net_ticket_revenue` | Synthetic ticket revenue |
| `merch_net_sales` | Synthetic merch revenue |
| `concession_net_sales` | Synthetic concession revenue |
| `in_park_spend_per_scanned_fan` | Merch plus concessions divided by scanned attendance |
| `total_revenue_indicator` | Synthetic total value measure |
| `follow_up_opportunity_count` | Follow-up opportunities created |
| `crm_follow_up_task_count` | CRM tasks created |
| `homestand_total_value_index` | Weighted value score |
| `recommended_focus` | Recommended action area |

### Business Use

Used to answer:

- Which homestands created the most total value?
- Which homestands had weak scan conversion?
- Which homestands created the strongest in-park value?
- Which homestands created follow-up opportunities?
- What should leadership focus on after each homestand?

---

## Final Export Table: RAW.PROMOTION_SCORECARD

### Purpose

Stores one row per promotion per game with connected promotion performance metrics.

This table supports the Promotion Performance Scorecard dashboard page.

### Grain

One row per promotion per game.

### Primary Key Logic

Logical key:

- `promo_id`

### Core Fields

| Field | Purpose |
|---|---|
| `promo_id` | Promotion identifier |
| `game_id` | Game identifier |
| `season` | Season year |
| `game_date` | Game date |
| `homestand_id` | Homestand identifier |
| `opponent` | Opponent |
| `day_of_week` | Day of week |
| `promo_name` | Promotion name |
| `promo_category` | Standardized promotion category |
| `promo_type` | Promotion type |
| `tickets_sold` | Synthetic ticket demand |
| `scanned_attendance` | Synthetic attendance conversion |
| `scan_rate` | Scanned attendance divided by tickets sold |
| `no_show_rate` | No-show rate |
| `group_tickets` | Group tickets tied to game |
| `merch_net_sales` | Merch sales tied to game |
| `concession_net_sales` | Concession sales tied to game |
| `repeat_buyer_rate` | Repeat buyer signal |
| `scanned_attendance_lift_vs_slot` | Lift compared to same season/day slot |
| `revenue_lift_per_scanned_fan` | Revenue lift compared to same season/day slot |
| `merch_lift_per_scanned_fan` | Merch lift compared to same season/day slot |
| `concession_lift_per_scanned_fan` | Concession lift compared to same season/day slot |
| `total_value_index` | Weighted promotion value score |
| `recommendation` | Return, rework, retire, or review |
| `recommendation_reason` | Plain-language explanation |

### Business Use

Used to answer:

- Which promotions should return?
- Which promotions should be reworked?
- Which promotions should be retired?
- Which promotions need review?
- Which promotions drove wallets, not just crowds?
- Which promotion categories created the strongest connected value?

---

## Final Export Table: RAW.CRM_FOLLOW_UP_QUEUE

### Purpose

Stores one row per prioritized CRM follow-up task.

This table supports the CRM Follow-Up Queue dashboard page.

### Grain

One row per CRM follow-up task.

### Primary Key Logic

Logical key:

- `follow_up_id`

### Core Fields

| Field | Purpose |
|---|---|
| `priority_rank` | Queue rank |
| `follow_up_id` | CRM task identifier |
| `opportunity_id` | Source opportunity identifier |
| `entity_type` | Fan or account |
| `entity_id` | Fan ID or account ID |
| `entity_display_name` | Display value for queue |
| `assigned_team` | Sales, service, marketing, or group sales |
| `assigned_owner` | Synthetic task owner |
| `executive_action_bucket` | Recover, upgrade, retain, or renew |
| `priority_score` | Rule-based task priority score |
| `priority_band` | High or medium |
| `opportunity_type` | Reason for follow-up |
| `opportunity_reason` | Explanation of signal |
| `source_signal` | Source behavior that created opportunity |
| `suggested_action` | Recommended next action |
| `due_date` | Suggested due date |
| `future_revenue_opportunity` | Synthetic future opportunity value |
| `repeat_likelihood_score` | Rule-based repeat score |
| `upgrade_potential_score` | Rule-based upgrade score |
| `entity_total_value` | Connected fan/account value |
| `entity_ticket_revenue` | Ticket or group ticket value |
| `entity_in_park_revenue` | Fan merch plus concession value |
| `game_id` | Game tied to opportunity |
| `season` | Season year |
| `homestand_id` | Homestand identifier |
| `promo_names` | Promotions tied to game |
| `promo_categories` | Promotion categories tied to game |
| `fan_segments` | Fan segment labels |
| `account_type` | Group account type |
| `account_group_revenue` | Group account revenue |

### Business Use

Used to answer:

- Who should sales or marketing contact first?
- Which fans or accounts should be recovered, upgraded, retained, or renewed?
- Which team owns each action?
- Which opportunities carry the most future value?
- Which fan/account behaviors create the queue?

---

## File Format Design

Use one CSV file format:

`RAW.CSV_EXPORT_FORMAT`

Recommended options:

- Type: CSV
- Field delimiter: comma
- Skip header: 1
- Field optionally enclosed by double quote
- Empty field as null: false
- Trim space: true

Reason:

The final exports are standard CSV files with headers and quoted descriptions where needed.

---

## Internal Stage Design

Use one internal stage:

`RAW.TP_EXPORT_STAGE`

Purpose:

Hold final export CSVs before loading them into raw tables.

Expected staged files:

- `homestand_summary.csv`
- `promotion_scorecard.csv`
- `crm_follow_up_queue.csv`

---

## SQL File Plan

Create these SQL files:

| File | Purpose |
|---|---|
| `sql/00_snowflake_setup.sql` | Create warehouse, database, schemas, file format, and stage |
| `sql/01_create_export_tables.sql` | Create raw tables matching final export files |
| `sql/02_load_export_tables.sql` | Load staged CSV exports into raw tables |
| `sql/03_validate_export_tables.sql` | Validate row counts and key totals |
| `sql/04_create_analytics_views.sql` | Create analytics views and helper summary views |
| `sql/05_business_question_queries.sql` | Answer the project’s core business questions |

---

## Validation Plan

Validation should confirm that Snowflake loaded the same values produced by Python.

### Required Row Count Checks

| Table | Expected Rows |
|---|---:|
| `RAW.HOMESTAND_SUMMARY` | 34 |
| `RAW.PROMOTION_SCORECARD` | 233 |
| `RAW.CRM_FOLLOW_UP_QUEUE` | 15,000 |

### Required Total Checks

| Metric | Expected Value |
|---|---:|
| Homestand tickets sold | 1,274,234 |
| Homestand scanned attendance | 1,126,560 |
| Homestand total revenue indicator | 28,655,060.87 |
| CRM future revenue opportunity | 12,605,270.19 |

### Required Logic Checks

Validation SQL should check:

- No duplicate homestand keys
- No duplicate promo IDs
- No duplicate follow-up IDs
- Promotion recommendations are valid
- CRM entity mapping is valid
- Priority ranks are unique
- Scan rates are between 0 and 1
- No-show rates are between 0 and 1
- Revenue values are non-negative

---

## Analytics View Plan

### ANALYTICS.V_HOMESTAND_SUMMARY

Purpose:

Clean reporting view for homestand performance.

Use cases:

- Executive dashboard
- Homestand ranking
- Tickets sold vs scanned attendance
- Revenue mix
- Recommended focus

---

### ANALYTICS.V_PROMOTION_SCORECARD

Purpose:

Clean reporting view for promotion decisions.

Use cases:

- Promotion recommendation summary
- Promotion scorecard table
- Attendance lift vs revenue lift
- In-park spend lift
- Repeat buyer signal

---

### ANALYTICS.V_CRM_FOLLOW_UP_QUEUE

Purpose:

Clean reporting view for CRM prioritization.

Use cases:

- Sales/service/marketing queue
- Action bucket workload
- Priority queue table
- Hidden fan value view
- Future opportunity tracking

---

### ANALYTICS.V_EXECUTIVE_HOMESTAND_OVERVIEW

Purpose:

Executive summary view for leadership.

Recommended fields:

- season
- homestand_id
- game_count
- tickets_sold
- scanned_attendance
- scan_rate
- no_show_rate
- total_revenue_indicator
- homestand_total_value_index
- recommended_focus

---

### ANALYTICS.V_PROMOTION_RECOMMENDATION_SUMMARY

Purpose:

Summarize promotion decision outcomes.

Recommended fields:

- season
- promo_category
- recommendation
- promotion_count
- avg_total_value_index
- avg_scanned_attendance
- avg_revenue_per_scanned_fan
- avg_in_park_spend_per_scanned_fan

---

### ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY

Purpose:

Summarize CRM follow-up workload.

Recommended fields:

- assigned_team
- executive_action_bucket
- priority_band
- task_count
- total_future_revenue_opportunity
- avg_priority_score

---

## Business Question SQL Plan

The final SQL query file should answer:

### 1. Which homestands created the most total value?

Use:

- `ANALYTICS.V_HOMESTAND_SUMMARY`

Sort by:

- `total_revenue_indicator`
- `homestand_total_value_index`

---

### 2. Which promotions should return?

Use:

- `ANALYTICS.V_PROMOTION_SCORECARD`

Filter:

- `recommendation = 'return'`

---

### 3. Which promotions should be reworked?

Use:

- `ANALYTICS.V_PROMOTION_SCORECARD`

Filter:

- `recommendation = 'rework'`

---

### 4. Which promotions should be retired?

Use:

- `ANALYTICS.V_PROMOTION_SCORECARD`

Filter:

- `recommendation = 'retire'`

---

### 5. Which promotions drove attendance lift but weak revenue lift?

Use:

- `ANALYTICS.V_PROMOTION_SCORECARD`

Filter:

- `scanned_attendance_lift_vs_slot > 0`
- `revenue_lift_per_scanned_fan < 0`

---

### 6. Which promotions drove in-park spend?

Use:

- `ANALYTICS.V_PROMOTION_SCORECARD`

Sort by:

- `in_park_spend_per_scanned_fan`
- `merch_lift_per_scanned_fan`
- `concession_lift_per_scanned_fan`

---

### 7. Which homestands had the most no-show recovery opportunity?

Use:

- `ANALYTICS.V_HOMESTAND_SUMMARY`

Sort by:

- `no_show_ticket_quantity`
- `no_show_rate`
- `follow_up_opportunity_count`

---

### 8. Which fans or accounts should be prioritized for follow-up?

Use:

- `ANALYTICS.V_CRM_FOLLOW_UP_QUEUE`

Sort by:

- `priority_rank`

---

### 9. Which CRM action buckets are driving the queue?

Use:

- `ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY`

Group by:

- `executive_action_bucket`

---

### 10. Which teams own the follow-up workload?

Use:

- `ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY`

Group by:

- `assigned_team`

---

## Relationship to Tableau Public

Tableau Public will use the final CSV exports directly.

This is intentional.

Snowflake proves the warehouse and SQL layer.

Tableau Public proves the dashboard and communication layer.

The final portfolio story should say:

> The connected reporting layer was modeled in Snowflake, validated with SQL, and visualized in Tableau Public using final dashboard-ready exports.

---

## Future Expansion

After the current build, Snowflake could also load the full source layer.

Future raw tables could include:

- `RAW.GAMES`
- `RAW.PROMOTIONS`
- `RAW.ATTENDANCE`
- `RAW.FANS`
- `RAW.FAN_SEGMENTS`
- `RAW.TICKET_ORDERS`
- `RAW.TICKET_ORDER_ITEMS`
- `RAW.TICKET_SCANS`
- `RAW.GROUP_ACCOUNTS`
- `RAW.GROUP_SALES`
- `RAW.MERCH_TRANSACTIONS`
- `RAW.CONCESSION_TRANSACTIONS`
- `RAW.SPONSORSHIP_ACTIVATIONS`
- `RAW.FAN_ENGAGEMENT`
- `RAW.FOLLOW_UP_OPPORTUNITIES`
- `RAW.CRM_FOLLOW_UPS`

Future schemas could include:

| Schema | Purpose |
|---|---|
| `STAGING` | Cleaned and typed source tables |
| `MARTS` | Business-specific reporting marts |
| `EXPORTS` | Final dashboard extracts |

This is optional.

The current build only needs the three final reporting exports.

---

## Completion Criteria

The Snowflake schema phase is complete when:

- `SNOWFLAKE_SCHEMA_PLAN.md` documents the structure
- `SNOWFLAKE_LOAD_GUIDE.md` documents the load process
- `sql/00_snowflake_setup.sql` creates the environment
- `sql/01_create_export_tables.sql` creates the raw tables
- `sql/02_load_export_tables.sql` loads the exports
- `sql/03_validate_export_tables.sql` validates row counts and totals
- `sql/04_create_analytics_views.sql` creates reporting views
- `sql/05_business_question_queries.sql` answers the main business questions

After this, Tableau Public dashboard build can begin.