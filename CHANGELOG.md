## 2026-05-07

### Added
- Built Tableau Public dashboard pages:
  - Executive Overview
  - Fan Segments + CRM Actions
  - Group Sales Opportunities
  - Promo Performance
- Added Tableau-ready visuals for:
  - attendance trend by season
  - CRM action buckets
  - fan value vs lapse risk
  - segment scorecard
  - group sales priority
  - group sales account list
  - promo average attendance
  - average group tickets by promo type
  - promo lift vs schedule baseline

### Changed
- Recalibrated the synthetic CRM generator after dashboard QA showed group-ticket volume was unrealistically high.
- Reduced synthetic group/corporate ticket weighting and order-size assumptions.
- Regenerated synthetic fan and ticket-order data after recalibration.
- Reloaded synthetic CRM tables, scoring views, and Tableau export files.
- Refined Promo Performance page to focus on business value instead of raw date-level attendance.
- Replaced noisy game-date attendance chart with schedule-adjusted promo lift logic.
- Added schedule-adjusted baseline logic in Tableau:
  - baseline = average attendance for the same season and day-of-week slot
  - lift = actual attendance minus schedule baseline
  - zero-attendance doubleheader records excluded from baseline

### Validated
- Confirmed Tableau export files refreshed after CRM recalibration.
- Confirmed attendance control still balances after recalibration:
  - Real attendance: 897,996
  - Synthetic ticket quantity: 897,996
  - Difference: 0
- Confirmed promo analysis is now clearer and avoids confusing percentage/share visuals.
- Confirmed Page 4 focuses on three business questions:
  - Which promo categories draw stronger average crowds?
  - Which promo types support group-ticket demand?
  - Which promos beat their schedule slot after accounting for season and day of week?

### Notes
- Dashboard QA surfaced an unrealistic group-ticket assumption, which was corrected before finalizing the Tableau story.
- The dashboard now positions promotions as business levers, not just attendance drivers.

## 2026-05-06

### Added
- Created `sql/06_tableau_exports.sql`.
- Created Tableau-ready export views for:
  - fan scoring
  - game performance
  - group sales opportunities
  - promo performance
  - season summary
  - CRM action summary
- Created `python/export_tableau_csvs.py`.
- Exported Tableau-ready CSV files to `outputs/tableau/`.

### Validated
- Confirmed Tableau export row counts:
  - `fan_scoring_export.csv`: 47,588 rows
  - `game_performance_export.csv`: 207 rows
  - `group_sales_opportunities_export.csv`: 5,560 rows
  - `promo_performance_export.csv`: 36 rows
  - `season_summary_export.csv`: 3 rows
  - `crm_action_summary_export.csv`: 29 rows
- Confirmed dashboard data layer is ready for Tableau Public.

### Added
- Created `sql/05_scoring_models.sql`.
- Built CRM scoring views:
  - `crm_game_promo_summary`
  - `crm_fan_order_summary`
  - `crm_fan_promo_summary`
  - `crm_fan_scoring_base`
  - `crm_fan_scoring_model`
  - `crm_game_performance_summary`
  - `crm_group_sales_opportunities`
- Added rule-based CRM scoring logic for:
  - fan value
  - repeat likelihood
  - lapsed fan risk
  - group sales opportunity
  - upgrade potential
  - promo responsiveness
- Added recommended CRM action categories:
  - Promo-Based Email Targeting
  - Mini Plan / Upgrade Offer
  - Group Sales Follow-Up
  - Second Purchase Nurture
  - Win-Back Campaign
  - General Nurture

### Validated
- Confirmed `crm_fan_scoring_model` contains 47,588 fan scoring rows.
- Confirmed game-level attendance control still balances:
  - Real attendance: 897,996
  - Synthetic tickets: 897,996
  - Difference: 0
- Confirmed 5,560 group sales opportunity fans.
- Confirmed season-level attendance summary:
  - 2023: 69 home games, 314,306 attendance, 4,555 average attendance
  - 2024: 69 home games, 308,267 attendance, 4,468 average attendance
  - 2025: 69 home games, 275,423 attendance, 3,992 average attendance

