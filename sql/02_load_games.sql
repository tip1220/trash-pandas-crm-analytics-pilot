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

SELECT COUNT(*) AS total_games
FROM games;

SELECT home_away, COUNT(*) AS games
FROM games
GROUP BY home_away;

SELECT promotion_type, COUNT(*) AS games
FROM games
GROUP BY promotion_type
ORDER BY games DESC;

SELECT *
FROM games
ORDER BY game_date
LIMIT 10;