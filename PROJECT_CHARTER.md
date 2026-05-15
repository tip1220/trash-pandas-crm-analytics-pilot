# Trash Pandas Connected Reporting Pilot

## Project Purpose

The Trash Pandas Connected Reporting Pilot is a sports business analytics proof-of-concept that shows how a Minor League Baseball team could connect fragmented business reports into one centralized reporting layer.

The project does not claim access to internal Trash Pandas data. It uses public data where available and clearly labeled synthetic data where internal business data would normally be required.

The goal is to demonstrate how leadership, sales, marketing, and promotions teams could make better decisions when ticketing, scans, promotions, group sales, merch, concessions, fan engagement, and CRM follow-up data are connected.

## One-Sentence Pitch

This project uses Snowflake, Python, SQL, and Tableau Public to model how the Trash Pandas could connect separate business reports into one reporting layer that identifies total fan value, promotion performance, and priority sales follow-up opportunities.

## Business Problem

Sports organizations often have valuable data spread across separate systems and department workflows.

A team may have separate reports for:

- ticketing
- promotions
- scanned attendance
- group sales
- merch sales
- concession sales
- sponsorship activations
- fan engagement
- CRM follow-up

When those reports stay separate, leadership may know what attendance looked like, but not whether a game created total business value.

A promotion may sell tickets, but that does not automatically mean it created strong scanned attendance, in-park spend, repeat buyers, or follow-up opportunity.

This project demonstrates what a connected reporting structure could look like.

## Main Business Question

Which games and promotions created the most total fan value beyond attendance, and which fans or accounts should sales and marketing follow up with first?

## Supporting Business Questions

1. Which promotions should return, be reworked, retired, or reviewed?
2. Which games sold tickets but underperformed on scanned attendance?
3. Which games drove strong merch and concession value?
4. Which fan segments are most valuable once ticket spend, attendance, merch, and concessions are connected?
5. Which fans are undervalued if the team only looks at ticket spend?
6. Which group accounts are highest priority for renewal or upsell?
7. Which no-show buyers are worth recovering?
8. Which homestands created the strongest total value?
9. Which data sources need to be connected to answer these questions consistently?

## Primary Audience

The dashboard and reporting structure are designed for:

1. Leadership and executives
2. Sales and marketing teams
3. Promotions staff
4. Recruiters and hiring managers reviewing the portfolio project

## Project Scope

The current build focuses on 2023-2025 Trash Pandas home games only.

The project is not a full CRM replacement. It is not a real-time data pipeline. It is not a machine learning project.

It is a connected reporting proof-of-concept.

## Technology Stack

- Snowflake: cloud reporting warehouse
- Python: data cleaning and synthetic data generation
- SQL: reporting views and business logic
- Tableau Public: dashboard visualization
- CSV files: source and export format
- GitHub: project documentation and version control
- VS Code: file editing

## Snowflake Architecture

The project will use a warehouse-style structure:

- RAW: loaded source files
- STAGING: cleaned and standardized tables
- ANALYTICS: reporting views and business logic
- EXPORTS: Tableau-ready output tables

## Public Data

Public data may include:

- game dates
- season
- opponent
- home/away flag
- day of week
- promotion names
- promotion categories
- announced attendance where available

Public data will not be treated as perfect or complete.

## Synthetic Data

Synthetic data will be generated for internal-style fields such as:

- fan profiles
- fan segments
- ticket orders
- ticket scans
- no-show behavior
- group accounts
- group sales
- merch transactions
- concession transactions
- sponsorship activation context
- fan engagement
- CRM follow-up opportunities
- CRM follow-up tasks

Synthetic data will be clearly labeled and documented.

## Fan-Linked Spend Assumption

The project will model partial fan-level matching for merch and concession purchases.

Assumptions:

- 60-75% of merch transactions are linked to fan_id
- 35-55% of concession transactions are linked to fan_id
- remaining transactions are tied only to game_id

This avoids pretending every in-park purchase can be matched to a fan.

## Core Decision Outputs

The project will produce three current build dashboard outputs:

1. Homestand Intelligence Dashboard
2. Promotion Performance Scorecard
3. CRM Follow-Up Queue

## Promotion Recommendation Labels

Promotions will be classified as:

- Return
- Rework
- Retire
- Review

The recommendation will be based on total value, not attendance alone.

## Total Value Definition

Total value will include:

- ticket sales
- scanned attendance
- no-show rate
- group sales
- merch spend
- concession spend
- repeat buyer signal
- follow-up opportunity

The project will use an index-based scoring approach instead of claiming exact financial truth.

## Future Revenue Opportunity

Future revenue opportunity will be shown as an index, not as a precise revenue forecast.

The index will consider:

- repeat likelihood
- recent attendance
- ticket spend
- merch and concession behavior
- group or corporate fit
- engagement signal
- upgrade potential

## Repeat Likelihood

Repeat likelihood will be rule-based, not machine-learning based.

It will consider:

- recency
- frequency
- promo or theme affinity
- engagement behavior
- scan reliability

## No-Show Recovery Logic

The project will focus on recovering valuable no-shows, not every no-show.

A no-show buyer becomes a recovery target when they purchased a ticket, did not scan, and have prior value or premium/group behavior.

One-time buyers with no prior value will be excluded unless they bought premium or group tickets.

## Sponsorship Scope

Sponsorship will be included as business context only.

The project will not claim to calculate sponsorship ROI because that would require internal contract, fulfillment, impression, and partner objective data.

## What This Project Is Not

This project is not:

- a replacement for the team's existing systems
- a claim of internal Trash Pandas data access
- a real CRM implementation
- a real-time reporting pipeline
- a machine learning project
- an exact revenue forecast
- a sponsorship ROI model

## Portfolio Story

This project shows how a sports organization could move from scattered reports to a connected reporting layer.

The value is not just the dashboard.

The value is the structure:

public data and synthetic internal-style data are staged, cleaned, connected, modeled, and transformed into business questions that leadership and sales teams can act on.

## Project Success Criteria

The project is successful if it can clearly show:

1. Which promotions created total fan value beyond attendance
2. Which fan and account segments deserve follow-up
3. Which games had attendance, scan, spend, or follow-up gaps
4. How Snowflake can support a connected sports business reporting layer
5. How Tableau can turn that layer into executive-ready reporting
