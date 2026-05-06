USE trash_pandas_crm;

DROP VIEW IF EXISTS crm_group_sales_opportunities;
DROP VIEW IF EXISTS crm_game_performance_summary;
DROP VIEW IF EXISTS crm_fan_scoring_model;
DROP VIEW IF EXISTS crm_fan_scoring_base;
DROP VIEW IF EXISTS crm_fan_promo_summary;
DROP VIEW IF EXISTS crm_fan_order_summary;
DROP VIEW IF EXISTS crm_game_promo_summary;

CREATE VIEW crm_game_promo_summary AS
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


CREATE VIEW crm_fan_order_summary AS
SELECT
    f.fan_id,
    f.household_id,
    f.fan_segment,
    f.city,
    f.state,
    f.acquisition_channel,
    f.first_seen_date,
    f.email_opt_in,
    f.sms_opt_in,
    f.favorite_promo_category,

    COUNT(o.order_id) AS total_orders,
    COUNT(DISTINCT o.game_id) AS games_purchased,
    COUNT(DISTINCT o.season) AS active_seasons,

    MIN(o.order_date) AS first_order_date,
    MAX(o.order_date) AS last_order_date,
    MIN(o.actual_game_date) AS first_game_date,
    MAX(o.actual_game_date) AS last_game_date,

    SUM(o.ticket_quantity) AS total_tickets,
    ROUND(SUM(o.estimated_ticket_revenue), 2) AS total_revenue,
    ROUND(AVG(o.ticket_quantity), 2) AS avg_tickets_per_order,
    ROUND(AVG(o.estimated_ticket_revenue), 2) AS avg_revenue_per_order,

    SUM(CASE WHEN o.is_group_order = 1 THEN 1 ELSE 0 END) AS group_orders,
    SUM(CASE WHEN o.is_group_order = 1 THEN o.ticket_quantity ELSE 0 END) AS group_tickets,
    ROUND(SUM(CASE WHEN o.is_group_order = 1 THEN o.estimated_ticket_revenue ELSE 0 END), 2) AS group_revenue,

    SUM(CASE WHEN o.is_repeat_buyer = 1 THEN 1 ELSE 0 END) AS repeat_orders,

    CASE
        WHEN COUNT(o.order_id) >= 2 THEN 1
        ELSE 0
    END AS is_repeat_buyer,

    DATEDIFF(
        (SELECT MAX(actual_game_date) FROM synthetic_ticket_orders),
        MAX(o.actual_game_date)
    ) AS days_since_last_game,

    MAX(CASE WHEN o.season = 2023 THEN 1 ELSE 0 END) AS purchased_2023,
    MAX(CASE WHEN o.season = 2024 THEN 1 ELSE 0 END) AS purchased_2024,
    MAX(CASE WHEN o.season = 2025 THEN 1 ELSE 0 END) AS purchased_2025

FROM synthetic_fans f
LEFT JOIN synthetic_ticket_orders o
    ON f.fan_id = o.fan_id
GROUP BY
    f.fan_id,
    f.household_id,
    f.fan_segment,
    f.city,
    f.state,
    f.acquisition_channel,
    f.first_seen_date,
    f.email_opt_in,
    f.sms_opt_in,
    f.favorite_promo_category;


