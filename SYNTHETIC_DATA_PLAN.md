# Synthetic Data Plan

## Purpose

This file defines how synthetic data will be created for the Trash Pandas Connected Reporting Pilot.

The project uses public data for schedule, promotions, game context, and announced attendance where available. Internal-style business records are generated with Python to model how a Minor League Baseball team could connect ticketing, scans, fan accounts, merch, concessions, group sales, engagement, and follow-up workflows in Snowflake.

Synthetic data is not real Trash Pandas internal data.

The purpose is to create realistic business patterns that support a connected reporting proof-of-concept.

---

## Synthetic Data Principle

Synthetic data should support business logic, not fake certainty.

The data should create realistic variation across:

- games
- promotions
- homestands
- fan segments
- ticket behavior
- scan behavior
- in-park spend
- group sales
- fan engagement
- follow-up priority

The synthetic data should include both strong and weak outcomes.

Not every promotion should perform well.

Not every high-attendance game should create high total value.

Not every fan should attend often.

Not every fan should be linked to merch or concession purchases.

---

## Public Data Anchor

The synthetic data will be anchored to public game-level context.

Public anchor fields include:

- season
- game date
- opponent
- home/away status
- day of week
- month
- homestand ID
- promotion name
- promotion category
- announced attendance where available

These public fields create the schedule and event context.

Synthetic records are then generated around that context.

---

## Core Synthetic Outputs

The Python build should generate the following synthetic CSV files:

| File | Purpose |
|---|---|
| fans.csv | Synthetic fan account base |
| fan_segments.csv | Segment assignments for each fan |
| ticket_orders.csv | Ticket order header records |
| ticket_order_items.csv | Ticket-level or order-line records |
| ticket_scans.csv | Scan and no-show behavior |
| group_accounts.csv | Group sales account base |
| group_sales.csv | Group sales purchase records |
| merch_transactions.csv | Fan-linked and game-linked merch purchases |
| concession_transactions.csv | Fan-linked and game-linked concession purchases |
| sponsorship_activations.csv | Sponsor context for games/promotions |
| fan_engagement.csv | Synthetic marketing and engagement signals |
| follow_up_opportunity_pool.csv | All qualified follow-up opportunities |
| crm_follow_up_tasks.csv | Prioritized working follow-up queue |

---

## Fan Base Size

The synthetic fan base should be large enough to support realistic segmentation but not so large that the project becomes heavy.

Target range:

| Dataset | Target Volume |
|---|---:|
| Fans | 35,000-55,000 |
| Ticket Orders | 75,000-125,000 |
| Ticket Order Items | 150,000-300,000 |
| Merch Transactions | 20,000-45,000 |
| Concession Transactions | 60,000-140,000 |
| Group Accounts | 750-1,500 |
| Group Sales | 2,000-5,000 |
| Fan Engagement Records | 50,000-150,000 |
| Follow-Up Opportunity Pool | 20,000-45,000 |
| CRM Follow-Up Tasks | 8,000-20,000 |

These are target ranges, not mandatory exact counts.

The final record counts should be documented in the quality check output.

---

## Fan Attendance Segments

The synthetic fan base should include different attendance behaviors across the 2023-2025 seasons.

| Segment | Attendance Pattern | Business Purpose |
|---|---|---|
| One-Time Buyer | Attends once across three seasons | Models casual/event-only fans |
| Occasional Fan | Attends 2-4 games across three seasons | Models light repeat behavior |
| Repeat Single-Game Buyer | Attends 5-10 games | Creates follow-up and upgrade opportunities |
| Mini Plan Buyer | Attends 8-15 games in a season | Models partial-plan value |
| Season Ticket Holder | Holds many tickets across a season | Creates scan/no-show and retention logic |
| Group Buyer | Attends through group purchases | Supports renewal and upsell analysis |
| Theme Night Buyer | Attends games tied to themes | Supports promotion follow-up logic |
| Family Buyer | Attends family-oriented games | Supports family pack and concessions logic |
| High In-Park Spender | Spends heavily on merch/concessions | Supports hidden fan value analysis |
| Lapsed Fan | Previously active, then inactive | Supports reactivation logic |

