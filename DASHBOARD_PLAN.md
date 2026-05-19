---

## `DASHBOARD_PLAN.md`

```markdown
# Dashboard Plan

## Project

Trash Pandas Connected Reporting Pilot

## Dashboard Purpose

This dashboard shows what a sports organization can learn when separate business reports are connected into one reporting layer.

The dashboard does not claim to use internal Trash Pandas data.

It uses:

- Public schedule, promotion, and attendance anchors where available
- Synthetic internal-style ticketing, scans, merch, concessions, engagement, group sales, and CRM follow-up data
- Derived exports built from connected source files
- Snowflake-modeled reporting logic
- Tableau Public dashboard-ready CSV exports

The goal is to show the reporting structure a growth-market sports organization could use if ticketing, scans, promotions, retail, concessions, group sales, fan engagement, and CRM workflows were connected.

---

## Dashboard Thesis

Siloed reports show activity.

Connected reporting shows decisions.

A ticket report can show what was sold.

A scan report can show who showed up.

A promotion report can show what was offered.

A POS report can show what fans bought.

A CRM report can show who needs follow-up.

The value comes from connecting those reports into one decision layer.

---

## Final Tableau Data Sources

Tableau Public should use the files in `data/exports/`.

### Primary Dashboard Exports

| Export | Grain | Dashboard Use |
|---|---|---|
| `homestand_summary.csv` | One row per homestand | Connected Homestand Intelligence |
| `promotion_scorecard.csv` | One row per promotion per game | Promotion Value Scorecard |
| `crm_follow_up_queue.csv` | One row per CRM follow-up task | CRM Follow-Up Queue |

### Documentation / QA Exports

| Export | Purpose |
|---|---|
| `export_manifest.csv` | Documents final dashboard-ready exports |
| `homestand_summary_generation_summary.csv` | Generation summary for homestand export |
| `promotion_scorecard_generation_summary.csv` | Generation summary for promotion scorecard |
| `crm_follow_up_queue_generation_summary.csv` | Generation summary for CRM queue |
| `homestand_summary_quality_summary.csv` | Quality checks for homestand export |
| `promotion_scorecard_quality_summary.csv` | Quality checks for promotion scorecard |
| `crm_follow_up_queue_quality_summary.csv` | Quality checks for CRM queue |

---

## Dashboard Page 1: Connected Homestand Intelligence

### Business Question

Which homestands created value across ticket demand, attendance conversion, in-park spend, and follow-up opportunity?

### Data Source

`homestand_summary.csv`

### Audience

Primary:

- Leadership
- General manager / executive staff
- Business operations

Secondary:

- Sales
- Marketing
- Promotions
- Service / CRM

### Main Decision

Which homestands created the strongest connected business value, and what should the team focus on next?

### Connected Reporting Lesson

A homestand can look strong in a ticket report but weaker once scan rate, no-shows, in-park spend, and follow-up opportunity are connected.

This page is designed to show the difference between demand and total value.

### Core KPI Labels

| KPI Label | Field | Connected Meaning |
|---|---|---|
| Demand Created | `tickets_sold` | What ticketing says was sold |
| Attendance Converted | `scanned_attendance` | What gate scans say turned into attendance |
| Demand-to-Attendance Conversion | `scan_rate` | How much demand became real attendance |
| Lost Attendance Opportunity | `no_show_rate` | Where sold tickets did not become attendance |
| Value After Arrival | `merch_net_sales` + `concession_net_sales` | What fans created after scanning in |
| Quality of Attendance | `revenue_per_scanned_fan` | Revenue value per scanned fan |
| Actionable CRM Signals | `follow_up_opportunity_count` | Future action created from connected behavior |
| Future Value Pipeline | `future_revenue_opportunity` | Modeled future opportunity from follow-up logic |
| Connected Value Score | `homestand_total_value_index` | Weighted value score across connected signals |
| Recommended Focus | `recommended_focus` | Action direction after the homestand |

### Recommended Visuals

#### 1. KPI Header

Show selected season or selected homestand totals.

Cards:

- Demand Created
- Attendance Converted
- Demand-to-Attendance Conversion
- Lost Attendance Opportunity
- Value After Arrival
- Connected Value Score

Purpose:

Start with the silo-to-connected story.

#### 2. Demand vs Attendance Converted

Chart:

- Side-by-side bar chart
- `tickets_sold`
- `scanned_attendance`
- by `homestand_id`

Purpose:

Separate ticket demand from actual attendance.

Business takeaway:

A sold ticket only creates full value when the fan shows up.

#### 3. Lost Attendance Opportunity by Homestand

Chart:

- Bar chart
- `no_show_rate`
- by `homestand_id`

Purpose:

Identify homestands where demand did not convert.

Business takeaway:

No-shows are not only an attendance issue. They can reduce in-park spend and future engagement.

#### 4. Value After Arrival

Chart:

- Stacked or side-by-side bar
- `merch_net_sales`
- `concession_net_sales`
- by `homestand_id`

Purpose:

Show the value created after fans entered the ballpark.

Business takeaway:

Attendance matters, but fan value continues after the scan.

#### 5. Connected Value Ranking Table

Rows:

- `homestand_id`
- `homestand_start_date`
- `homestand_end_date`
- `opponents`

Measures:

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

Purpose:

Show which homestands performed best across connected signals.

#### 6. Recommended Focus Breakdown

Chart:

- Bar chart or highlight table
- `recommended_focus`
- count of `homestand_id`

Purpose:

Turn reporting into executive action.

### Suggested Filters

- `season`
- `homestand_id`
- `recommended_focus`
- `promo_categories`
- `opponents`

### Executive Takeaway

This page shows what leadership can learn only when ticketing, scans, merch, concessions, engagement, and CRM signals are connected.

---

## Dashboard Page 2: Promotion Value Scorecard

### Business Question

Which promotions created value beyond attendance, and should they return, be reworked, retired, or reviewed?

### Data Source

`promotion_scorecard.csv`

### Audience

Primary:

- Leadership
- Marketing
- Promotions

Secondary:

- Sales
- Sponsorship
- Ticketing

### Main Decision

Which promotions deserve future inventory, budget, sponsor support, or redesign?

### Connected Reporting Lesson

A promotion can drive a crowd and still underperform if scan rate, in-park spend, repeat behavior, or follow-up opportunity are weak.

This page is designed to separate crowd-driving promotions from value-driving promotions.

### Core KPI Labels

| KPI Label | Field | Connected Meaning |
|---|---|---|
| Promotions Reviewed | `promo_id` | Scope of promotion analysis |
| Avg Connected Value Score | `total_value_index` | Overall promotion value |
| Demand Created | `tickets_sold` | Ticket demand tied to promotion |
| Attendance Converted | `scanned_attendance` | Actual attendance tied to promotion |
| Demand-to-Attendance Conversion | `scan_rate` | Whether ticket demand became attendance |
| Value After Arrival | `merch_net_sales` + `concession_net_sales` | Spend created inside the ballpark |
| Quality of Attendance | `revenue_per_scanned_fan` | Revenue per scanned fan |
| Repeat Buyer Signal | `repeat_buyer_rate` | Long-term fan behavior |
| Future Value Pipeline | `future_revenue_opportunity` | Future opportunity created |
| Return / Rework / Retire / Review | `recommendation` | Decision output |

### Recommended Visuals

#### 1. Promotion Recommendation Summary

Chart:

- Bar chart
- `recommendation`
- count of `promo_id`

Categories:

- return
- rework
- retire
- review

Purpose:

Give leadership a quick read on promotion inventory quality.

#### 2. Promotion Scorecard Table

Rows:

- `promo_name`
- `promo_category`
- `game_date`
- `opponent`

Measures:

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

Purpose:

Create a working review tool for promotion decisions.

#### 3. Connected Value by Promotion Category

Chart:

- Bar chart
- `promo_category`
- average `total_value_index`

Purpose:

Show which promotion categories create the strongest connected value.

#### 4. Attendance Lift vs Revenue Lift

Chart:

- Scatterplot
- X-axis: `scanned_attendance_lift_vs_slot`
- Y-axis: `revenue_lift_per_scanned_fan`
- Detail: `promo_name`
- Color: `recommendation`

Purpose:

Separate promotions that create attendance from promotions that create stronger revenue per fan.

Business takeaway:

A promo can win on crowd size but lose on revenue quality.

#### 5. In-Park Spend Lift by Promotion

Chart:

- Bar chart
- `merch_lift_per_scanned_fan`
- `concession_lift_per_scanned_fan`
- by `promo_name`

Purpose:

Show which promotions change fan spending behavior inside the ballpark.

#### 6. Repeat Buyer Signal

Chart:

- Bar chart or table
- `repeat_buyer_rate`
- `repeat_buyer_rate_lift_vs_slot`

Purpose:

Show which promotions may create long-term fan value instead of one-night attendance.

### Suggested Filters

- `season`
- `promo_category`
- `promo_type`
- `recommendation`
- `day_of_week`
- `weekend_flag`
- `homestand_id`

### Executive Takeaway

A promotion should not be judged only by attendance. Better decisions come from connecting tickets sold, scan rate, no-shows, group sales, merch, concessions, repeat buyers, and follow-up opportunities.

---

## Dashboard Page 3: CRM Follow-Up Queue

### Business Question

Which fans and accounts become actionable once behavior from multiple systems is connected?

### Data Source

`crm_follow_up_queue.csv`

### Audience

Primary:

- Leadership
- Sales
- Group sales
- Service
- Marketing

Secondary:

- CRM / business intelligence
- Hiring managers / recruiters reviewing portfolio work

### Main Decision

Which fans or accounts should receive follow-up first, and which team owns the next action?

### Connected Reporting Lesson

Ticket data alone cannot tell a team who is worth contacting.

When ticketing, scans, merch, concessions, engagement, and group sales are connected, the team can prioritize action instead of guessing.

### Core KPI Labels

| KPI Label | Field | Connected Meaning |
|---|---|---|
| Actionable CRM Signals | `follow_up_id` | Total prioritized follow-up tasks |
| High Priority Signals | `priority_band = High` | Most urgent follow-up work |
| Future Value Pipeline | `future_revenue_opportunity` | Modeled future value from follow-up |
| Avg Priority Score | `priority_score` | Quality of the task queue |
| Fan Opportunities | `entity_type = fan` | Individual fan action |
| Account Opportunities | `entity_type = account` | Group or organizational action |
| Recover / Upgrade / Retain / Renew | `executive_action_bucket` | Action type |
| Team Ownership | `assigned_team` | Which team owns follow-up |

### Recommended Visuals

#### 1. Queue KPI Header

Cards:

- Actionable CRM Signals
- High Priority Signals
- Future Value Pipeline
- Avg Priority Score
- Fan Opportunities
- Account Opportunities

Purpose:

Show the size and value of the follow-up workload.

#### 2. Action Bucket Breakdown

Chart:

- Bar chart
- `executive_action_bucket`
- count of `follow_up_id`

Buckets:

- Recover
- Upgrade
- Retain
- Renew

Purpose:

Show what type of work the team needs to do.

#### 3. Team Ownership Workload

Chart:

- Bar chart
- `assigned_team`
- count of `follow_up_id`

Purpose:

Show whether the action list belongs to sales, marketing, service, or group sales.

#### 4. Priority Queue Table

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

Make the dashboard usable as a working action list.

#### 5. Hidden Fan Value View

Chart:

- Table or scatterplot
- `entity_total_value`
- `entity_ticket_revenue`
- `entity_in_park_revenue`
- `fan_hidden_value_flag`

Purpose:

Show fans who may be more valuable than ticket-only reporting suggests.

Business takeaway:

A fan can look average in ticketing data but become valuable when merch, concessions, attendance behavior, and engagement are connected.

#### 6. Opportunity Type Breakdown

Chart:

- Bar chart
- `opportunity_type`
- count of `follow_up_id`

Purpose:

Show which behavior signals are creating action.

### Suggested Filters

- `assigned_team`
- `executive_action_bucket`
- `priority_band`
- `opportunity_type`
- `entity_type`
- `season`
- `homestand_id`
- `promo_categories`
- `market_distance_band`

### Executive Takeaway

The connected reporting layer turns scattered behavior into an action list. It tells the team who to contact, why they matter, who owns the follow-up, and what action should happen next.

---

## Dashboard Build Order

### Step 1: Connect Data Sources

Connect Tableau Public to:

1. `homestand_summary.csv`
2. `promotion_scorecard.csv`
3. `crm_follow_up_queue.csv`

Use them as separate data sources.

Do not force relationships unless needed.

### Step 2: Build Connected Homestand Intelligence

Build the executive summary first.

Priority sheets:

1. KPI Header
2. Demand vs Attendance Converted
3. Lost Attendance Opportunity by Homestand
4. Value After Arrival
5. Connected Value Ranking Table
6. Recommended Focus Breakdown

### Step 3: Build Promotion Value Scorecard

Build the promotion decision layer second.

Priority sheets:

1. Promotion Recommendation Summary
2. Promotion Scorecard Table
3. Connected Value by Promotion Category
4. Attendance Lift vs Revenue Lift
5. In-Park Spend Lift by Promotion
6. Repeat Buyer Signal

### Step 4: Build CRM Follow-Up Queue

Build the action layer third.

Priority sheets:

1. Queue KPI Header
2. Action Bucket Breakdown
3. Team Ownership Workload
4. Priority Queue Table
5. Hidden Fan Value View
6. Opportunity Type Breakdown

### Step 5: Add Navigation

Dashboard tabs:

1. Connected Homestand Intelligence
2. Promotion Value Scorecard
3. CRM Follow-Up Queue

### Step 6: Add Source Notes

Each dashboard should include a small note:

> Public data is used where available. Internal-style ticketing, scan, merch, concessions, engagement, group sales, and CRM fields are synthetic and used only to demonstrate connected reporting structure.

---

## Dashboard Design Rules

Keep the dashboard clean and executive-facing.

Use:

- Clear titles
- Plain language
- Minimal chart clutter
- Business-first labels
- Action-oriented dashboard sections
- Source notes where synthetic fields appear
- KPI names that explain connected value
- Tooltips that explain what the connected data reveals

Avoid:

- Overcomplicated visuals
- Too many filters
- Fake precision
- Claims that this is real internal Trash Pandas data
- Overstating sponsorship ROI
- Making the CRM queue look like a real operational system
- Framing the project as only a dashboard

---

## Final Dashboard Story

The dashboard should show this progression:

1. Connected Homestand Intelligence: What happened across demand, attendance, spend, and follow-up opportunity?
2. Promotion Value Scorecard: What worked beyond attendance?
3. CRM Follow-Up Queue: What should the team do next?

The team may already have the data.

The value is connecting it.