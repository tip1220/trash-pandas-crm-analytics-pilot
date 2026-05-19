# Trash Pandas Connected Reporting Pilot

## Project Pitch

A proof-of-concept showing how a growth-market sports organization could connect separate business data sources into one reporting layer to uncover insights that siloed reports cannot show alone.

The project uses the Rocket City Trash Pandas as the portfolio case study.

The goal is not just to build a dashboard.

The goal is to show what becomes possible when ticketing, scans, promotions, merch, concessions, group sales, fan engagement, and CRM follow-up data are analyzed together.

## Business Problem

Sports teams often have useful data spread across multiple departments and systems:

- Ticketing
- Promotions
- Gate scans
- Group sales
- Retail / merch
- Concessions
- Sponsorship context
- Fan engagement
- CRM workflows

Each report can answer one narrow question.

Ticketing can show what was sold.

Scans can show who showed up.

Promotions can show what was offered.

POS data can show what fans spent.

CRM data can show who needs follow-up.

The real value comes when those sources connect.

This project demonstrates how separate reports could be pulled into one reporting layer so leadership can better understand:

- What created demand
- What converted into attendance
- What created value after fans arrived
- What created future sales or marketing opportunity
- Which fans or accounts should receive action next

## Important Data Note

This project does **not** use internal Trash Pandas data.

The project uses:

- Public schedule, promotion, game date, opponent, and announced attendance anchors where available
- Synthetic ticketing, scan, merch, concession, fan, group sales, engagement, and CRM follow-up data generated with Python
- Snowflake reporting layer design and SQL validation
- CSV exports prepared for Tableau Public

The synthetic data is used only to demonstrate structure, workflow, and business logic.

This project does not claim access to internal team systems.

## Why This Project Exists

The original idea was a CRM analytics pilot.

The stronger business problem became connected reporting.

A team may already have the data it needs.

The issue is that the data can live in separate reports, departments, tools, or workflows.

When that happens, leaders can see activity but miss the full business story.

This project shows how a growth-market sports organization could connect those pieces into one decision layer.

The main question is:

**What new decisions become possible when separate sports business data sources are connected?**

## Core Insight

A promotion may sell tickets.

But ticket sales alone do not prove business value.

When tickets, scans, no-shows, merch, concessions, group sales, engagement, and follow-up behavior are connected, the team can see whether that promotion created real value.

Connected reporting helps separate:

- Demand from attendance
- Attendance from in-park value
- Promotion activity from promotion impact
- Fan transactions from fan opportunity
- Reports from action

## Dashboard Story

The Tableau dashboard is built around one story:

**Siloed reports show activity. Connected reporting shows decisions.**

The dashboard follows this flow:

1. **Connected Homestand Intelligence**  
   What happened across demand, attendance conversion, in-park value, and future opportunity?

2. **Promotion Value Scorecard**  
   Which promotions created value beyond attendance?

3. **CRM Follow-Up Queue**  
   Which fans or accounts become actionable when behavior from multiple systems is connected?

## Final Dashboard Pages

### 1. Connected Homestand Intelligence

Business question:

Which homestands created value across ticket demand, attendance conversion, in-park spend, and follow-up opportunity?

This page compares homestands using connected business signals:

- Demand created
- Attendance converted
- Demand-to-attendance conversion
- Lost attendance opportunity
- Ticket revenue
- Value after arrival
- Revenue per scanned fan
- Actionable CRM signals
- Future value pipeline
- Connected value score
- Recommended focus

Why this page matters:

A homestand can sell well but still lose value through no-shows, weak in-park spend, or limited follow-up opportunity.

This page shows what leadership can learn only when ticketing, scans, merch, concessions, engagement, and CRM signals are connected.

### 2. Promotion Value Scorecard

Business question:

Which promotions created the most connected value, and should they return, be reworked, retired, or reviewed?

This page evaluates promotions using:

- Tickets sold
- Scanned attendance
- Scan rate
- No-show rate
- Group tickets
- Merch lift
- Concession lift
- Revenue per scanned fan
- Repeat buyer rate
- Fan engagement
- Follow-up opportunity
- Total value index
- Recommendation

Recommendation options:

- Return
- Rework
- Retire
- Review

Why this page matters:

A promotion should not be judged by attendance alone.