A fan can belong to more than one segment.

Example:

A fan can be both a Family Buyer and a High In-Park Spender.

---

## Fan Segment Distribution Rules

The fan base should not be evenly distributed across segments.

Recommended starting distribution:

| Segment | Target Share |
|---|---:|
| One-Time Buyer | 35-45% |
| Occasional Fan | 25-35% |
| Repeat Single-Game Buyer | 12-18% |
| Mini Plan Buyer | 5-8% |
| Season Ticket Holder | 2-5% |
| Group Buyer | 3-7% |
| Theme Night Buyer | 10-20% |
| Family Buyer | 12-25% |
| High In-Park Spender | 8-15% |
| Lapsed Fan | 8-18% |

These ranges can overlap because segment assignments are not mutually exclusive.

---

## Ticket Sales Generation Rules

Ticket sales should be synthetic but anchored to public game context.

Ticket demand should vary by:

- day of week
- month
- promotion category
- homestand
- opponent
- fan segment
- group sales activity
- ticket type

Stronger demand factors:

- Friday games
- Saturday games
- fireworks
- giveaways
- family games
- major theme nights
- group-heavy games
- summer dates
- strong homestand momentum

Weaker demand factors:

- Tuesday and Wednesday games
- school-year weekday games
- low-promotion games
- games with limited event hook
- late-season games with weaker context

Ticket sales should not exactly equal announced attendance.

---

## Ticket Type Rules

Synthetic ticket orders should include multiple ticket types.

| Ticket Type | Description |
|---|---|
| Single Game | Standard single-game ticket |
| Mini Plan | Partial-plan ticket package |
| Season Ticket | Season ticket holder allocation |
| Group | Group account purchase |
| Premium | Higher-value seating or hospitality |
| Comp | Complimentary or non-revenue ticket |
| Partner | Sponsor or partner-related ticket |

Ticket type affects scan behavior, no-show behavior, and follow-up logic.

---

## Ticket Scan Rules

Ticket scans represent attendance conversion.

Scanned attendance should usually be lower than tickets sold.

Scan behavior should vary by:

- ticket type
- fan segment
- promotion category
- purchase timing
- day of week
- group size
- attendance history
- season ticket behavior

General rules:

- Single-game buyers who purchase close to game date have stronger scan rates.
- Season ticket holders can have unused tickets.
- Group buyers can have moderate no-show risk due to group size.
- Fireworks, giveaways, and family games can reduce no-show risk.
- Weekday games can increase no-show risk.
- Lapsed or low-engagement fans have weaker scan reliability.

---

## No-Show Recovery Rules

The project should recover valuable no-shows, not every no-show.

A fan qualifies as a no-show recovery opportunity when:

- the fan purchased a ticket
- the ticket was not scanned
- the fan has prior attendance, spend, group, premium, or engagement value
- the fan has not already been contacted recently

Exclude one-time buyers with no prior value unless they bought premium or group tickets.

No-show recovery should feed the follow-up opportunity pool.

---

## Merch Transaction Rules

Merch transactions show fan spending beyond tickets.

Fan matching rule:

- 60-75% of merch transactions are linked to fan_id
- remaining merch transactions are tied only to game_id

Merch spend should vary by:

- promotion category
- theme nights
- jersey auctions
- giveaways
- fan segment
- attendance frequency
- family behavior
- high in-park spender flag

Merch behavior rules:

- Most fans do not buy merch every game.
- Theme nights increase merch purchase probability.
- Jersey auction and specialty jersey games increase merch value.
- First-time fans can buy souvenir items.
- Repeat fans buy less often but can have larger baskets.
- High in-park spenders should show stronger merch behavior.

Recommended item categories:

- jersey
- hat
- novelty
- kids
- theme_item
- collectible
- apparel
- souvenir

