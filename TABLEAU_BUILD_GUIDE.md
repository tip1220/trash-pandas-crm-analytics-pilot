# Tableau Build Guide

## Project

Trash Pandas Connected Reporting Pilot

## Purpose

This guide explains how to build the Tableau Public dashboard using the final export files in `data/exports/`.

The dashboard should prove one idea:

Separate business reports become more valuable when they are connected into one reporting layer.

---

## Final Tableau Data Sources

Use these three CSV files as separate Tableau data sources:

| Data Source | File | Grain |
|---|---|---|
| Homestand Summary | `data/exports/homestand_summary.csv` | One row per homestand |
| Promotion Scorecard | `data/exports/promotion_scorecard.csv` | One row per promotion per game |
| CRM Follow-Up Queue | `data/exports/crm_follow_up_queue.csv` | One row per follow-up task |

Do not force joins or relationships inside Tableau unless needed.

Each export already contains the fields needed for its dashboard page.

---

## Dashboard Pages

Build three dashboard pages:

1. Homestand Intelligence
2. Promotion Scorecard
3. CRM Follow-Up Queue

The story should move from leadership summary to promotion decisions to action queue.

---

# Page 1: Homestand Intelligence

## Business Question

After a homestand, what happened, why did it happen, and what should leadership do next?

## Data Source

`homestand_summary.csv`

## Dashboard Role

Executive summary.

This page helps leadership compare homestands and understand which ones created the most connected business value.

## Required Sheets

### Sheet 1: KPI - Tickets Sold

Field:

- `tickets_sold`

Use:

- SUM

Title:

`Tickets Sold`

---

### Sheet 2: KPI - Scanned Attendance

Field:

- `scanned_attendance`

Use:

- SUM

Title:

`Scanned Attendance`

---

### Sheet 3: KPI - Scan Rate

Create calculated field:

`Scan Rate Display`

Formula:

`SUM([scanned_attendance]) / SUM([tickets_sold])`

Format:

- Percentage
- 1 decimal place

Title:

`Scan Rate`

---

### Sheet 4: KPI - No-Show Rate

Create calculated field:

`No-Show Rate Display`

Formula:

`SUM([no_show_ticket_quantity]) / SUM([tickets_sold])`

Format:

- Percentage
- 1 decimal place

Title:

`No-Show Rate`

---

### Sheet 5: KPI - Total Revenue Indicator

Field:

- `total_revenue_indicator`

Use:

- SUM

Format:

- Currency
- No decimals

Title:

`Total Revenue Indicator`

---

### Sheet 6: KPI - Homestand Value Index

Field:

- `homestand_total_value_index`

Use:

- AVG

Format:

- Number
- 1 decimal place

Title:

`Avg. Homestand Value Index`

---

### Sheet 7: Homestand Ranking Table

Rows:

- `homestand_id`
- `homestand_start_date`
- `homestand_end_date`
- `opponents`

Text / Measures:

- `game_count`
- `tickets_sold`
- `scanned_attendance`
- `scan_rate`
- `no_show_rate`
- `total_revenue_indicator`
- `homestand_total_value_index`
- `recommended_focus`

Purpose:

Show which homestands performed best and what action leadership should consider.

---

### Sheet 8: Tickets Sold vs Scanned Attendance

Columns:

- `homestand_id`

Rows:

- `tickets_sold`
- `scanned_attendance`

Chart:

- Side-by-side bars

Purpose:

Show the gap between demand and actual attendance.

---

### Sheet 9: No-Show Rate by Homestand

Columns:

- `homestand_id`

Rows:

- `no_show_rate`

Chart:

- Bar chart

Sort:

- Descending by `no_show_rate`

Purpose:

Identify homestands where sold tickets did not convert into attendance.

---

### Sheet 10: Revenue Mix by Homestand

Columns:

- `homestand_id`

Rows:

- `net_ticket_revenue`
- `merch_net_sales`
- `concession_net_sales`

Chart:

