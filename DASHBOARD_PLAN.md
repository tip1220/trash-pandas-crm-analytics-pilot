# Dashboard Plan

## Purpose

This file defines the Tableau Public dashboard plan for the Trash Pandas Connected Reporting Pilot.

The dashboard is designed to show how connected reporting can help a sports organization move beyond attendance-only analysis and make better decisions about game value, promotions, fan follow-up, and group sales.

The dashboard is built for three audiences:

1. Leadership and executives
2. Sales and marketing teams
3. Recruiters and hiring managers reviewing the portfolio project

---

## Dashboard Strategy

The dashboard should not try to show everything.

The dashboard should answer a focused set of business questions:

1. Which games and promotions created the most total fan value beyond attendance?
2. Which promotions should return, be reworked, retired, or reviewed?
3. Which fans or accounts should sales and marketing follow up with first?
4. Which fans are undervalued if the team only looks at ticket spend?
5. Which data sources need to connect to answer these questions consistently?

The dashboard should feel like a decision tool, not a chart collection.

---

## Dashboard Pages

The dashboard will include three pages:

| Page | Dashboard Name | Primary Audience | Primary Decision |
|---|---|---|---|
| 1 | Homestand Intelligence | Leadership | What happened, why, and what should we do next? |
| 2 | Promotion Performance Scorecard | Leadership, marketing, promotions | Should this promotion return, be reworked, retired, or reviewed? |
| 3 | CRM Follow-Up Queue | Sales, marketing | Who should we contact first, and why? |

---

## Page 1: Homestand Intelligence

### Primary Business Question

After each homestand, what happened, why did it happen, and what should leadership, sales, marketing, and promotions do next?

### Purpose

This page gives leadership a connected view of homestand performance.

It should summarize the business story across:

- tickets
- scanned attendance
- no-shows
- promotions
- group sales
- merch
- concessions
- fan engagement
- follow-up opportunities

### Recommended Filters

| Filter | Purpose |
|---|---|
| Season | Compare 2023, 2024, and 2025 |
| Homestand ID | Select one homestand |
| Promo Category | Filter by promotion type |
| Day of Week | Compare schedule slots |
| Opponent | Add game context |

### KPI Cards

| KPI | Definition |
|---|---|
| Tickets Sold | Synthetic tickets sold for selected homestand |
| Scanned Attendance | Synthetic scanned attendance |
| Scan Rate | Scanned attendance divided by tickets sold |
| No-Show Rate | No-shows divided by tickets sold |
| Total Revenue Indicator | Synthetic ticket, group, merch, and concession value |
| In-Park Spend Per Scanned Fan | Merch plus concessions divided by scanned attendance |
| Total Value Index | Weighted 0-100 value score |
| Follow-Up Opportunity Count | Qualified fan/account opportunities created |

### Core Visuals

| Visual | Purpose |
|---|---|
| Game-by-game bar chart | Compare tickets sold vs scanned attendance |
| No-show rate by game | Identify show-up problems |
| Total value index by game | Show which games created the most connected value |
| Revenue mix by game | Compare ticket, group, merch, and concession contribution |
| In-park spend per scanned fan | Identify games with strong spend behavior |
| Promo summary table | Show promo category, scan rate, spend lift, and recommendation |
| Department action panel | Translate insights into next steps |

### Recommended Layout

Top row:

- Homestand selector
- Tickets Sold
- Scanned Attendance
- Scan Rate
- No-Show Rate
- Total Value Index

Middle row:

- Tickets sold vs scanned attendance by game
- Revenue mix by game
- In-park spend per scanned fan

Bottom row:

- Promotion performance summary
- Follow-up opportunity summary
- Department action notes

### Department Action Panel

The dashboard should include a simple action panel.

| Department | What They Need to Know | Example Action |
|---|---|---|
| Leadership | Did the homestand create total value? | Review top and bottom games by Total Value Index |
| Sales | Which fans/accounts should be contacted? | Work high-priority CRM queue |
| Marketing | Which fan segments responded? | Build next campaign around strongest segment |
| Promotions | Which themes created value? | Return, rework, retire, or review promo |
| Group Sales | Which accounts showed renewal potential? | Assign renewal calls |

### Key Insight Examples

The dashboard should make insights like these possible:

- A game had strong announced attendance but weak scan rate.
- A promotion drove attendance but did not drive in-park spend.
- A theme night created strong merch behavior and repeat buyer signals.
- A lower-attendance game created strong value per scanned fan.
- A homestand created a large number of qualified follow-up opportunities.

---

## Page 2: Promotion Performance Scorecard

### Primary Business Question

Which promotions should return, be reworked, retired, or reviewed?

### Purpose

This page evaluates promotion value beyond attendance.

Promotion performance should be based on total value, not just crowd size.

### Recommended Filters

| Filter | Purpose |
|---|---|
| Season | Compare promotion performance by year |
| Promo Category | Focus on fireworks, giveaway, theme night, family, etc. |
| Day of Week | Control for schedule context |
| Homestand ID | Review promotions within a homestand |
| Recommendation | Filter Return, Rework, Retire, Review |

