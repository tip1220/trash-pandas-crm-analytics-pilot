## Current Status

### Phase 1: Raw Schedule and Promotion Data

Status: Complete

Completed:
- Created raw schedule files for 2023, 2024, and 2025.
- Created public promotion record files for 2023, 2024, and 2025.
- Standardized schedule headers to align with the database schema.
- Created MySQL `games` table.
- Created MySQL `promotions` table.
- Loaded all three schedule files into MySQL.
- Loaded all three promotion files into MySQL.
- Validated 414 total games.
- Validated 138 games per season.
- Validated 207 home games and 207 away games.
- Validated promotion records by season.
- Validated promotion dates against scheduled home games.

Next:
- Build `sql/03_feature_engineering.sql`.
- Create game-level feature views.
- Aggregate promotion records to the game level.
- Prepare the foundation for synthetic CRM tables.

Paused:
- Synthetic CRM tables should not be built until the feature layer is complete.