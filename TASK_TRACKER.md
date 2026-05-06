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

Next:
- Build Tableau Public dashboard.
- Create dashboard pages:
  - Executive Overview
  - Fan Segments and CRM Actions
  - Group Sales Opportunities
  - Promo and Game Performance
- Write README business story.
- Create final project summary for GitHub and outreach.