A strong promotion should help create attendance conversion, in-park spend, repeat behavior, group demand, or qualified follow-up opportunity.

### 3. CRM Follow-Up Queue

Business question:

Which fans and accounts become actionable once ticketing, scans, spend, engagement, and group behavior are connected?

This page turns connected behavior into a prioritized queue for:

- Sales
- Marketing
- Service
- Group sales

The queue includes:

- Fan/account ID
- Segment or account type
- Priority score
- Priority band
- Opportunity type
- Future revenue opportunity
- Repeat likelihood score
- Upgrade potential score
- Suggested action
- Assigned team
- Due date

Why this page matters:

Ticket data alone cannot tell the team who is worth contacting.

Connected reporting helps rank action instead of guessing.

## Final Tableau Export Files

Final dashboard-ready exports are stored in:

`data/exports/`

| File | Grain | Dashboard Use |
|---|---|---|
| `homestand_summary.csv` | One row per homestand | Connected Homestand Intelligence |
| `promotion_scorecard.csv` | One row per promotion per game | Promotion Value Scorecard |
| `crm_follow_up_queue.csv` | One row per follow-up task | CRM Follow-Up Queue |
| `export_manifest.csv` | One row per export | Documentation |

## Snowflake Reporting Layer

The project includes a Snowflake reporting layer to show how the final connected reporting exports could live inside a cloud warehouse.

Snowflake is used for:

- Warehouse, database, and schema setup
- Loading the final reporting exports
- Validating row counts and key totals
- Creating analytics views
- Answering business questions with SQL

Snowflake SQL files:

| File | Purpose |
|---|---|
| `sql/00_snowflake_setup.sql` | Creates the warehouse, database, schemas, file format, and stage |
| `sql/01_create_export_tables.sql` | Creates raw tables for the final exports |
| `sql/02_load_export_tables.sql` | Loads staged CSV exports into Snowflake tables |
| `sql/03_validate_export_tables.sql` | Validates row counts, totals, duplicates, and business rules |
| `sql/04_create_analytics_views.sql` | Creates reporting-ready analytics views |
| `sql/05_business_question_queries.sql` | Answers the core business questions with SQL |

Snowflake objects:

| Object Type | Name |
|---|---|
| Warehouse | `TP_REPORTING_WH` |
| Database | `TRASH_PANDAS_CONNECTED_REPORTING` |
| Raw schema | `RAW` |
| Analytics schema | `ANALYTICS` |
| QA schema | `QA` |
| Stage | `RAW.TP_EXPORT_STAGE` |
| File format | `RAW.CSV_EXPORT_FORMAT` |

Raw Snowflake tables:

- `RAW.HOMESTAND_SUMMARY`
- `RAW.PROMOTION_SCORECARD`
- `RAW.CRM_FOLLOW_UP_QUEUE`

Analytics views:

- `ANALYTICS.V_HOMESTAND_SUMMARY`
- `ANALYTICS.V_PROMOTION_SCORECARD`
- `ANALYTICS.V_CRM_FOLLOW_UP_QUEUE`
- `ANALYTICS.V_EXECUTIVE_HOMESTAND_OVERVIEW`
- `ANALYTICS.V_PROMOTION_RECOMMENDATION_SUMMARY`
- `ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY`

Validation targets:

| Check | Expected Value |
|---|---:|
| Homestand rows | 34 |
| Promotion scorecard rows | 233 |
| CRM queue rows | 15,000 |
| Homestand tickets sold | 1,274,234 |
| Homestand scanned attendance | 1,126,560 |
| Homestand total revenue indicator | 28,655,060.87 |
| CRM future revenue opportunity | 12,605,270.19 |

Tableau Public uses the same final CSV exports so the published dashboard remains accessible and portfolio-friendly.

Snowflake proves the warehouse and SQL layer.

Tableau Public proves the communication layer.

## Project Scale

Current modeled project output:

| Area | Count |
|---|---:|
| Home games modeled | 207 |
| Homestands modeled | 34 |
| Promotion rows | 233 |
| Synthetic fans | 45,000 |
| Ticket orders | 343,165 |
| Tickets sold | 1,274,234 |
| Scanned attendance | 1,126,560 |
| Merch transactions | 45,557 |
| Concession transactions | 314,165 |
| Sponsorship activations | 93 |
| Fan engagement rows | 135,112 |
| Follow-up opportunities | 52,416 |
| CRM follow-up queue rows | 15,000 |

