USE trash_pandas_crm;

DROP VIEW IF EXISTS home_game_features;
DROP VIEW IF EXISTS game_features;
DROP VIEW IF EXISTS game_promo_summary;

CREATE VIEW game_promo_summary AS
SELECT
    g.game_id,
    g.game_date,
    g.season,

    COUNT(p.promo_id) AS promo_record_count,

    CASE
        WHEN COUNT(p.promo_id) > 0 THEN 1
        ELSE 0
    END AS has_promotion,

    MAX(COALESCE(p.is_fireworks, 0)) AS has_fireworks,
    MAX(COALESCE(p.is_giveaway, 0)) AS has_giveaway,
    MAX(COALESCE(p.is_theme_night, 0)) AS has_theme_night,
    MAX(COALESCE(p.is_weekly_promo, 0)) AS has_weekly_promo,
    MAX(COALESCE(p.is_group_sales, 0)) AS has_group_sales,
    MAX(COALESCE(p.is_community, 0)) AS has_community_promo,
    MAX(COALESCE(p.is_appearance, 0)) AS has_appearance,
    MAX(COALESCE(p.is_jersey_auction, 0)) AS has_jersey_auction,

    GROUP_CONCAT(DISTINCT p.promo_category ORDER BY p.promo_category SEPARATOR ' | ') AS promo_categories,
    GROUP_CONCAT(DISTINCT p.promo_name ORDER BY p.promo_name SEPARATOR ' | ') AS promo_names

FROM games g
LEFT JOIN promotions p
    ON g.game_date = p.game_date
    AND g.season = p.season
    AND g.home_away = 'Home'
GROUP BY
    g.game_id,
    g.game_date,
    g.season;


CREATE VIEW game_features AS
SELECT
    g.game_id,
    g.game_date,
    g.season,
    g.opponent_code,
    g.opponent,
    g.home_away,
    g.game_time,
    g.day_of_week,
    g.month_name,
    g.source,

    CASE
        WHEN g.home_away = 'Home' THEN 1
        ELSE 0
    END AS is_home_game,

    CASE
        WHEN g.home_away = 'Away' THEN 1
        ELSE 0
    END AS is_away_game,

    CASE
        WHEN g.day_of_week IN ('Friday', 'Saturday', 'Sunday') THEN 1
        ELSE 0
    END AS is_weekend_game,

    CASE
        WHEN g.day_of_week IN ('Tuesday', 'Wednesday', 'Thursday') THEN 1
        ELSE 0
    END AS is_weekday_game,

    CASE
        WHEN g.game_time IS NULL OR g.game_time = '' THEN 'Away / Unknown'
        WHEN g.game_time LIKE '11:%' THEN 'Education / Morning Game'
        WHEN g.game_time LIKE '1:%' THEN 'Early Afternoon Game'
        WHEN g.game_time LIKE '2:%' THEN 'Afternoon Game'
        WHEN g.game_time LIKE '4:%' THEN 'Late Afternoon Game'
        WHEN g.game_time LIKE '6:%' THEN 'Evening Game'
        ELSE 'Other'
    END AS game_time_bucket,

    CASE
        WHEN MONTH(g.game_date) IN (4, 5) THEN 'Early Season'
        WHEN MONTH(g.game_date) IN (6, 7) THEN 'Mid Season'
        WHEN MONTH(g.game_date) IN (8, 9) THEN 'Late Season'
        ELSE 'Other'
    END AS season_phase,

    MONTH(g.game_date) AS game_month_number,
    DAYOFWEEK(g.game_date) AS day_of_week_number,
    DAYNAME(g.game_date) AS date_day_name,

    COALESCE(ps.promo_record_count, 0) AS promo_record_count,
    COALESCE(ps.has_promotion, 0) AS has_promotion,
    COALESCE(ps.has_fireworks, 0) AS has_fireworks,
    COALESCE(ps.has_giveaway, 0) AS has_giveaway,
    COALESCE(ps.has_theme_night, 0) AS has_theme_night,
    COALESCE(ps.has_weekly_promo, 0) AS has_weekly_promo,
    COALESCE(ps.has_group_sales, 0) AS has_group_sales,
    COALESCE(ps.has_community_promo, 0) AS has_community_promo,
    COALESCE(ps.has_appearance, 0) AS has_appearance,
    COALESCE(ps.has_jersey_auction, 0) AS has_jersey_auction,

    ps.promo_categories,
    ps.promo_names

FROM games g
LEFT JOIN game_promo_summary ps
    ON g.game_id = ps.game_id;


CREATE VIEW home_game_features AS
SELECT *
FROM game_features
WHERE is_home_game = 1;


SELECT 'GAME FEATURES TOTAL' AS check_name, COUNT(*) AS value
FROM game_features;

SELECT season, COUNT(*) AS games
FROM game_features
GROUP BY season
ORDER BY season;

SELECT home_away, COUNT(*) AS games
FROM game_features
GROUP BY home_away;

SELECT 'HOME GAME FEATURES TOTAL' AS check_name, COUNT(*) AS value
FROM home_game_features;

SELECT season, COUNT(*) AS home_games
FROM home_game_features
GROUP BY season
ORDER BY season;

SELECT
    season,
    SUM(has_promotion) AS home_games_with_promos,
    SUM(promo_record_count) AS promo_records,
    SUM(has_fireworks) AS fireworks_games,
    SUM(has_giveaway) AS giveaway_games,
    SUM(has_theme_night) AS theme_night_games,
    SUM(has_group_sales) AS group_sales_games,
    SUM(has_community_promo) AS community_promo_games,
    SUM(has_appearance) AS appearance_games,
    SUM(has_jersey_auction) AS jersey_auction_games
FROM home_game_features
GROUP BY season
ORDER BY season;

SELECT
    season_phase,
    COUNT(*) AS games
FROM game_features
GROUP BY season_phase
ORDER BY
    CASE season_phase
        WHEN 'Early Season' THEN 1
        WHEN 'Mid Season' THEN 2
        WHEN 'Late Season' THEN 3
        ELSE 4
    END;

SELECT
    season,
    game_date,
    opponent,
    game_time,
    promo_record_count,
    has_fireworks,
    has_giveaway,
    has_theme_night,
    promo_categories,
    promo_names
FROM home_game_features
ORDER BY game_date
LIMIT 15;