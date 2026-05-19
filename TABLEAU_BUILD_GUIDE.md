# Tableau Build Guide

## Project

Trash Pandas Connected Reporting Pilot

## Purpose

This guide explains how to build the Tableau Public dashboard using the final export files in `data/exports/`.

The dashboard should prove one idea:

Separate business reports become more valuable when they are connected into one reporting layer.

The dashboard should not feel like a generic sports dashboard.

It should feel like a connected reporting pilot that shows what a team can learn when ticketing, scans, promotions, merch, concessions, group sales, engagement, and CRM follow-up data are analyzed together.

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

## Workbook Title

Use:

`Trash Pandas Connected Reporting Pilot: From Siloed Reports to Actionable Insights`

Shorter dashboard title option:

`From Siloed Reports to Actionable Insights`

---

## Required Source Note

Use this note on each dashboard page:

Public data is used where available. Internal-style ticketing, scan, merch, concessions, engagement, group sales, and CRM fields are synthetic and used only to demonstrate connected reporting structure.

---

## Dashboard Pages

Build three dashboard pages:

1. Connected Homestand Intelligence
2. Promotion Value Scorecard
3. CRM Follow-Up Queue

The story should move from leadership summary to promotion decisions to action queue.

---

# Page 1: Connected Homestand Intelligence

## Business Question

Which homestands created value across ticket demand, attendance conversion, in-park spend, and follow-up opportunity?

## Data Source

`homestand_summary.csv`

## Dashboard Role

Executive summary.

This page helps leadership compare homestands and understand which ones created the most connected business value.

## Page-Level Story

Ticket sales tell one part of the story.

Connected reporting shows whether that demand converted into attendance, created in-park value, and produced follow-up opportunity.

## Required Sheets

### Sheet 1: KPI - Demand Created

Field:

- `tickets_sold`

Use:

- SUM

Title:

`Demand Created`

Subtitle / tooltip language:

Tickets sold from the connected reporting export. This is the demand signal, not the full value story.

---

### Sheet 2: KPI - Attendance Converted

Field:

- `scanned_attendance`

Use:

- SUM

Title:

`Attendance Converted`

Subtitle / tooltip language:

Scanned attendance shows how much ticket demand became real ballpark attendance.

---

### Sheet 3: KPI - Demand-to-Attendance Conversion

Create calculated field:

`Demand-to-Attendance Conversion`

Formula:

`SUM([scanned_attendance]) / SUM([tickets_sold])`

Format:

- Percentage
- 1 decimal place

Title:

`Demand-to-Attendance Conversion`

Subtitle / tooltip language:

This connects ticketing and scan data to show whether sold tickets became attendance.

---

### Sheet 4: KPI - Lost Attendance Opportunity

Create calculated field:

`Lost Attendance Opportunity`

Formula:

`SUM([no_show_ticket_quantity]) / SUM([tickets_sold])`

Format:

- Percentage
- 1 decimal place

Title:

`Lost Attendance Opportunity`

Subtitle / tooltip language:

No-show rate shows where ticket demand did not become scanned attendance.

---

### Sheet 5: KPI - Value After Arrival

Create calculated field:

`Value After Arrival`

Formula:

`SUM([merch_net_sales]) + SUM([concession_net_sales])`

Format:

- Currency
- No decimals

Title:

`Value After Arrival`

Subtitle / tooltip language:

Merch and concession sales show the value created after fans entered the ballpark.

---

### Sheet 6: KPI - Connected Value Score

Field:

- `homestand_total_value_index`

Use:

- AVG

Format:

- Number
- 1 decimal place

Title:

`Connected Value Score`

Subtitle / tooltip language:

Weighted score across demand, attendance conversion, spend, engagement, and follow-up opportunity.

---

### Sheet 7: Demand vs Attendance Converted

Columns:

- `homestand_id`

Rows:

- `tickets_sold`
- `scanned_attendance`

Chart:

- Side-by-side bars

Title:

`Demand vs Attendance Converted`

Purpose:

Show the gap between ticket demand and actual attendance.

---

### Sheet 8: Lost Attendance Opportunity by Homestand

Columns:

- `homestand_id`

Rows:

- `no_show_rate`

Chart:

- Bar chart

Sort:

- Descending by `no_show_rate`

Title:

`Lost Attendance Opportunity by Homestand`

Purpose:

Identify homestands where sold tickets did not convert into attendance.

---

### Sheet 9: Value After Arrival by Homestand

Columns:

- `homestand_id`

Rows:

- `merch_net_sales`
- `concession_net_sales`

Chart:

- Stacked bar or side-by-side bar

Title:

`Value After Arrival by Homestand`

Purpose:

Show how the value story changes when merch and concessions are connected to attendance.

---

