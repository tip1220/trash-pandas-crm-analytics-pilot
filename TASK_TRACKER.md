## Current Status

### Phase 1: Raw Schedule and Promotion Data

Status: In Progress

Completed:
- Created raw schedule files for 2023, 2024, and 2025.
- Created public promotion record files for 2023, 2024, and 2025.
- Standardized schedule headers to align with the database schema.
- Ran QC checks across schedule and promotion files.
- Confirmed schedule files have 138 games per season.
- Confirmed each season has 69 home games and 69 away games.
- Confirmed promotion files use one row per promo record.

Next:
- Update `sql/01_schema.sql` to include the promotions table.
- Update `sql/02_load_games.sql` so it loads all three schedule files.
- Create or update the SQL load process for promotion files.
- Load all schedule and promotion data into MySQL.
- Validate expected database counts:
  - 414 total games
  - 207 home games
  - 207 away games
  - promotion dates matching scheduled home games
- Build feature views after the full raw data layer is loaded.

Paused:
- `sql/03_feature_engineering.sql` should not be finalized until all schedule and promotion tables are loaded and validated.