- Stacked bar or side-by-side bar

Purpose:

Show how the total value story changes when tickets, merch, and concessions are viewed together.

---

### Sheet 11: Recommended Focus Breakdown

Rows:

- `recommended_focus`

Columns:

- COUNTD `homestand_id`

Chart:

- Bar chart

Purpose:

Show how many homestands point to each action area.

---

## Page 1 Filters

Add filters:

- `season`
- `homestand_id`
- `recommended_focus`

Show filters on the dashboard.

---

## Page 1 Layout

Recommended layout:

1. Title
2. Short source note
3. KPI row
4. Tickets sold vs scanned attendance
5. Revenue mix
6. Homestand ranking table
7. Recommended focus breakdown

---

# Page 2: Promotion Scorecard

## Business Question

Which promotions created the most total value, and should they return, be reworked, retired, or reviewed?

## Data Source

`promotion_scorecard.csv`

## Dashboard Role

Promotion decision layer.

This page helps leadership and marketing evaluate promotions beyond attendance.

## Required Sheets

### Sheet 1: KPI - Promotion Count

Field:

- `promo_id`

Use:

- COUNTD

Title:

`Promotions Reviewed`

---

### Sheet 2: KPI - Avg. Total Value Index

Field:

- `total_value_index`

Use:

- AVG

Title:

`Avg. Total Value Index`

---

### Sheet 3: KPI - Return / Rework Count

Create calculated field:

`Return or Rework Flag`

Formula:

`IF [recommendation] = "return" OR [recommendation] = "rework" THEN 1 ELSE 0 END`

Use:

- SUM

Title:

`Return / Rework Candidates`

---

### Sheet 4: Recommendation Breakdown

Rows:

- `recommendation`

Columns:

- COUNTD `promo_id`

Chart:

- Bar chart

Purpose:

Show the promotion inventory decision mix.

---

### Sheet 5: Promotion Scorecard Table

Rows:

- `promo_name`
- `promo_category`
- `game_date`
- `opponent`

Text / Measures:

- `tickets_sold`
- `scanned_attendance`
- `scan_rate`
- `no_show_rate`
- `group_tickets`
- `merch_net_sales`
- `concession_net_sales`
- `repeat_buyer_rate`
- `total_value_index`
- `recommendation`
- `recommendation_reason`

Purpose:

Create a working review table for promotion decisions.

---

### Sheet 6: Total Value Index by Promo Category

Rows:

- `promo_category`

Columns:

- AVG `total_value_index`

Chart:

- Bar chart

Sort:

- Descending by AVG `total_value_index`

Purpose:

Show which promotion categories create the strongest connected value.

---

### Sheet 7: Attendance Lift vs Revenue Lift

Columns:

- `scanned_attendance_lift_vs_slot`

Rows:

- `revenue_lift_per_scanned_fan`

Detail:

- `promo_name`

Color:

- `recommendation`

Chart:

- Scatterplot

Purpose:

Separate crowd-driving promotions from revenue-driving promotions.

---

### Sheet 8: In-Park Spend Lift by Promotion

Rows:

- `promo_name`

Columns:

- `merch_lift_per_scanned_fan`
- `concession_lift_per_scanned_fan`

Chart:

- Bar chart

Sort:

- Descending by `merch_lift_per_scanned_fan` or total in-park lift

Purpose:

Show which promotions changed in-park spending.

---

### Sheet 9: Repeat Buyer Signal

Rows:

- `promo_name`

Columns:

- `repeat_buyer_rate`
- `repeat_buyer_rate_lift_vs_slot`

Chart:

- Bar chart or table

Purpose:

Show which promotions may create longer-term fan behavior.

---

## Page 2 Filters

Add filters:

- `season`
- `promo_category`
- `recommendation`
- `day_of_week`
- `weekend_flag`

---

## Page 2 Layout

Recommended layout:

1. Title
2. Short source note
3. KPI row
4. Recommendation breakdown
5. Total value by category
6. Attendance lift vs revenue lift scatterplot
7. Promotion scorecard table

