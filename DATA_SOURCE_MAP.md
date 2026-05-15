# Data Source Map

## Purpose

The Data Source Map defines where each business data source comes from, what level of detail it contains, how it connects to other sources, and how it supports the Trash Pandas Connected Reporting Pilot.

This project does not assume access to internal Trash Pandas systems.

The goal is to model how separate business reports can be connected in Snowflake to support better decisions around game value, promotion performance, fan behavior, group sales, and follow-up opportunities.

---

## Data Classification

Each data source is classified as one of three types:

| Classification | Meaning |
|---|---|
| Public | Data collected from public sources such as published schedules, promotions, game dates, opponents, and announced attendance |
| Synthetic | Data generated with Python to represent internal-style business data that is not publicly available |
| Internal-Only | Data that exists inside team systems in a production environment, represented synthetically in this project |

For this portfolio project, internal-only fields are not real internal Trash Pandas data. They are modeled synthetically to demonstrate the reporting structure.

---

## Source System Overview

For this proof-of-concept, the source system represents the business report, platform export, or operational data feed that would supply Snowflake in a connected reporting environment.

| Business Area | Source System | Project Data Type | Snowflake Layer |
|---|---|---|---|
| Games/Schedule | Team website, MiLB schedule pages, public schedule files | Public | RAW → STAGING |
| Promotions | Team promotion schedule, public promo pages | Public + synthetic tags | RAW → STAGING |
| Announced Attendance | Public box scores, game logs, published attendance sources | Public | RAW → STAGING |
| Ticket Sales | Ticketing platform or ticket export | Synthetic / internal-style | RAW → STAGING |
| Ticket Scans | Access control / gate scan system | Synthetic / internal-style | RAW → STAGING |
| Fan Accounts | CRM, ticketing CRM, marketing database | Synthetic / internal-style | RAW → STAGING |
| Fan Segments | CRM segmentation or analytics scoring | Synthetic | STAGING → ANALYTICS |
| Group Accounts | Group sales CRM or sales pipeline | Synthetic / internal-style | RAW → STAGING |
| Group Sales | Ticketing/group sales reports | Synthetic / internal-style | RAW → STAGING |
| Merch Transactions | Retail POS, team store, online store | Synthetic / internal-style | RAW → STAGING |
| Concession Transactions | Concessions POS | Synthetic / internal-style | RAW → STAGING |
| Sponsorship Activations | Partnership tracking, activation calendar | Synthetic context only | RAW → STAGING |
| Fan Engagement | Email, SMS, app, social, survey, campaign tools | Synthetic / internal-style | RAW → STAGING |
| CRM Follow-Ups | CRM tasks, sales activity, marketing workflows | Synthetic / internal-style | STAGING → ANALYTICS |
| Revenue Summary | Finance/revenue reports | Synthetic / internal-style | ANALYTICS → EXPORTS |

---

## Source 1: Games / Schedule

### Purpose

The games table is the foundation of the reporting layer. Every promotion, ticket sale, scan, group sale, merch transaction, concession transaction, and follow-up opportunity connects back to a game when possible.

### Grain

One row per game.

### Project Classification

Public.

### Key Fields

| Field | Description |
|---|---|
| game_id | Unique project-generated game identifier |
| season | Season year |
| game_date | Date of game |
| home_away | Home or away flag |
| opponent | Opposing team |
| day_of_week | Day of week |
| start_time | Scheduled start time if available |
| homestand_id | Manually assigned ID for consecutive home-game blocks |
| series_id | Optional series identifier |
| game_number_in_homestand | Order of game within homestand |
| month | Game month |
| weekend_flag | Indicates Friday/Saturday/Sunday game |
| holiday_flag | Indicates holiday or special calendar context if known |

### Join Keys

| Join Key | Connects To |
|---|---|
| game_id | Promotions, attendance, tickets, scans, group sales, merch, concessions, sponsorship, engagement, follow-ups |
| game_date | Public attendance, schedule validation, promotions |
| homestand_id | Homestand reporting views |