---

## Concession Transaction Rules

Concession transactions show in-park food and beverage behavior.

Fan matching rule:

- 35-55% of concession transactions are linked to fan_id
- remaining concession transactions are tied only to game_id

Concession spend should vary by:

- scanned attendance
- family behavior
- group behavior
- weekend games
- game duration proxy if modeled
- promotion type
- weather context if added later
- high in-park spender flag

Concession behavior rules:

- Concession spend is more common than merch spend.
- Families and groups should create higher concession activity.
- Weekend games should create stronger concession volume.
- High-attendance games should not automatically have the highest per-fan spend.
- Some average-attendance games should perform well on concession value.

Recommended item categories:

- food
- beverage
- snack
- dessert
- family_item
- premium_item

---

## Group Account Rules

Group accounts represent organizations and larger buyer relationships.

Recommended account types:

- corporate
- school
- church
- youth_sports
- nonprofit
- community_group
- local_business
- healthcare
- military
- civic_group

Group account behavior should vary by:

- account type
- previous purchase history
- group ticket quantity
- scan rate
- renewal timing
- engagement
- promotion fit
- family/community fit

Group accounts should be scored separately from individual fans.

---

## Group Sales Rules

Group sales records should connect:

- account_id
- game_id
- ticket order
- group ticket quantity
- group revenue
- group scan rate
- renewal flag
- upsell flag

Group sales should be stronger around:

- community promotions
- school nights
- youth sports nights
- faith/community nights
- business/networking events
- weekend games
- family-oriented promotions

Not every group sale should become a renewal target.

The renewal and upsell logic should depend on value, scan rate, repeat behavior, and timing.

---

## Sponsorship Activation Rules

Sponsorship is context only.

The project does not calculate sponsorship ROI.

Sponsorship records should identify whether a game or promotion had partner context.

Recommended activation types:

- giveaway
- theme night
- concourse table
- signage
- digital campaign
- community activation
- pregame recognition
- hospitality

Sponsorship context can be used to filter or describe game and promotion performance, but not to claim ROI.

---

## Fan Engagement Rules

Fan engagement records support repeat likelihood and follow-up priority.

Recommended engagement types:

- email_open
- email_click
- sms_response
- qr_scan
- survey_response
- app_activity
- offer_response
- social_engagement
- website_visit

Engagement should vary by:

- fan segment
- recent attendance
- promotion affinity
- prior purchases
- opt-in status
- campaign type

Engagement should not be evenly distributed.

Higher engagement should increase:

- repeat likelihood
- follow-up priority
- upgrade potential

---

## Follow-Up Opportunity Pool Rules

The follow-up opportunity pool includes all fans and accounts that qualify for possible action.

Opportunity types include:

- no_show_recovery
- theme_night_follow_up
- group_renewal
- group_upsell
- family_pack_offer
- mini_plan_upgrade
- merch_offer
- lapsed_fan_reactivation
- high_in_park_spender_follow_up
- corporate_prospecting

A fan or account can have multiple opportunity records.

The opportunity pool should be broader than the final CRM task list.

---

## CRM Follow-Up Task Rules

CRM follow-up tasks represent the prioritized working queue.

Tasks should be created from the opportunity pool when priority logic crosses the task threshold.

Recommended threshold:

- priority_score >= 65

CRM task records should include:

- follow_up_id
- opportunity_id
- fan_id or account_id
- game_id
- assigned_team
- assigned_owner
- suggested_action
- priority_score
- priority_band
- due_date
- status
- outcome

The CRM follow-up task list should be smaller than the opportunity pool.

This keeps the workflow realistic.

---

## Repeat Likelihood Score

Repeat likelihood is rule-based.

It is not a machine learning model.

Formula:

```text
Repeat Likelihood =
0.30 * Recency Score
+ 0.25 * Frequency Score
+ 0.20 * Promo/Theme Affinity Score
+ 0.15 * Engagement Score
+ 0.10 * Scan Reliability Score