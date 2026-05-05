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