### Reporting Purpose

Supports game-level and homestand-level reporting.

Used to answer:

- Which games created the most total value?
- Which homestands performed best?
- Which day-of-week slots performed better?
- Which games should be compared against similar schedule contexts?

---

## Source 2: Promotions

### Purpose

Promotion data explains what theme, giveaway, or event was attached to each game.

This is central to the Promotion Performance Scorecard.

### Grain

One row per promotion per game.

A game can have multiple promotions.

### Project Classification

Public + synthetic tags.

The promotion name comes from public sources when available. Standardized promotion categories and scoring tags are created for analysis.

### Key Fields

| Field | Description |
|---|---|
| promo_id | Unique promotion identifier |
| game_id | Connected game |
| promo_name | Promotion name |
| promo_category | Standardized promotion category |
| promo_type | Theme, giveaway, fireworks, family, dog day, community, jersey auction, group, etc. |
| sponsor_attached_flag | Whether sponsor activation is attached |
| giveaway_flag | Whether item giveaway is attached |
| fireworks_flag | Whether fireworks are attached |
| theme_night_flag | Whether theme night is attached |
| family_flag | Whether family/kids positioning is attached |
| dog_day_flag | Whether dog-related promotion is attached |
| jersey_auction_flag | Whether jersey auction/specialty jersey is attached |
| expected_fan_segment | Synthetic expected audience fit |

### Join Keys

| Join Key | Connects To |
|---|---|
| game_id | Games, tickets, scans, merch, concessions, group sales |
| promo_id | Sponsorship activations, promotion scorecard |
| promo_category | Promo category analysis |

### Reporting Purpose

Supports promotion value analysis.

Used to answer:

- Which promotions should return?
- Which promotions drove scanned attendance?
- Which promotions drove merch or concession lift?
- Which themes created follow-up opportunities?
- Which promotions created wallets, not just crowds?

---

## Source 3: Announced Attendance

### Purpose

Announced attendance provides a public attendance anchor.

It should not be treated as scanned attendance.

### Grain

One row per home game.

### Project Classification

Public.

### Key Fields

| Field | Description |
|---|---|
| attendance_id | Unique attendance record ID |
| game_id | Connected game |
| game_date | Game date |
| announced_attendance | Publicly announced attendance |
| attendance_source | Source reference or collection note |
| attendance_note | Any limitation or reconciliation note |

### Join Keys

| Join Key | Connects To |
|---|---|
| game_id | Games, reporting views |
| game_date | Schedule validation |

### Reporting Purpose

Supports public baseline reporting.

Used to answer:

- What was the announced attendance?
- How does announced attendance compare to synthetic tickets sold?
- How does announced attendance compare to synthetic scanned attendance?

### Important Assumption

Announced attendance is used as a public anchor. It is not assumed to equal true scanned attendance.

---

## Source 4: Ticket Sales

### Purpose

Ticket sales data represents ticket demand and purchase behavior.

In a production sports business environment, this data comes from a ticketing platform or ticket export.

### Grain

One row per ticket order and one row per order item.

For this project, we will model both:

- ticket order header
- ticket order item/detail

### Project Classification

Synthetic / internal-style.

### Key Fields

| Field | Description |
|---|---|
| order_id | Unique ticket order ID |
| order_item_id | Unique ticket order line/item ID |
| game_id | Game purchased |
| fan_id | Buyer account |
| account_id | Group account if applicable |
| order_date | Date purchased |
| ticket_type | Single game, mini plan, season ticket, group, premium, comp, etc. |
| ticket_quantity | Number of tickets |
| section_type | General seating category |
| gross_ticket_revenue | Synthetic gross ticket revenue |
| discount_amount | Synthetic discount amount |
| net_ticket_revenue | Synthetic net ticket revenue |
| purchase_channel | Online, phone, box office, group sales, partner, etc. |
| group_order_flag | Indicates group sale |
| premium_flag | Indicates premium ticket type |