### Notes
- CRM scoring is currently rule-based, not machine learning.
- The scoring layer is designed to be explainable for a CRM/ticketing team.
- Early business story: average home attendance declined from 2023 to 2025, creating a clear need for retention, win-back, upgrade, and group sales targeting.

### Added
- Collected public game-log attendance data for 2023, 2024, and 2025.
- Created `python/collect_attendance_actuals.py` to collect attendance actuals from public game logs.
- Created `data/raw/attendance_game_logs_2023_2025.csv` with full parsed game-log attendance records.
- Created `data/raw/attendance_2023_2025.csv` with home attendance records only.
- Created `python/reconcile_attendance_to_schedule.py` to map actual attendance records back to planned schedule game IDs.
- Created `data/processed/game_attendance_reconciled_2023_2025.csv`.
- Added `game_attendance_actuals` table to MySQL.
- Created `python/generate_synthetic_crm.py`.
- Created attendance-calibrated synthetic CRM files:
  - `data/processed/synthetic_fans.csv`
  - `data/processed/synthetic_ticket_orders.csv`
- Created `sql/04_synthetic_tables.sql` to load synthetic fans and ticket orders into MySQL.

### Changed
- Normalized promotion category naming across all promotion files.
- Updated `sql/01_schema.sql` to include attendance actuals.
- Updated `sql/02_load_games.sql` to load reconciled attendance data.
- Built synthetic ticket orders around real attendance control totals instead of arbitrary simulated volume.

### Validated
- Confirmed 207 home attendance records across 2023–2025.
- Confirmed attendance by season:
  - 2023: 69 home games, 314,306 attendance
  - 2024: 69 home games, 308,267 attendance
  - 2025: 69 home games, 275,423 attendance
- Confirmed synthetic CRM output:
  - 47,588 synthetic fans
  - 93,011 synthetic ticket orders
  - 897,996 synthetic tickets
- Confirmed synthetic ticket quantity matches real attendance exactly:
  - Real attendance: 897,996
  - Synthetic ticket quantity: 897,996
  - Difference: 0

### Notes
- Attendance reconciliation accounts for rainouts, makeups, doubleheaders, and actual game-log dates.
- Some reconciled games have zero attendance because public game logs assign paid gate attendance to one game of a doubleheader.
- Synthetic CRM records remain fictional, but they are calibrated to real home attendance totals.

## 2026-05-05

### Added
- Added raw multi-season schedule files for the Rocket City Trash Pandas:
  - `data/raw/schedule_2023.csv`
  - `data/raw/schedule_2024.csv`
  - `data/raw/schedule_2025.csv`
- Added public promotional records files:
  - `data/raw/promotions_2023.csv`
  - `data/raw/promotions_2024.csv`
  - `data/raw/promotions_2025.csv`
- Built promotion files as one row per promo, not one row per game, so games can support multiple promo records.

### Changed
- Standardized schedule file headers to match the MySQL schema:
  - `date` renamed to `game_date`
  - `month` renamed to `month_name`
- Paused feature engineering until all three seasons of schedule and promotion data were collected and checked.

### Quality Checks
- Ran raw file QC for:
  - required columns
  - 138 games per season
  - 69 home and 69 away games per season
  - duplicate game IDs
  - invalid promotion flag values
  - promotion dates matching schedule dates

### Notes
- Promotion data is based on public records and official promotional schedule/homestand sources.
- 2025 fireworks records may need one more spot-check later because season-level and date-level public records may not perfectly match.

### Added
- Updated MySQL schema to include a `promotions` table.
- Updated `sql/02_load_games.sql` to load all three schedule files and all three promotion files.
- Added validation checks for total games, games by season, home/away split, promotion records by season, promo dates, and promo category counts.

### Validated
- Confirmed 414 total games loaded into MySQL.
- Confirmed 138 games per season for 2023, 2024, and 2025.
- Confirmed 207 home games and 207 away games.
- Confirmed promotion records loaded for all three seasons.
- Confirmed promo dates match scheduled home games.