# Snowflake Schema Plan

## Purpose

This file defines the planned Snowflake structure for the Trash Pandas Connected Reporting Pilot.

The goal is to model how separate business reports can be staged, cleaned, connected, and transformed into decision-ready reporting views.

This project uses Snowflake as the reporting warehouse because the project is focused on connected business intelligence, not just local SQL practice.

---

## Snowflake Design Principle

The Snowflake build will follow a warehouse-style structure:

| Layer | Purpose |
|---|---|
| RAW | Load source CSV files with minimal transformation |
| STAGING | Clean, standardize, type-cast, and prepare source tables |
| ANALYTICS | Build connected reporting views and business logic |
| EXPORTS | Create Tableau-ready tables or views |

This structure keeps the project clean and makes the data flow easy to explain.

---

## Database Name

```sql
TRASH_PANDAS_CONNECTED_REPORTING