### Join Keys

| Join Key | Connects To |
|---|---|
| order_id | Ticket order items, scans |
| order_item_id | Scans |
| game_id | Games, promotions, attendance |
| fan_id | Fans, engagement, merch, concessions, follow-ups |
| account_id | Group accounts, group sales |

### Reporting Purpose

Supports demand and sales analysis.

Used to answer:

- Which games sold the most tickets?
- Which ticket types drive value?
- Which fans purchased but did not scan?
- Which fan segments buy repeatedly?
- Which group accounts have renewal or upsell potential?

---

## Source 5: Ticket Scans

### Purpose

Ticket scan data shows who attended.

This is critical because ticket sales and attendance are not the same thing.

### Grain

One row per ticket/order item scan status.

### Project Classification

Synthetic / internal-style.

### Key Fields

| Field | Description |
|---|---|
| scan_id | Unique scan record ID |
| order_item_id | Ticket/order item connected to scan |
| order_id | Ticket order |
| game_id | Game |
| fan_id | Fan account if known |
| scan_status | Scanned or not scanned |
| scan_time | Time of scan if scanned |
| gate | Gate location if modeled |
| no_show_flag | Indicates purchased ticket was not scanned |
| scan_match_confidence | Optional synthetic match confidence |

### Join Keys

| Join Key | Connects To |
|---|---|
| order_item_id | Ticket order item |
| order_id | Ticket order |
| game_id | Games |
| fan_id | Fans, follow-ups |

### Reporting Purpose

Supports attendance conversion analysis.

Used to answer:

- Which games sold tickets but had weak scan rates?
- Which fans are reliable attendees?
- Which no-show buyers are worth recovering?
- Which promotions create actual attendance instead of only ticket sales?

---

## Source 6: Fan Accounts

### Purpose

Fan accounts represent the customer base.

The goal is not to claim real fan data. The goal is to model how fan-level reporting works when ticketing, scans, merch, concessions, and engagement are connected.

### Grain

One row per fan account.

### Project Classification

Synthetic / internal-style.

### Key Fields

| Field | Description |
|---|---|
| fan_id | Unique synthetic fan ID |
| household_id | Optional household grouping |
| first_seen_date | First synthetic purchase or engagement date |
| last_seen_date | Most recent synthetic activity |
| zip_code | Synthetic local/regional ZIP |
| market_distance_band | Local, regional, out-of-market |
| email_opt_in_flag | Marketing opt-in |
| sms_opt_in_flag | SMS opt-in |
| family_flag | Family buyer signal |
| corporate_flag | Corporate prospect signal |
| youth_sports_flag | Youth/team group signal |
| fan_created_source | Ticketing, group sale, promotion, event, etc. |

### Join Keys

| Join Key | Connects To |
|---|---|
| fan_id | Ticket orders, scans, merch, concessions, engagement, follow-ups |
| household_id | Household-level analysis |
| zip_code | Market-distance analysis |

### Reporting Purpose

Supports customer-level reporting.

Used to answer:

- Which fans create the most total value?
- Which fans are hidden high-value fans?
- Which fans should sales or marketing contact?
- Which fans have repeat or upgrade potential?

---

## Source 7: Fan Segments

### Purpose

Fan segments group fans into useful business categories.

Segments help move from raw data to action.

### Grain

One row per fan per assigned segment.

A fan can belong to more than one segment.

### Project Classification

Synthetic.

### Key Fields

| Field | Description |
|---|---|
| fan_segment_id | Unique segment assignment ID |
| fan_id | Connected fan |
| segment_name | Segment label |
| segment_type | Behavioral, value, lifecycle, sales, marketing |
| assigned_date | Date assigned |
| active_flag | Whether segment is current |
| segment_score | Optional score for strength of segment fit |

### Recommended Segments

