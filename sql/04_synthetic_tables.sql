USE trash_pandas_crm;

DROP TABLE IF EXISTS synthetic_ticket_orders;
DROP TABLE IF EXISTS synthetic_fans;

CREATE TABLE synthetic_fans (
    fan_id VARCHAR(20) PRIMARY KEY,
    household_id VARCHAR(20),
    fan_segment VARCHAR(50),
    city VARCHAR(75),
    state VARCHAR(10),
    acquisition_channel VARCHAR(75),
    first_seen_date DATE,
    email_opt_in TINYINT DEFAULT 0,
    sms_opt_in TINYINT DEFAULT 0,
    favorite_promo_category VARCHAR(75),
    synthetic_model_version VARCHAR(100),

    INDEX idx_fans_segment (fan_segment),
    INDEX idx_fans_city_state (city, state)
);

CREATE TABLE synthetic_ticket_orders (
    order_id VARCHAR(25) PRIMARY KEY,
    fan_id VARCHAR(20) NOT NULL,
    game_id VARCHAR(25) NOT NULL,
    season INT NOT NULL,
    planned_game_date DATE,
    actual_game_date DATE,
    order_date DATE,
    ticket_quantity INT NOT NULL,
    ticket_type VARCHAR(50),
    sales_channel VARCHAR(75),
    estimated_ticket_revenue DECIMAL(10,2),
    is_group_order TINYINT DEFAULT 0,
    is_repeat_buyer TINYINT DEFAULT 0,
    buyer_game_number INT,
    buyer_segment_at_purchase VARCHAR(50),
    attendance_control_total INT,
    synthetic_model_version VARCHAR(100),

    INDEX idx_orders_fan_id (fan_id),
    INDEX idx_orders_game_id (game_id),
    INDEX idx_orders_season (season),
    INDEX idx_orders_segment (buyer_segment_at_purchase),
    INDEX idx_orders_ticket_type (ticket_type),

    CONSTRAINT fk_orders_fans
        FOREIGN KEY (fan_id)
        REFERENCES synthetic_fans(fan_id),

    CONSTRAINT fk_orders_games
        FOREIGN KEY (game_id)
        REFERENCES games(game_id)
);

LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/processed/synthetic_fans.csv'
INTO TABLE synthetic_fans
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    fan_id,
    household_id,
    fan_segment,
    city,
    state,
    acquisition_channel,
    @first_seen_date,
    email_opt_in,
    sms_opt_in,
    favorite_promo_category,
    synthetic_model_version
)
SET
    first_seen_date = STR_TO_DATE(@first_seen_date, '%Y-%m-%d');

LOAD DATA LOCAL INFILE '/Users/Tip/Desktop/trash-pandas-crm-analytics-pilot/data/processed/synthetic_ticket_orders.csv'
INTO TABLE synthetic_ticket_orders
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    order_id,
    fan_id,
    game_id,
    season,
    @planned_game_date,
    @actual_game_date,
    @order_date,
    ticket_quantity,
    ticket_type,
    sales_channel,
    estimated_ticket_revenue,
    is_group_order,
    is_repeat_buyer,
    buyer_game_number,
    buyer_segment_at_purchase,
    attendance_control_total,
    synthetic_model_version
)
SET
    planned_game_date = STR_TO_DATE(@planned_game_date, '%Y-%m-%d'),
    actual_game_date = STR_TO_DATE(@actual_game_date, '%Y-%m-%d'),
    order_date = STR_TO_DATE(@order_date, '%Y-%m-%d');

SELECT 'SYNTHETIC FANS TOTAL' AS check_name, COUNT(*) AS value
FROM synthetic_fans;

SELECT 'SYNTHETIC ORDERS TOTAL' AS check_name, COUNT(*) AS value
FROM synthetic_ticket_orders;

SELECT
    season,
    COUNT(*) AS orders,
    SUM(ticket_quantity) AS synthetic_tickets,
    ROUND(SUM(estimated_ticket_revenue), 2) AS estimated_ticket_revenue
FROM synthetic_ticket_orders
GROUP BY season
ORDER BY season;

SELECT
    fan_segment,
    COUNT(*) AS fans
FROM synthetic_fans
GROUP BY fan_segment
ORDER BY fans DESC;

SELECT
    buyer_segment_at_purchase,
    COUNT(*) AS orders,
    SUM(ticket_quantity) AS tickets,
    ROUND(SUM(estimated_ticket_revenue), 2) AS estimated_revenue
FROM synthetic_ticket_orders
GROUP BY buyer_segment_at_purchase
ORDER BY tickets DESC;

SELECT
    a.game_id,
    a.season,
    a.attendance AS real_attendance,
    COALESCE(SUM(o.ticket_quantity), 0) AS synthetic_ticket_quantity,
    a.attendance - COALESCE(SUM(o.ticket_quantity), 0) AS difference
FROM game_attendance_actuals a
LEFT JOIN synthetic_ticket_orders o
    ON a.game_id = o.game_id
GROUP BY
    a.game_id,
    a.season,
    a.attendance
HAVING difference <> 0
ORDER BY a.season, a.game_id;

SELECT
    'ATTENDANCE CONTROL CHECK' AS check_name,
    SUM(a.attendance) AS real_attendance,
    (
        SELECT SUM(ticket_quantity)
        FROM synthetic_ticket_orders
    ) AS synthetic_ticket_quantity,
    SUM(a.attendance) - (
        SELECT SUM(ticket_quantity)
        FROM synthetic_ticket_orders
    ) AS difference
FROM game_attendance_actuals a;