## Current Status

### Phase 1: Raw Schedule, Promotion, and Attendance Data

Status: Complete

Completed:
- Created raw schedule files for 2023, 2024, and 2025.
- Created public promotion record files for 2023, 2024, and 2025.
- Standardized schedule headers to align with the database schema.
- Normalized promotion categories across all promo files.
- Created MySQL `games` table.
- Created MySQL `promotions` table.
- Loaded all three schedule files into MySQL.
- Loaded all three promotion files into MySQL.
- Validated 414 total games.
- Validated 207 home games and 207 away games.
- Validated 491 promotion records.
- Collected public attendance actuals.
- Reconciled actual attendance back to planned schedule game IDs.
- Created MySQL `game_attendance_actuals` table.
- Loaded reconciled attendance actuals into MySQL.
- Validated 207 home attendance records.
- Validated 897,996 total home attendance across 2023–2025.

### Phase 2: Synthetic CRM Layer

Status: Complete

Completed:
- Created attendance-calibrated synthetic fan records.
- Created attendance-calibrated synthetic ticket order records.
- Created MySQL `synthetic_fans` table.
- Created MySQL `synthetic_ticket_orders` table.
- Loaded synthetic CRM records into MySQL.
- Validated 47,588 synthetic fans.
- Validated 93,011 synthetic ticket orders.
- Validated synthetic ticket quantity equals real attendance:
  - Real attendance: 897,996
  - Synthetic ticket quantity: 897,996
  - Difference: 0

### Phase 3: CRM Scoring Model

Status: Complete

Completed:
- Created `sql/05_scoring_models.sql`.
- Built game-level promo summary view.
- Built fan-level order summary view.
- Built fan-level promo response summary view.
- Built fan scoring base view.
- Built final fan scoring model view.
- Built game performance summary view.
- Built group sales opportunities view.
- Created rule-based scores for:
  - fan value
  - repeat likelihood
  - lapsed risk
  - group sales opportunity
  - upgrade potential
- Created recommended CRM actions for:
  - promo-based email targeting
  - mini plan / upgrade offers
  - group sales follow-up
  - second purchase nurture
  - win-back campaigns
  - general nurture
- Validated 47,588 fan scoring rows.
- Validated 5,560 group sales opportunity fans.
- Validated attendance control still matches:
  - Real attendance: 897,996
  - Synthetic tickets: 897,996
  - Difference: 0

### Phase 4: Tableau Export Layer

Status: Complete

Completed:
- Created Tableau export views.
- Exported dashboard-ready CSV files.
- Validated CSV row counts.
- Prepared data files for Tableau Public.

### Phase 5: Tableau Dashboard Build

Status: In Progress

Completed:
- Connected Tableau Public to exported CSV files.
- Built Executive Overview dashboard page.
- Built Fan Segments + CRM Actions dashboard page.
- Built Group Sales Opportunities dashboard page.
- Built Promo Performance dashboard page.
- Created KPI cards for attendance, average attendance, synthetic fans, and group sales opportunities.
- Created fan scoring and CRM action visuals.
- Created group sales opportunity visuals and call-list style table.
- Created promo performance visuals focused on:
  - average attendance by promo category
  - average group tickets by promo type
  - promo lift vs schedule baseline
- Added a schedule-adjusted promo lift calculation to control for season and day-of-week effects.
- Recalibrated synthetic CRM group-ticket assumptions after dashboard QA.
- Refreshed Tableau export files after recalibration.

Current QA Notes:
- Keep Page 4 focused on business value, not raw game-by-game noise.
- Avoid using percentage charts where promo categories can overlap.
- Use `primary_promo_type` for game-level promo comparisons when one promo category per game is needed.
- Use schedule-adjusted lift to show which promos outperform their season/day-of-week slot.
- Clearly explain schedule baseline in tooltip:
  - baseline = average attendance for the same season and day of week
  - lift = fans above or below that baseline
  - zero-attendance doubleheader records excluded

Next:
- Finish dashboard polish.
- Clean chart titles and tooltips.
- Standardize number formatting.
- Add data note/disclaimer to Page 1.
- Publish Tableau Public workbook.
- Copy Tableau Public link.
- Update `README.md` with final business story and dashboard link.
- Prepare GitHub project summary.
- Write LinkedIn/project case study post.

Paused:
- Final README should wait until the Tableau Public dashboard link is available.