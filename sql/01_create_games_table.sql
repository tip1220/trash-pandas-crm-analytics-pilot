CREATE DATABASE IF NOT EXISTS trash_pandas_crm;

USE trash_pandas_crm;

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
