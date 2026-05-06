CREATE DATABASE IF NOT EXISTS trash_pandas_crm;

USE trash_pandas_crm;

DROP TABLE IF EXISTS promotions;
DROP TABLE IF EXISTS games;

CREATE TABLE games (
    game_id VARCHAR(25) PRIMARY KEY,
    game_date DATE NOT NULL,
    season INT NOT NULL,
    opponent_code VARCHAR(10),
    opponent VARCHAR(100) NOT NULL,
    home_away VARCHAR(10) NOT NULL,
    game_time VARCHAR(25),
    day_of_week VARCHAR(15),
    month_name VARCHAR(15),
    promotion_flag VARCHAR(5),
    promotion_type VARCHAR(50),
    source VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE promotions (
    promo_id INT AUTO_INCREMENT PRIMARY KEY,
    game_date DATE NOT NULL,
    season INT NOT NULL,
    promo_name VARCHAR(150) NOT NULL,
    promo_category VARCHAR(75),
    promo_audience VARCHAR(100),
    sponsor VARCHAR(150),
    is_fireworks TINYINT DEFAULT 0,
    is_giveaway TINYINT DEFAULT 0,
    is_theme_night TINYINT DEFAULT 0,
    is_weekly_promo TINYINT DEFAULT 0,
    is_group_sales TINYINT DEFAULT 0,
    is_community TINYINT DEFAULT 0,
    is_appearance TINYINT DEFAULT 0,
    is_jersey_auction TINYINT DEFAULT 0,
    source_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_promotions_game_date (game_date),
    INDEX idx_promotions_season (season),
    INDEX idx_promotions_category (promo_category)
);