---

# Page 3: CRM Follow-Up Queue

## Business Question

Who should be contacted, why do they matter, and which team owns the next action?

## Data Source

`crm_follow_up_queue.csv`

## Dashboard Role

Action layer.

This page shows that connected reporting can turn behavior into a prioritized queue.

## Required Sheets

### Sheet 1: KPI - Open Follow-Up Tasks

Field:

- `follow_up_id`

Use:

- COUNTD

Title:

`Open Follow-Up Tasks`

---

### Sheet 2: KPI - High Priority Tasks

Create calculated field:

`High Priority Task Flag`

Formula:

`IF [priority_band] = "High" THEN 1 ELSE 0 END`

Use:

- SUM

Title:

`High Priority Tasks`

---

### Sheet 3: KPI - Future Revenue Opportunity

Field:

- `future_revenue_opportunity`

Use:

- SUM

Format:

- Currency
- No decimals

Title:

`Future Revenue Opportunity`

---

### Sheet 4: KPI - Avg. Priority Score

Field:

- `priority_score`

Use:

- AVG

Title:

`Avg. Priority Score`

---

### Sheet 5: Action Bucket Breakdown

Rows:

- `executive_action_bucket`

Columns:

- COUNTD `follow_up_id`

Chart:

- Bar chart

Purpose:

Show whether the queue is focused on recovery, upgrades, retention, or renewals.

---

### Sheet 6: Assigned Team Workload

Rows:

- `assigned_team`

Columns:

- COUNTD `follow_up_id`

Chart:

- Bar chart

Purpose:

Show which team owns the follow-up work.

---

### Sheet 7: Priority Queue Table

Rows:

- `priority_rank`
- `entity_type`
- `entity_id`
- `assigned_team`
- `priority_band`
- `opportunity_type`
- `suggested_action`
- `future_revenue_opportunity`
- `repeat_likelihood_score`
- `upgrade_potential_score`
- `due_date`

Purpose:

Create a working action list.

---

### Sheet 8: Hidden Fan Value View

Rows:

- `entity_id`
- `fan_segments`

Columns / Measures:

- `entity_total_value`
- `entity_ticket_revenue`
- `entity_in_park_revenue`

Filter:

- `entity_type = fan`

Optional filter:

- `fan_hidden_value_flag = True`

Purpose:

Show fans who become more valuable once merch and concessions are connected.

---

### Sheet 9: Opportunity Type Breakdown

Rows:

- `opportunity_type`

Columns:

- COUNTD `follow_up_id`

Chart:

- Bar chart

Purpose:

Show which behavior signals are creating the queue.

---

## Page 3 Filters

Add filters:

- `assigned_team`
- `executive_action_bucket`
- `priority_band`
- `opportunity_type`
- `entity_type`
- `season`
- `homestand_id`

---

## Page 3 Layout

Recommended layout:

1. Title
2. Short source note
3. KPI row
4. Action bucket breakdown
5. Assigned team workload
6. Priority queue table
7. Hidden fan value view

---

# Required Source Note

Use this note on each dashboard page:

Public data is used where available. Internal-style ticketing, scan, merch, concessions, engagement, group sales, and CRM fields are synthetic and used only to demonstrate connected reporting structure.

---

# Dashboard Publishing Notes

When publishing to Tableau Public:

- Use a clear title
- Include “Connected Reporting Pilot” in the workbook name
- Do not imply access to internal Trash Pandas data
- Include the synthetic data note
- Keep dashboard pages clean and business-facing

Suggested Tableau Public workbook title:

`Trash Pandas Connected Reporting Pilot`

---

# Final Dashboard Story

The finished dashboard should tell this story:

1. Homestand Intelligence shows what happened.
2. Promotion Scorecard shows what worked.
3. CRM Follow-Up Queue shows what to do next.

The project does not argue that the team lacks data.

It shows the value of connecting the data they may already have.