| Segment | Description |
|---|---|
| Season Ticket Holder | High-frequency ticket buyer |
| Mini Plan Buyer | Partial-plan buyer |
| Repeat Single-Game Buyer | Buys individual games repeatedly |
| One-Time Buyer | Attends once across the modeled period |
| Theme Night Buyer | Attends theme-driven games |
| Family Buyer | Family/kids-oriented behavior |
| Group Buyer | Associated with group sales |
| Corporate Prospect | Potential business/corporate account |
| High In-Park Spender | Strong merch/concession behavior |
| No-Show Recovery Target | Valuable buyer who missed a game |
| Lapsed Fan | Previously active, now inactive |

### Join Keys

| Join Key | Connects To |
|---|---|
| fan_id | Fans, orders, scans, spend, engagement, follow-ups |
| segment_name | Dashboard filters and scoring logic |

### Reporting Purpose

Supports audience targeting and follow-up prioritization.

Used to answer:

- Which segments create the most value?
- Which segments overperform in merch/concessions?
- Which segments should receive different offers?
- Which segments are most likely to repeat?

---

## Source 8: Group Accounts

### Purpose

Group accounts represent organizations, companies, schools, churches, teams, community groups, and other buyers that purchase blocks of tickets.

### Grain

One row per account.

### Project Classification

Synthetic / internal-style.

### Key Fields

| Field | Description |
|---|---|
| account_id | Unique group account ID |
| account_name | Synthetic account name |
| account_type | Corporate, school, church, youth sports, nonprofit, community, etc. |
| account_owner | Synthetic sales rep or owner |
| industry | Optional business category |
| city | Synthetic city |
| zip_code | Synthetic ZIP |
| first_purchase_date | First group purchase |
| last_purchase_date | Most recent group purchase |
| renewal_status | New, active, renewal target, lapsed |
| corporate_prospect_flag | Indicates partnership or premium potential |

### Join Keys

| Join Key | Connects To |
|---|---|
| account_id | Group sales, ticket orders, CRM follow-ups |
| zip_code | Market analysis |

### Reporting Purpose

Supports group sales renewal and upsell analysis.

Used to answer:

- Which group accounts are highest priority?
- Which accounts should be renewed or upsold?
- Which group types produce strong scan rates?
- Which group accounts create in-park value?

---

## Source 9: Group Sales

### Purpose

Group sales data tracks ticket blocks and account-level purchases.

### Grain

One row per group account per game purchase.

### Project Classification

Synthetic / internal-style.

### Key Fields

| Field | Description |
|---|---|
| group_sale_id | Unique group sale ID |
| account_id | Group account |
| game_id | Game purchased |
| order_id | Related ticket order if applicable |
| group_ticket_quantity | Number of group tickets |
| group_ticket_revenue | Synthetic group ticket revenue |
| group_type | School, church, company, youth sports, nonprofit, etc. |
| event_type | Outing, fundraiser, corporate night, team event, etc. |
| renewal_flag | Whether account is eligible for renewal |
| upsell_flag | Whether account is eligible for upsell |
| group_scan_rate | Synthetic scan rate for group block |

### Join Keys

| Join Key | Connects To |
|---|---|
| group_sale_id | Group reporting |
| account_id | Group accounts, follow-ups |
| game_id | Games, promotions |
| order_id | Ticket orders |

### Reporting Purpose

Supports group sales performance and account prioritization.

Used to answer:

- Which group accounts should sales contact?
- Which group types perform best?
- Which group-heavy games created total value?
- Which group accounts have renewal or upsell potential?

---

## Source 10: Merch Transactions

### Purpose

Merch transactions show fan spending beyond tickets.

This source is important because some fans are more valuable than ticket-only reporting suggests.

### Grain

One row per merch transaction.

### Project Classification

Synthetic / internal-style.

### Fan Match Assumption

60-75% of merch transactions are linked to fan_id.

Remaining transactions are tied only to game_id.

### Key Fields