### Sheet 10: Connected Value Ranking Table

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
- `revenue_per_scanned_fan`
- `in_park_spend_per_scanned_fan`
- `future_revenue_opportunity`
- `homestand_total_value_index`
- `recommended_focus`

Title:

`Connected Value Ranking`

Purpose:

Show which homestands performed best across connected signals.

---

### Sheet 11: Recommended Focus Breakdown

Rows:

- `recommended_focus`

Columns:

- COUNTD `homestand_id`

Chart:

- Bar chart

Title:

`Recommended Focus Breakdown`

Purpose:

Show how connected reporting turns performance into action.

---

## Page 1 Filters

Add filters:

- `season`
- `homestand_id`
- `recommended_focus`

Show filters on the dashboard.

## Page 1 Layout

Recommended layout:

1. Title
2. One-sentence connected reporting takeaway
3. Source note
4. KPI row
5. Demand vs Attendance Converted
6. Value After Arrival
7. Connected Value Ranking Table
8. Recommended Focus Breakdown

## Page 1 Takeaway Text

Use this on the dashboard:

`Ticket demand is only the starting point. Connected reporting shows whether fans showed up, spent inside the ballpark, and created future follow-up opportunity.`

---

# Page 2: Promotion Value Scorecard

## Business Question

Which promotions created value beyond attendance, and should they return, be reworked, retired, or reviewed?

## Data Source

`promotion_scorecard.csv`

## Dashboard Role

Promotion decision layer.

This page helps leadership and marketing evaluate promotions beyond crowd size.

## Page-Level Story

A promotion can drive attendance and still underperform on revenue quality, repeat behavior, or follow-up opportunity.

Connected reporting shows which promotions created broader value.

## Required Sheets

### Sheet 1: KPI - Promotions Reviewed

Field:

- `promo_id`

Use:

- COUNTD

Title:

`Promotions Reviewed`

---

### Sheet 2: KPI - Avg Connected Value Score

Field:

- `total_value_index`

Use:

- AVG

Format:

- Number
- 1 decimal place

Title:

`Avg Connected Value Score`

---

### Sheet 3: KPI - Value After Arrival

Create calculated field:

`Promotion Value After Arrival`

Formula:

`SUM([merch_net_sales]) + SUM([concession_net_sales])`

Format:

- Currency
- No decimals

Title:

`Value After Arrival`

---

### Sheet 4: KPI - Future Value Pipeline

Field:

- `future_revenue_opportunity`

Use:

- SUM

Format:

- Currency
- No decimals

Title:

`Future Value Pipeline`

---

### Sheet 5: KPI - Return / Rework Candidates

Create calculated field:

`Return or Rework Flag`

Formula:

`IF [recommendation] = "return" OR [recommendation] = "rework" THEN 1 ELSE 0 END`

Use:

- SUM

Title:

`Return / Rework Candidates`

---

### Sheet 6: Recommendation Breakdown

Rows:

- `recommendation`

Columns:

- COUNTD `promo_id`

Chart:

- Bar chart

Title:

`Promotion Decision Mix`

Purpose:

Show the promotion inventory decision mix.

---

### Sheet 7: Promotion Scorecard Table

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
- `revenue_per_scanned_fan`
- `repeat_buyer_rate`
- `total_value_index`
- `recommendation`
- `recommendation_reason`

Title:

`Promotion Value Scorecard`

Purpose:

Create a working review table for promotion decisions.

---

### Sheet 8: Connected Value by Promotion Category

Rows:

- `promo_category`

Columns:

- AVG `total_value_index`

Chart:

- Bar chart

Sort:

- Descending by AVG `total_value_index`

Title:

`Connected Value by Promotion Category`

Purpose:

Show which promotion categories create the strongest connected value.

---

### Sheet 9: Attendance Lift vs Revenue Lift

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

Title:

`Attendance Lift vs Revenue Lift`

Purpose:

Separate crowd-driving promotions from revenue-driving promotions.

Dashboard note:

`Upper-right promotions lifted attendance and revenue quality. Lower-right promotions lifted attendance but underperformed on revenue per fan.`

---

### Sheet 10: In-Park Spend Lift by Promotion

Rows:

- `promo_name`

Columns:

- `merch_lift_per_scanned_fan`
- `concession_lift_per_scanned_fan`

Chart:

- Bar chart

Sort:

- Descending by in-park lift

Title:

`In-Park Spend Lift by Promotion`

Purpose:

Show which promotions changed fan spending behavior inside the ballpark.

---

### Sheet 11: Repeat Buyer Signal

Rows:

- `promo_name`

Columns:

- `repeat_buyer_rate`
- `repeat_buyer_rate_lift_vs_slot`

Chart:

- Bar chart or table

Title:

`Repeat Buyer Signal`

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