### KPI Cards

| KPI | Definition |
|---|---|
| Promo Games | Count of games with selected promo type |
| Avg Scanned Attendance | Average scanned attendance for selected promo |
| Avg Scan Rate | Average scan rate for selected promo |
| Avg No-Show Rate | Average no-show rate for selected promo |
| Avg In-Park Spend Per Fan | Merch plus concessions per scanned fan |
| Avg Total Value Index | Average promotion value score |
| Return Count | Number of promotions recommended to return |
| Review/Rework/Retire Count | Number of promotions needing action |

### Core Visuals

| Visual | Purpose |
|---|---|
| Ranked bar chart: Total Value Index by promo | Identify strongest promo types |
| Scatter: Attendance lift vs in-park spend lift | Separate crowds from wallets |
| Table: Promotion scorecard | Show full scorecard and recommendation |
| Bar: Merch lift by promo category | Identify merch-driving promos |
| Bar: Concession lift by promo category | Identify concession-driving promos |
| Repeat buyer signal by promo | Identify relationship-building promotions |
| Follow-up opportunities by promo | Show which promos created sales/marketing action |

### Promotion Scorecard Table Fields

| Field | Purpose |
|---|---|
| Promo Category | Promotion type |
| Games Used | Number of games with promo |
| Tickets Sold | Ticket demand |
| Scanned Attendance | Actual attendance signal |
| Scan Rate | Attendance conversion |
| No-Show Rate | Attendance leakage |
| Group Tickets | Group sales impact |
| Merch Lift | Merchandise impact |
| Concession Lift | Concession impact |
| In-Park Spend Per Fan | Spend efficiency |
| Repeat Buyer Signal | Future behavior |
| Follow-Up Opportunity Count | Actionable opportunity |
| Total Value Index | Overall performance |
| Recommendation | Return, Rework, Retire, Review |

### Recommendation Logic

| Recommendation | Meaning |
|---|---|
| Return | Strong total value across scan rate, spend, repeat signal, or follow-up opportunity |
| Rework | Some value, but clear weakness in attendance conversion, spend, or repeat behavior |
| Retire | Weak total value across multiple measures |
| Review | Mixed result that needs more context |

### Key Insight Examples

The dashboard should make insights like these possible:

- Fireworks drew strong attendance but did not always create the highest spend per fan.
- A theme night produced moderate attendance but strong merch lift.
- A family promotion created strong concession value and repeat opportunity.
- A promotion looked successful by attendance but had weak scan conversion.
- A promotion should be reworked because it created interest but not enough follow-up value.

---

## Page 3: CRM Follow-Up Queue

### Primary Business Question

Which fans or accounts should sales and marketing follow up with first?

### Purpose

This page turns connected reporting into action.

The queue should prioritize fans and accounts based on behavior, not just ticket spend.

### Recommended Filters

| Filter | Purpose |
|---|---|
| Priority Band | High, medium, monitor, low |
| Segment | Focus on fan type |
| Opportunity Type | Filter by no-show, theme follow-up, group renewal, etc. |
| Assigned Team | Sales, marketing, group sales, service |
| Season | Review by season |
| Homestand ID | Review post-homestand queue |
| Promo Category | Connect follow-up to promotion behavior |

### KPI Cards

| KPI | Definition |
|---|---|
| High-Priority Follow-Ups | Count of high-priority tasks |
| Medium-Priority Follow-Ups | Count of medium-priority tasks |
| No-Show Recovery Targets | Valuable no-shows worth contacting |
| Group Renewal Targets | Group accounts flagged for renewal |
| Hidden High-Value Fans | Fans undervalued by ticket-only reporting |
| Avg Priority Score | Average priority score of current queue |
| Estimated Future Opportunity Index | Average future opportunity score |

### Core Visuals

| Visual | Purpose |
|---|---|
| Follow-up queue table | Operational list for sales/marketing |
| Priority by segment | Show which segments need action |
| Opportunity type breakdown | Show why fans/accounts qualify |
| Hidden high-value fan table | Show fans missed by ticket-only value |
| Group account priority table | Show account-level renewal/upsell targets |
| Suggested next action breakdown | Show recommended workflow |

### Follow-Up Queue Table Fields

| Field | Purpose |
|---|---|
| Fan ID | Synthetic fan identifier |
| Account ID | Group/corporate account identifier if applicable |
| Segment | Fan/account segment |
| Last Game Attended | Most recent scanned game |
| Last Purchase Date | Most recent purchase |
| Promo/Theme Attended | Promotion context |
| Ticket Spend | Synthetic ticket value |
| Merch Spend | Synthetic merch value |
| Concession Spend | Synthetic concession value |
| Total Fan Value Score | Connected fan value |
| Repeat Likelihood | Rule-based likelihood score |
| Future Opportunity Index | Rule-based future opportunity score |
| Upgrade Potential | Higher-value offer fit |
| Priority Score | Follow-up ranking |
| Priority Band | High, medium, monitor, low |
| Opportunity Type | Reason for follow-up |
| Suggested Action | Recommended next step |
| Assigned Team | Sales, marketing, group sales, service |
| Status | Open, completed, deferred, dismissed |

