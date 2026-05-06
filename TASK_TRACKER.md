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

Next:
- Build `sql/05_scoring_models.sql`.
- Create fan-level CRM scoring views.
- Build repeat buyer signals.
- Build lapsed fan risk logic.
- Build estimated fan value logic.
- Build group sales opportunity logic.
- Build upgrade potential logic.
- Build promo responsiveness logic.
- Validate scoring model outputs before Tableau exports.

Paused:
- Tableau exports should not be created until the scoring model layer is complete.