## Page 2 Layout

Recommended layout:

1. Title
2. One-sentence connected reporting takeaway
3. Source note
4. KPI row
5. Promotion Decision Mix
6. Connected Value by Promotion Category
7. Attendance Lift vs Revenue Lift
8. Promotion Value Scorecard table

## Page 2 Takeaway Text

Use this on the dashboard:

`Attendance alone does not prove a promotion worked. Connected reporting shows whether a promotion also created spend, repeat behavior, group demand, or follow-up opportunity.`

---

# Page 3: CRM Follow-Up Queue

## Business Question

Which fans and accounts become actionable once behavior from multiple systems is connected?

## Data Source

`crm_follow_up_queue.csv`

## Dashboard Role

Action layer.

This page shows that connected reporting can turn behavior into a prioritized queue.

## Page-Level Story

Ticketing alone cannot tell a team who should be contacted first.

Connected reporting combines purchase behavior, scans, spend, engagement, group activity, and opportunity logic to prioritize action.

## Required Sheets

### Sheet 1: KPI - Actionable CRM Signals

Field:

- `follow_up_id`

Use:

- COUNTD

Title:

`Actionable CRM Signals`

---

### Sheet 2: KPI - High Priority Signals

Create calculated field:

`High Priority Task Flag`

Formula:

`IF [priority_band] = "High" THEN 1 ELSE 0 END`

Use:

- SUM

Title:

`High Priority Signals`

---

### Sheet 3: KPI - Future Value Pipeline

Field:

- `future_revenue_opportunity`

Use:

- SUM

Format:

- Currency
- No decimals

Title:

`Future Value Pipeline`

---

### Sheet 4: KPI - Avg Priority Score

Field:

- `priority_score`

Use:

- AVG

Format:

- Number
- 1 decimal place

Title:

`Avg Priority Score`

---

### Sheet 5: KPI - Fan Opportunities

Create calculated field:

`Fan Opportunity Flag`

Formula:

`IF [entity_type] = "fan" THEN 1 ELSE 0 END`

Use:

- SUM

Title:

`Fan Opportunities`

---

### Sheet 6: KPI - Account Opportunities

Create calculated field:

`Account Opportunity Flag`

Formula:

`IF [entity_type] = "account" THEN 1 ELSE 0 END`

Use:

- SUM

Title:

`Account Opportunities`

---

### Sheet 7: Action Bucket Breakdown

Rows:

- `executive_action_bucket`

Columns:

- COUNTD `follow_up_id`

Chart:

- Bar chart

Title:

`Action Bucket Breakdown`

Purpose:

Show whether the queue is focused on recovery, upgrades, retention, or renewals.

---

### Sheet 8: Team Ownership Workload

Rows:

- `assigned_team`

Columns:

- COUNTD `follow_up_id`

Chart:

- Bar chart

Title:

`Team Ownership Workload`

Purpose:

Show which team owns the follow-up work.

---

### Sheet 9: Priority Queue Table

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

Title:

`Prioritized Follow-Up Queue`

Purpose:

Create a working action list.

---

### Sheet 10: Hidden Fan Value View

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

Title:

`Hidden Fan Value`

Purpose:

Show fans who become more valuable once merch and concessions are connected.

---

### Sheet 11: Opportunity Type Breakdown

Rows:

- `opportunity_type`

Columns:

- COUNTD `follow_up_id`

Chart:

- Bar chart

Title:

`Opportunity Type Breakdown`

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

## Page 3 Layout

Recommended layout:

1. Title
2. One-sentence connected reporting takeaway
3. Source note
4. KPI row
5. Action Bucket Breakdown
6. Team Ownership Workload
7. Prioritized Follow-Up Queue
8. Hidden Fan Value

## Page 3 Takeaway Text

Use this on the dashboard:

`Connected reporting turns scattered fan and account behavior into a ranked action list. It shows who to contact, why they matter, and which team owns the next step.`

---

# Dashboard Publishing Notes

When publishing to Tableau Public:

- Use a clear title
- Include “Connected Reporting Pilot” in the workbook name
- Do not imply access to internal Trash Pandas data
- Include the synthetic data note
- Keep dashboard pages clean and business-facing
- Make the connected-data story visible in the page titles, KPI labels, and short takeaway text

Suggested Tableau Public workbook title:

`Trash Pandas Connected Reporting Pilot: From Siloed Reports to Actionable Insights`

---

# Final Dashboard Story

The finished dashboard should tell this story:

1. Connected Homestand Intelligence shows what happened across demand, attendance, spend, and opportunity.
2. Promotion Value Scorecard shows what worked beyond attendance.
3. CRM Follow-Up Queue shows what to do next.

The project does not argue that the team lacks data.

It shows the value of connecting the data they may already have.