## Connected Reporting Logic

The project connects business data at several levels.

### Game-Level Connections

Games connect to:

- Promotions
- Public attendance
- Ticket orders
- Ticket scans
- Group sales
- Merch transactions
- Concession transactions
- Sponsorship activations
- Fan engagement
- Follow-up opportunities

This creates homestand and promotion insight.

### Fan-Level Connections

Fans connect to:

- Ticket orders
- Ticket scans
- Merch transactions
- Concession transactions
- Engagement behavior
- Segments
- Follow-up opportunities
- CRM tasks

This creates fan value and follow-up insight.

### Account-Level Connections

Group accounts connect to:

- Group sales
- Ticket orders
- Renewal signals
- Upsell signals
- CRM tasks

This creates account prioritization insight.

## What Connected Reporting Adds

A siloed ticket report can show what was sold.

A scan report can show who attended.

A merch report can show what was bought.

A concession report can show what fans spent.

A CRM report can show who was contacted.

Connected reporting can show:

- Which games sold tickets but lost value through no-shows
- Which average-attendance games created strong in-park spend
- Which promotions created wallets, not just crowds
- Which fans are valuable beyond seat location
- Which group accounts should receive renewal or upsell action
- Which teams own the next step after a homestand

## Why Merch and Concessions Matter

Ticket-only reporting can miss valuable fans.

A fan may not buy season tickets or premium seats but may still create strong value through:

- Repeat attendance
- Merchandise purchases
- Concession purchases
- Theme-night behavior
- Engagement signals
- Family or group buying patterns

By linking a portion of merch and concession purchases to `fan_id`, the project can identify hidden high-value fans.

This creates better targeting for retention, upgrades, bundles, and follow-up campaigns.

## Scoring Concepts

### Total Revenue Indicator

A synthetic business value measure that combines:

- Ticket revenue
- Merch revenue
- Concession revenue

This is not actual financial reporting.

It is a portfolio metric used to demonstrate how connected reporting could support better decisions.

### Total Value Index

A weighted index that scores games, homestands, or promotions based on connected business signals such as:

- Revenue indicator
- Scanned attendance
- Scan rate
- In-park spend
- Group tickets
- Fan engagement
- Follow-up opportunities

### Repeat Likelihood Score

A rule-based score estimating whether a fan or account is likely to buy or attend again.

Signals include:

- Attendance history
- Purchase history
- Engagement behavior
- Segment type
- Lapsed status
- Prior value

### Upgrade Potential Score

A rule-based score estimating whether a fan or account may be a good fit for a higher-value offer.

Signals include:

- Premium behavior
- Group buying behavior
- Corporate prospect signals
- In-park spending
- Engagement with upgrade-related campaigns

### Priority Score

A rule-based score used to rank follow-up actions.

Signals include:

- Opportunity type
- Prior value
- No-show recovery value
- Repeat likelihood
- Upgrade potential
- Group renewal or upsell signals

## Tech Stack

| Tool | Use |
|---|---|
| Python | Synthetic data generation, data prep, export builds, quality checks |
| CSV / Excel-style files | Source and export file format |
| Snowflake | Warehouse-style reporting layer, SQL validation, analytics views |
| SQL | Data validation, reporting queries, business-question analysis |
| Tableau Public | Dashboard build |
| GitHub | Version control and project documentation |
| VS Code | File editing |

## Repository Structure

```text
data/
  exports/
  processed/
  public/
  synthetic/

python/
  data_generation/
  export_builds/
  quality_checks/

sql/
  00_snowflake_setup.sql
  01_create_export_tables.sql
  02_load_export_tables.sql
  03_validate_export_tables.sql
  04_create_analytics_views.sql
  05_business_question_queries.sql

README.md
DATA_SOURCE_MAP.md
DATA_ASSUMPTIONS.md
SYNTHETIC_DATA_PLAN.md
SNOWFLAKE_SCHEMA_PLAN.md
SNOWFLAKE_LOAD_GUIDE.md
DASHBOARD_PLAN.md
TABLEAU_BUILD_GUIDE.md
BUSINESS_QUESTIONS.md
BUILD_ORDER.md
TASK_TRACKER.md