CREATE VIEW crm_fan_promo_summary AS
SELECT
    o.fan_id,

    SUM(CASE WHEN gps.has_fireworks = 1 THEN o.ticket_quantity ELSE 0 END) AS fireworks_tickets,
    SUM(CASE WHEN gps.has_giveaway = 1 THEN o.ticket_quantity ELSE 0 END) AS giveaway_tickets,
    SUM(CASE WHEN gps.has_theme_night = 1 THEN o.ticket_quantity ELSE 0 END) AS theme_night_tickets,
    SUM(CASE WHEN gps.has_weekly_promo = 1 THEN o.ticket_quantity ELSE 0 END) AS weekly_promo_tickets,
    SUM(CASE WHEN gps.has_group_sales = 1 THEN o.ticket_quantity ELSE 0 END) AS group_sales_promo_tickets,
    SUM(CASE WHEN gps.has_community_promo = 1 THEN o.ticket_quantity ELSE 0 END) AS community_promo_tickets,

    SUM(CASE WHEN gps.has_fireworks = 1 THEN 1 ELSE 0 END) AS fireworks_orders,
    SUM(CASE WHEN gps.has_giveaway = 1 THEN 1 ELSE 0 END) AS giveaway_orders,
    SUM(CASE WHEN gps.has_theme_night = 1 THEN 1 ELSE 0 END) AS theme_night_orders,
    SUM(CASE WHEN gps.has_weekly_promo = 1 THEN 1 ELSE 0 END) AS weekly_promo_orders,
    SUM(CASE WHEN gps.has_group_sales = 1 THEN 1 ELSE 0 END) AS group_sales_promo_orders,
    SUM(CASE WHEN gps.has_community_promo = 1 THEN 1 ELSE 0 END) AS community_promo_orders,

    CASE
        WHEN SUM(CASE WHEN gps.has_fireworks = 1 THEN o.ticket_quantity ELSE 0 END) >=
             GREATEST(
                SUM(CASE WHEN gps.has_giveaway = 1 THEN o.ticket_quantity ELSE 0 END),
                SUM(CASE WHEN gps.has_theme_night = 1 THEN o.ticket_quantity ELSE 0 END),
                SUM(CASE WHEN gps.has_group_sales = 1 THEN o.ticket_quantity ELSE 0 END),
                SUM(CASE WHEN gps.has_community_promo = 1 THEN o.ticket_quantity ELSE 0 END)
             )
        THEN 'fireworks'

        WHEN SUM(CASE WHEN gps.has_giveaway = 1 THEN o.ticket_quantity ELSE 0 END) >=
             GREATEST(
                SUM(CASE WHEN gps.has_theme_night = 1 THEN o.ticket_quantity ELSE 0 END),
                SUM(CASE WHEN gps.has_group_sales = 1 THEN o.ticket_quantity ELSE 0 END),
                SUM(CASE WHEN gps.has_community_promo = 1 THEN o.ticket_quantity ELSE 0 END)
             )
        THEN 'giveaway'

        WHEN SUM(CASE WHEN gps.has_theme_night = 1 THEN o.ticket_quantity ELSE 0 END) >=
             GREATEST(
                SUM(CASE WHEN gps.has_group_sales = 1 THEN o.ticket_quantity ELSE 0 END),
                SUM(CASE WHEN gps.has_community_promo = 1 THEN o.ticket_quantity ELSE 0 END)
             )
        THEN 'theme_night'

        WHEN SUM(CASE WHEN gps.has_group_sales = 1 THEN o.ticket_quantity ELSE 0 END) >=
             SUM(CASE WHEN gps.has_community_promo = 1 THEN o.ticket_quantity ELSE 0 END)
        THEN 'group_sales'

        ELSE 'community'
    END AS top_promo_response_category

FROM synthetic_ticket_orders o
LEFT JOIN crm_game_promo_summary gps
    ON o.game_id = gps.game_id
GROUP BY o.fan_id;


CREATE VIEW crm_fan_scoring_base AS
SELECT
    fos.fan_id,
    fos.household_id,
    fos.fan_segment,
    fos.city,
    fos.state,
    fos.acquisition_channel,
    fos.first_seen_date,
    fos.email_opt_in,
    fos.sms_opt_in,
    fos.favorite_promo_category,

    fos.total_orders,
    fos.games_purchased,
    fos.active_seasons,
    fos.first_order_date,
    fos.last_order_date,
    fos.first_game_date,
    fos.last_game_date,
    fos.total_tickets,
    fos.total_revenue,
    fos.avg_tickets_per_order,
    fos.avg_revenue_per_order,
    fos.group_orders,
    fos.group_tickets,
    fos.group_revenue,
    fos.repeat_orders,
    fos.is_repeat_buyer,
    fos.days_since_last_game,
    fos.purchased_2023,
    fos.purchased_2024,
    fos.purchased_2025,

    COALESCE(fps.fireworks_tickets, 0) AS fireworks_tickets,
    COALESCE(fps.giveaway_tickets, 0) AS giveaway_tickets,
    COALESCE(fps.theme_night_tickets, 0) AS theme_night_tickets,
    COALESCE(fps.weekly_promo_tickets, 0) AS weekly_promo_tickets,
    COALESCE(fps.group_sales_promo_tickets, 0) AS group_sales_promo_tickets,
    COALESCE(fps.community_promo_tickets, 0) AS community_promo_tickets,
    COALESCE(fps.top_promo_response_category, 'none') AS top_promo_response_category

FROM crm_fan_order_summary fos
LEFT JOIN crm_fan_promo_summary fps
    ON fos.fan_id = fps.fan_id;