| Field | Description |
|---|---|
| merch_transaction_id | Unique merch transaction ID |
| game_id | Game context |
| fan_id | Fan account if matched |
| transaction_date | Date of purchase |
| transaction_time | Time of purchase |
| item_category | Jersey, hat, novelty, kids, theme item, etc. |
| quantity | Items purchased |
| gross_sales | Synthetic gross sales |
| discount_amount | Synthetic discount |
| net_sales | Synthetic net sales |
| channel | Stadium store, kiosk, online, mobile |
| promo_related_flag | Whether purchase is tied to promo/theme |
| fan_match_flag | Whether transaction links to fan_id |

### Join Keys

| Join Key | Connects To |
|---|---|
| merch_transaction_id | Merch reporting |
| game_id | Games, promotions, homestands |
| fan_id | Fans, fan segments, follow-ups |

### Reporting Purpose

Supports in-park value and hidden fan value analysis.

Used to answer:

- Which games drove merch lift?
- Which promotions drove merch purchases?
- Which fans are high-value merch buyers?
- Which low-ticket fans become valuable when merch is included?

---

## Source 11: Concession Transactions

### Purpose

Concession transactions show in-park food and beverage behavior.

This source helps measure the value of getting fans into the ballpark.

### Grain

One row per concession transaction.

### Project Classification

Synthetic / internal-style.

### Fan Match Assumption

35-55% of concession transactions are linked to fan_id.

Remaining transactions are tied only to game_id.

### Key Fields

| Field | Description |
|---|---|
| concession_transaction_id | Unique concession transaction ID |
| game_id | Game context |
| fan_id | Fan account if matched |
| transaction_date | Date of purchase |
| transaction_time | Time of purchase |
| stand_category | Main stand, portable, premium area, dessert, beverage, etc. |
| item_category | Food, beverage, snack, family item, premium item |
| quantity | Items purchased |
| gross_sales | Synthetic gross sales |
| discount_amount | Synthetic discount |
| net_sales | Synthetic net sales |
| fan_match_flag | Whether transaction links to fan_id |

### Join Keys

| Join Key | Connects To |
|---|---|
| concession_transaction_id | Concession reporting |
| game_id | Games, promotions, homestands |
| fan_id | Fans, fan segments, follow-ups |

### Reporting Purpose

Supports fan value and in-park spend analysis.

Used to answer:

- Which games drove concession lift?
- Which fan segments spend most inside the ballpark?
- Which average-attendance games created strong in-park value?
- Which fans are valuable beyond ticket spend?

---

## Source 12: Sponsorship Activations

### Purpose

Sponsorship activation data provides context for games and promotions that include partner involvement.

This project will not calculate sponsorship ROI.

### Grain

One row per sponsor activation per game.

### Project Classification

Synthetic context only.

### Key Fields

| Field | Description |
|---|---|
| activation_id | Unique activation ID |
| game_id | Game |
| promo_id | Promotion if attached |
| sponsor_id | Synthetic sponsor ID |
| sponsor_category | Local business, healthcare, auto, restaurant, etc. |
| activation_type | Giveaway, theme night, concourse table, signage, digital, community |
| activation_location | Ballpark, digital, concourse, field, pregame |
| activation_goal | Awareness, lead capture, community, sales, hospitality |
| sponsor_attached_flag | Whether game/promo has sponsor context |

### Join Keys

| Join Key | Connects To |
|---|---|
| game_id | Games, promotions |
| promo_id | Promotion scorecard |
| sponsor_id | Sponsorship context reporting |

### Reporting Purpose

Adds context to game and promotion performance.

Used to answer:

- Which sponsor-linked games also drove attendance, spend, or engagement?
- Which promotion categories frequently have sponsor activation?
- Where would sponsorship data need to connect in a real reporting layer?

### Important Limitation

This project will not calculate sponsorship ROI because that would require internal contract terms, fulfillment data, impression tracking, and sponsor goals.

---

## Source 13: Fan Engagement

### Purpose

Fan engagement data shows marketing and interaction signals beyond purchases.

### Grain

One row per fan engagement event.

### Project Classification

