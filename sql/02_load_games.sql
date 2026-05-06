USE trash_pandas_crm;

LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/raw/schedule_2023.csv'
INTO TABLE games
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    game_id,
    @game_date,
    season,
    opponent_code,
    opponent,
    home_away,
    @game_time,
    day_of_week,
    month_name,
    promotion_flag,
    @promotion_type,
    source
)
SET
    game_date = STR_TO_DATE(@game_date, '%Y-%m-%d'),
    game_time = NULLIF(@game_time, ''),
    promotion_type = NULLIF(@promotion_type, '');

LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/raw/schedule_2024.csv'
INTO TABLE games
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    game_id,
    @game_date,
    season,
    opponent_code,
    opponent,
    home_away,
    @game_time,
    day_of_week,
    month_name,
    promotion_flag,
    @promotion_type,
    source
)
SET
    game_date = STR_TO_DATE(@game_date, '%Y-%m-%d'),
    game_time = NULLIF(@game_time, ''),
    promotion_type = NULLIF(@promotion_type, '');

LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/raw/schedule_2025.csv'
INTO TABLE games
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    game_id,
    @game_date,
    season,
    opponent_code,
    opponent,
    home_away,
    @game_time,
    day_of_week,
    month_name,
    promotion_flag,
    @promotion_type,
    source
)
SET
    game_date = STR_TO_DATE(@game_date, '%Y-%m-%d'),
    game_time = NULLIF(@game_time, ''),
    promotion_type = NULLIF(@promotion_type, '');

LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/raw/promotions_2023.csv'
INTO TABLE promotions
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    @game_date,
    season,
    promo_name,
    promo_category,
    promo_audience,
    sponsor,
    is_fireworks,
    is_giveaway,
    is_theme_night,
    is_weekly_promo,
    is_group_sales,
    is_community,
    is_appearance,
    is_jersey_auction,
    source_name
)
SET
    game_date = STR_TO_DATE(@game_date, '%Y-%m-%d');

LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/raw/promotions_2024.csv'
INTO TABLE promotions
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    @game_date,
    season,
    promo_name,
    promo_category,
    promo_audience,
    sponsor,
    is_fireworks,
    is_giveaway,
    is_theme_night,
    is_weekly_promo,
    is_group_sales,
    is_community,
    is_appearance,
    is_jersey_auction,
    source_name
)
SET
    game_date = STR_TO_DATE(@game_date, '%Y-%m-%d');

LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/raw/promotions_2025.csv'
INTO TABLE promotions
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    @game_date,
    season,
    promo_name,
    promo_category,
    promo_audience,
    sponsor,
    is_fireworks,
    is_giveaway,
    is_theme_night,
    is_weekly_promo,
    is_group_sales,
    is_community,
    is_appearance,
    is_jersey_auction,
    source_name
)
SET
    game_date = STR_TO_DATE(@game_date, '%Y-%m-%d');

SELECT 'GAMES TOTAL' AS check_name, COUNT(*) AS value
FROM games;

SELECT season, COUNT(*) AS games
FROM games
GROUP BY season
ORDER BY season;

SELECT home_away, COUNT(*) AS games
FROM games
GROUP BY home_away;

SELECT 'PROMOTIONS TOTAL' AS check_name, COUNT(*) AS value
FROM promotions;

SELECT season, COUNT(*) AS promo_records
FROM promotions
GROUP BY season
ORDER BY season;

SELECT season, COUNT(DISTINCT game_date) AS promo_dates
FROM promotions
GROUP BY season
ORDER BY season;

SELECT promo_category, COUNT(*) AS promo_records
FROM promotions
GROUP BY promo_category
ORDER BY promo_records DESC;

SELECT
    p.season,
    p.game_date,
    COUNT(*) AS promo_records
FROM promotions p
LEFT JOIN games g
    ON p.game_date = g.game_date
    AND p.season = g.season
    AND g.home_away = 'Home'
WHERE g.game_id IS NULL
GROUP BY p.season, p.game_date
ORDER BY p.season, p.game_date;
LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/processed/game_attendance_reconciled_2023_2025.csv'
INTO TABLE game_attendance_actuals
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    game_id,
    season,
    @planned_game_date,
    @actual_game_date,
    opponent_code,
    opponent,
    planned_game_time,
    planned_day_of_week,
    planned_month_name,
    result,
    score,
    attendance,
    time_of_game,
    team_record_after_game,
    ballpark,
    location,
    is_doubleheader_date,
    attendance_rows_on_actual_date,
    zero_attendance_flag,
    date_match_flag,
    match_method,
    attendance_source_name
)
SET
    planned_game_date = STR_TO_DATE(@planned_game_date, '%Y-%m-%d'),
    actual_game_date = STR_TO_DATE(@actual_game_date, '%Y-%m-%d');

SELECT 'ATTENDANCE TOTAL' AS check_name, COUNT(*) AS value
FROM game_attendance_actuals;

SELECT
    season,
    COUNT(*) AS home_games,
    SUM(attendance) AS total_attendance,
    SUM(zero_attendance_flag) AS zero_attendance_games,
    SUM(is_doubleheader_date) AS doubleheader_rows,
    SUM(CASE WHEN date_match_flag = 0 THEN 1 ELSE 0 END) AS planned_vs_actual_date_mismatches
FROM game_attendance_actuals
GROUP BY season
ORDER BY season;

SELECT
    a.game_id,
    a.season,
    a.planned_game_date,
    a.actual_game_date,
    a.attendance
FROM game_attendance_actuals a
LEFT JOIN games g
    ON a.game_id = g.game_id
WHERE g.game_id IS NULL;