CREATE VIEW crm_fan_scoring_model AS
SELECT
    fan_id,
    household_id,
    fan_segment,
    city,
    state,
    acquisition_channel,
    first_seen_date,
    email_opt_in,
    sms_opt_in,
    favorite_promo_category,

    total_orders,
    games_purchased,
    active_seasons,
    first_order_date,
    last_order_date,
    first_game_date,
    last_game_date,
    total_tickets,
    total_revenue,
    avg_tickets_per_order,
    avg_revenue_per_order,
    group_orders,
    group_tickets,
    group_revenue,
    is_repeat_buyer,
    days_since_last_game,
    purchased_2023,
    purchased_2024,
    purchased_2025,

    fireworks_tickets,
    giveaway_tickets,
    theme_night_tickets,
    weekly_promo_tickets,
    group_sales_promo_tickets,
    community_promo_tickets,
    top_promo_response_category,

    LEAST(
        100,
        ROUND(
            (LEAST(total_revenue, 1500) / 1500 * 40) +
            (LEAST(total_tickets, 100) / 100 * 25) +
            (LEAST(total_orders, 12) / 12 * 20) +
            (active_seasons / 3 * 15)
        )
    ) AS fan_value_score,

    LEAST(
        100,
        ROUND(
            (CASE WHEN is_repeat_buyer = 1 THEN 30 ELSE 0 END) +
            (LEAST(total_orders, 10) / 10 * 30) +
            (LEAST(active_seasons, 3) / 3 * 20) +
            (CASE
                WHEN days_since_last_game <= 45 THEN 20
                WHEN days_since_last_game <= 90 THEN 15
                WHEN days_since_last_game <= 180 THEN 10
                ELSE 0
            END)
        )
    ) AS repeat_likelihood_score,

    LEAST(
        100,
        ROUND(
            (CASE
                WHEN days_since_last_game <= 45 THEN 10
                WHEN days_since_last_game <= 90 THEN 25
                WHEN days_since_last_game <= 180 THEN 45
                WHEN days_since_last_game <= 365 THEN 65
                ELSE 85
            END) +
            (CASE WHEN purchased_2025 = 0 THEN 10 ELSE 0 END) +
            (CASE WHEN total_orders = 1 THEN 5 ELSE 0 END)
        )
    ) AS lapsed_risk_score,

    LEAST(
        100,
        ROUND(
            (CASE WHEN group_orders > 0 THEN 40 ELSE 0 END) +
            (LEAST(group_tickets, 150) / 150 * 30) +
            (CASE WHEN fan_segment IN ('group_buyer', 'corporate_group') THEN 20 ELSE 0 END) +
            (CASE WHEN group_sales_promo_tickets > 0 THEN 10 ELSE 0 END)
        )
    ) AS group_sales_score,

    LEAST(
        100,
        ROUND(
            (CASE
                WHEN fan_segment IN ('family_buyer', 'promo_chaser', 'mini_plan_buyer') THEN 20
                ELSE 5
            END) +
            (CASE WHEN is_repeat_buyer = 1 THEN 25 ELSE 0 END) +
            (LEAST(total_tickets, 50) / 50 * 25) +
            (LEAST(total_revenue, 750) / 750 * 20) +
            (CASE WHEN email_opt_in = 1 THEN 10 ELSE 0 END)
        )
    ) AS upgrade_potential_score,

    CASE
        WHEN group_orders > 0 OR fan_segment IN ('group_buyer', 'corporate_group')
            THEN 'Group Sales Follow-Up'

        WHEN purchased_2025 = 0 AND total_revenue >= 250
            THEN 'Win-Back Campaign'

        WHEN fan_segment IN ('family_buyer', 'promo_chaser', 'mini_plan_buyer')
             AND is_repeat_buyer = 1
             AND email_opt_in = 1
            THEN 'Mini Plan / Upgrade Offer'

        WHEN top_promo_response_category IN ('fireworks', 'giveaway', 'theme_night')
            THEN 'Promo-Based Email Targeting'

        WHEN total_orders = 1
            THEN 'Second Purchase Nurture'

        ELSE 'General Nurture'
    END AS recommended_crm_action

FROM crm_fan_scoring_base;