Synthetic / internal-style.

### Key Fields

| Field | Description |
|---|---|
| engagement_id | Unique engagement event ID |
| fan_id | Fan account |
| game_id | Game if tied to specific event |
| campaign_id | Campaign identifier |
| engagement_date | Date of engagement |
| engagement_type | Email open, click, SMS, QR scan, survey, app, social, offer response |
| engagement_channel | Email, SMS, app, social, website, in-park |
| engagement_score | Synthetic score for interaction value |
| campaign_name | Campaign or offer name |
| promo_related_flag | Whether engagement ties to a promotion |

### Join Keys

| Join Key | Connects To |
|---|---|
| fan_id | Fans, segments, follow-ups |
| game_id | Games, promotions |
| campaign_id | Campaign reporting |

### Reporting Purpose

Supports repeat likelihood and follow-up scoring.

Used to answer:

- Which fans are engaged enough to contact?
- Which campaigns created follow-up signals?
- Which theme-night buyers showed engagement after the event?
- Which fans have repeat or upgrade potential?

---

## Source 14: Follow-Up Opportunity Pool

### Purpose

The follow-up opportunity pool identifies all fans and accounts who qualify for action.

This is broader than the actual CRM task list.

### Grain

One row per fan/account per opportunity reason.

A fan or account can have multiple opportunity reasons.

### Project Classification

Synthetic / internal-style.

### Key Fields

| Field | Description |
|---|---|
| opportunity_id | Unique opportunity ID |
| fan_id | Fan if individual opportunity |
| account_id | Group account if account opportunity |
| game_id | Game that created opportunity |
| homestand_id | Homestand context |
| opportunity_type | No-show recovery, theme follow-up, group renewal, merch offer, family pack, etc. |
| opportunity_reason | Explanation for why the record qualifies |
| opportunity_score | Rule-based score |
| priority_band | High, medium, monitor, low |
| source_signal | Ticket, scan, merch, concession, engagement, group |
| created_date | Opportunity creation date |

### Join Keys

| Join Key | Connects To |
|---|---|
| fan_id | Fans, fan segments, spend, engagement |
| account_id | Group accounts, group sales |
| game_id | Games, promotions |
| homestand_id | Homestand summary |

### Reporting Purpose

Supports action planning.

Used to answer:

- Which fans/accounts could be contacted?
- What business signal created the opportunity?
- Which games or promotions created the most qualified opportunities?

---

## Source 15: CRM Follow-Up Tasks

### Purpose

CRM follow-up tasks represent the prioritized working queue.

This table should be smaller than the full opportunity pool.

### Grain

One row per assigned follow-up task.

### Project Classification

Synthetic / internal-style.

### Key Fields

| Field | Description |
|---|---|
| follow_up_id | Unique follow-up task ID |
| opportunity_id | Related opportunity |
| fan_id | Fan if individual task |
| account_id | Account if group/corporate task |
| game_id | Game context |
| assigned_team | Sales, marketing, group sales, service |
| assigned_owner | Synthetic owner/rep |
| suggested_action | Recommended next action |
| priority_score | Rule-based priority score |
| priority_band | High, medium, monitor, low |
| due_date | Suggested task due date |
| status | Open, completed, deferred, dismissed |
| outcome | Renewal, purchase, no response, not contacted, etc. |

### Join Keys

| Join Key | Connects To |
|---|---|
| opportunity_id | Follow-up opportunity pool |
| fan_id | Fans |
| account_id | Group accounts |
| game_id | Games |

### Reporting Purpose

Supports the CRM Follow-Up Queue dashboard.

Used to answer:

- Who should sales contact first?
- What action should they take?
- Which opportunities are highest priority?
- Which departments own the next steps?

---

## Source 16: Revenue Summary / Reporting Views

### Purpose

Revenue summary data is not a raw source in the MVP. It is built from connected reporting views.

The project should avoid pretending to have actual financial truth.

### Grain

One row per game, promotion, homestand, fan, or account depending on the view.

