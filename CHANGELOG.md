## 2026-05-06

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