CREATE VIEW crm_game_performance_summary AS
SELECT
    a.game_id,
    a.season,
    a.planned_game_date,
    a.actual_game_date,
    g.opponent,
    g.day_of_week,
    g.game_time,

    a.attendance AS real_attendance,

    COUNT(o.order_id) AS synthetic_orders,
    COUNT(DISTINCT o.fan_id) AS unique_buyers,
    SUM(o.ticket_quantity) AS synthetic_tickets,
    ROUND(SUM(o.estimated_ticket_revenue), 2) AS estimated_ticket_revenue,
    ROUND(SUM(o.ticket_quantity) / COUNT(o.order_id), 2) AS avg_tickets_per_order,

    SUM(CASE WHEN o.is_group_order = 1 THEN o.ticket_quantity ELSE 0 END) AS group_tickets,
    SUM(CASE WHEN o.is_repeat_buyer = 1 THEN o.ticket_quantity ELSE 0 END) AS repeat_buyer_tickets,

    gps.promo_record_count,
    gps.has_promotion,
    gps.has_fireworks,
    gps.has_giveaway,
    gps.has_theme_night,
    gps.has_weekly_promo,
    gps.has_group_sales,
    gps.has_community_promo,
    gps.has_appearance,
    gps.has_jersey_auction,
    gps.promo_categories,
    gps.promo_names,

    a.zero_attendance_flag,
    a.is_doubleheader_date,
    a.date_match_flag

FROM game_attendance_actuals a
LEFT JOIN games g
    ON a.game_id = g.game_id
LEFT JOIN synthetic_ticket_orders o
    ON a.game_id = o.game_id
LEFT JOIN crm_game_promo_summary gps
    ON a.game_id = gps.game_id
GROUP BY
    a.game_id,
    a.season,
    a.planned_game_date,
    a.actual_game_date,
    g.opponent,
    g.day_of_week,
    g.game_time,
    a.attendance,
    gps.promo_record_count,
    gps.has_promotion,
    gps.has_fireworks,
    gps.has_giveaway,
    gps.has_theme_night,
    gps.has_weekly_promo,
    gps.has_group_sales,
    gps.has_community_promo,
    gps.has_appearance,
    gps.has_jersey_auction,
    gps.promo_categories,
    gps.promo_names,
    a.zero_attendance_flag,
    a.is_doubleheader_date,
    a.date_match_flag;


CREATE VIEW crm_group_sales_opportunities AS
SELECT
    fan_id,
    household_id,
    fan_segment,
    city,
    state,
    acquisition_channel,
    total_orders,
    total_tickets,
    total_revenue,
    group_orders,
    group_tickets,
    group_revenue,
    avg_tickets_per_order,
    group_sales_score,
    upgrade_potential_score,
    days_since_last_game,
    email_opt_in,
    sms_opt_in,
    recommended_crm_action
FROM crm_fan_scoring_model
WHERE group_sales_score >= 60
   OR fan_segment IN ('group_buyer', 'corporate_group')
   OR avg_tickets_per_order >= 10
ORDER BY group_sales_score DESC, total_revenue DESC;


SELECT 'FAN SCORING ROWS' AS check_name, COUNT(*) AS value
FROM crm_fan_scoring_model;

SELECT recommended_crm_action, COUNT(*) AS fans
FROM crm_fan_scoring_model
GROUP BY recommended_crm_action
ORDER BY fans DESC;

SELECT
    fan_segment,
    COUNT(*) AS fans,
    ROUND(AVG(fan_value_score), 1) AS avg_value_score,
    ROUND(AVG(repeat_likelihood_score), 1) AS avg_repeat_score,
    ROUND(AVG(lapsed_risk_score), 1) AS avg_lapsed_risk_score,
    ROUND(AVG(group_sales_score), 1) AS avg_group_sales_score,
    ROUND(AVG(upgrade_potential_score), 1) AS avg_upgrade_score
FROM crm_fan_scoring_model
GROUP BY fan_segment
ORDER BY avg_value_score DESC;

SELECT
    'GAME ATTENDANCE CONTROL CHECK' AS check_name,
    SUM(real_attendance) AS real_attendance,
    SUM(synthetic_tickets) AS synthetic_tickets,
    SUM(real_attendance) - SUM(synthetic_tickets) AS difference
FROM crm_game_performance_summary;

SELECT
    season,
    COUNT(*) AS home_games,
    SUM(real_attendance) AS attendance,
    ROUND(SUM(estimated_ticket_revenue), 2) AS estimated_ticket_revenue,
    ROUND(AVG(real_attendance), 0) AS avg_attendance
FROM crm_game_performance_summary
GROUP BY season
ORDER BY season;

SELECT
    COUNT(*) AS group_sales_opportunity_fans
FROM crm_group_sales_opportunities;