### Project Classification

Synthetic / derived.

### Key Metrics

| Metric | Description |
|---|---|
| total_revenue_indicator | Synthetic sum of ticket, group, merch, concession, and sponsor context value if used |
| revenue_per_scanned_fan | Synthetic revenue indicator divided by scanned attendance |
| in_park_spend_per_scanned_fan | Merch plus concessions divided by scanned attendance |
| ticket_revenue | Synthetic ticket revenue |
| group_revenue | Synthetic group revenue |
| merch_revenue | Synthetic merch revenue |
| concession_revenue | Synthetic concession revenue |
| total_value_index | Weighted index for game or promotion value |
| future_opportunity_index | Rule-based index for future fan/account opportunity |

### Join Keys

| Join Key | Connects To |
|---|---|
| game_id | Game summary |
| promo_id | Promotion scorecard |
| homestand_id | Homestand summary |
| fan_id | Fan value summary |
| account_id | Group account priority |

### Reporting Purpose

Supports Tableau-ready executive reporting.

Used to answer:

- Which games created total value?
- Which promotions should return?
- Which fans/accounts should receive follow-up?
- Which homestands performed best?

---

## Highest-Value Joins

The most important joins in this project are:

| Join | Why It Matters |
|---|---|
| Games → Promotions | Connects game context to promotion strategy |
| Games → Announced Attendance | Adds public baseline |
| Ticket Orders → Ticket Scans | Separates tickets sold from fans who showed up |
| Fans → Ticket Orders | Connects purchase behavior to fan accounts |
| Fans → Ticket Scans | Measures attendance reliability |
| Fans → Merch Transactions | Identifies fans with value beyond ticket spend |
| Fans → Concession Transactions | Identifies in-park spend behavior |
| Games → Merch/Concessions | Shows which games created in-park value |
| Promotions → Merch/Concessions | Shows which promos created spend lift |
| Group Accounts → Group Sales | Supports renewal and upsell decisions |
| Fans/Accounts → Follow-Up Opportunities | Converts behavior into action |
| Follow-Up Opportunities → CRM Tasks | Converts signals into a working queue |

---

## MVP Source Priority

The MVP should focus on the sources that best support the core business questions.

### Tier 1: Required for MVP

| Source | Reason |
|---|---|
| Games/Schedule | Foundation for everything |
| Promotions | Needed for promotion scorecard |
| Announced Attendance | Public baseline |
| Ticket Sales | Needed for sales demand |
| Ticket Scans | Needed for no-show/scan-rate logic |
| Fans | Needed for customer-level reporting |
| Fan Segments | Needed for targeting and dashboard filters |
| Merch Transactions | Needed for hidden fan value |
| Concession Transactions | Needed for total fan value |
| Follow-Up Opportunity Pool | Needed for actionability |
| CRM Follow-Up Tasks | Needed for CRM queue |

### Tier 2: Important but Secondary

| Source | Reason |
|---|---|
| Group Accounts | Supports account-level sales action |
| Group Sales | Supports renewal/upsell logic |
| Fan Engagement | Supports repeat likelihood and priority scoring |

### Tier 3: Context Only

| Source | Reason |
|---|---|
| Sponsorship Activations | Useful context but not ROI analysis |
| Revenue Summary | Derived output, not raw source |

---

## Data Source Map Summary

This project models how a sports organization can connect separate reports into one Snowflake reporting layer.

The key business shift is moving from isolated reports to connected decision-making.

A ticket report can show what was sold.

A scan report can show who attended.

A merch report can show what fans bought.

A concession report can show in-park spend.

A CRM report can show who was contacted.

The value comes from connecting them.

That connection allows leadership to answer better questions:

- Which games created total fan value?
- Which promotions deserve future investment?
- Which fans are valuable beyond ticket spend?
- Which accounts should sales contact first?
- Which data sources need to connect to support better decisions?

This is the foundation of the Trash Pandas Connected Reporting Pilot.