### Suggested Next Actions

| Opportunity Type | Suggested Action |
|---|---|
| No-show recovery | Send recovery offer or personal follow-up |
| Theme-night follow-up | Invite to next related theme night |
| Family buyer | Offer family pack or kids-focused promotion |
| High in-park spender | Send merch or concession-linked offer |
| Repeat single-game buyer | Offer mini plan |
| Mini plan buyer | Offer season ticket conversation |
| Group buyer | Assign group renewal call |
| Corporate prospect | Assign business development outreach |
| Lapsed fan | Send reactivation campaign |
| High engagement fan | Send targeted offer |

### Key Insight Examples

The dashboard should make insights like these possible:

- A fan with low ticket spend creates high total value through merch and concessions.
- A no-show buyer is worth contacting because of prior value.
- A group account has strong renewal potential because of high scan rate and repeat activity.
- A theme-night buyer should receive a targeted promotion instead of a generic offer.
- Sales should prioritize fewer, higher-value contacts instead of every possible fan.

---

## Supporting Dashboard Concepts

These are useful but should not become separate dashboard pages yet.

### Fan Value Explorer

Possible future page.

Purpose:

- Identify hidden high-value fans
- Compare ticket spend vs in-park spend
- Show repeat likelihood by segment
- Show upgrade paths

### Data Connection Map

Possible portfolio screenshot or documentation visual.

Purpose:

- Show how source systems connect
- Explain why Snowflake is being used
- Make the project easier for recruiters and leadership to understand

### Group Sales Drilldown

Possible future page.

Purpose:

- Prioritize group renewal and upsell opportunities
- Compare account types
- Show group scan rates and repeat behavior

---

## Core Metrics

### Tickets Sold

Synthetic count of tickets sold for a game, promotion, or homestand.

### Scanned Attendance

Synthetic count of tickets scanned for a game.

### Scan Rate

Scanned attendance divided by tickets sold.

### No-Show Rate

Tickets sold minus scanned attendance, divided by tickets sold.

### In-Park Spend Per Scanned Fan

Merch plus concession net sales divided by scanned attendance.

### Total Revenue Indicator

Synthetic sum of ticket, group, merch, and concession value.

This is not actual team revenue.

### Total Value Index

Weighted 0-100 score used to compare games and promotions.

Recommended components:

- ticket sales score
- scan rate score
- group sales score
- in-park spend score
- repeat buyer signal
- follow-up opportunity score

### Repeat Likelihood

Rule-based 0-100 score estimating how likely a fan is to return.

### Future Opportunity Index

Rule-based 0-100 score estimating future value opportunity.

### Priority Score

Rule-based 0-100 score used to rank the follow-up queue.

### Hidden High-Value Fan Flag

Identifies fans who look average in ticket data but strong when merch, concessions, and scan reliability are included.

---

## Tableau Data Sources

Tableau Public should use flat export files.

Recommended files:

| File | Dashboard Use |
|---|---|
| tableau_game_connected_summary.csv | Homestand Intelligence |
| tableau_homestand_summary.csv | Homestand Intelligence |
| tableau_promotion_scorecard.csv | Promotion Scorecard |
| tableau_crm_follow_up_queue.csv | CRM Follow-Up Queue |
| tableau_group_account_priority.csv | CRM Follow-Up Queue |
| tableau_fan_value_segments.csv | Fan value filters and segment analysis |

These exports can come from Snowflake views or from Python-generated processed files before Snowflake is opened.

---

## Design Requirements

The dashboard should be clean, executive-ready, and practical.

Design principles:

- Use clear page titles.
- Use action-oriented section headers.
- Avoid clutter.
- Use filters sparingly.
- Prioritize decisions over decoration.
- Show the business question on each page.
- Use tooltips to explain synthetic fields.
- Label synthetic data clearly.
- Keep recruiter/hiring manager readability in mind.

---

## Required Data Disclaimer

Each dashboard should include a short data note.

Recommended wording:

Public data is used where available. Internal-style records such as fan accounts, ticket orders, scans, merch, concessions, engagement, and CRM follow-up tasks are synthetic and created for portfolio demonstration purposes.

---

## Dashboard Boundaries

The dashboard will not include:

- predictive attendance modeling
- exact fan lifetime value
- real sponsorship ROI
- weather modeling
- player/team performance impact
- real-time pipeline monitoring
- item-level concession profitability
- advanced machine learning

The dashboard focuses on connected reporting, business logic, and decision support.

---

## Final Dashboard Statement

The Tableau dashboard should prove that connected reporting changes the quality of business decisions.

Attendance alone can show crowd size.

Connected reporting can show total value.

The dashboard should help users see:

- which games created value
- which promotions deserve action
- which fans are hidden high-value opportunities
- which group accounts should be contacted
- which reports need to connect for better decisions

That is the purpose of the Trash Pandas Connected Reporting Pilot.