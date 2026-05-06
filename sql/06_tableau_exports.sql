USE trash_pandas_crm;

DROP VIEW IF EXISTS tableau_crm_action_summary_export;
DROP VIEW IF EXISTS tableau_season_summary_export;
DROP VIEW IF EXISTS tableau_promo_performance_export;
DROP VIEW IF EXISTS tableau_group_sales_opportunities_export;
DROP VIEW IF EXISTS tableau_game_performance_export;
DROP VIEW IF EXISTS tableau_fan_scoring_export;

CREATE VIEW tableau_fan_scoring_export AS
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

    fan_value_score,
    repeat_likelihood_score,
    lapsed_risk_score,
    group_sales_score,
    upgrade_potential_score,
    recommended_crm_action,

    CASE
        WHEN fan_value_score >= 75 THEN 'High Value'
        WHEN fan_value_score >= 40 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS fan_value_tier,

    CASE
        WHEN repeat_likelihood_score >= 75 THEN 'High Repeat Likelihood'
        WHEN repeat_likelihood_score >= 40 THEN 'Medium Repeat Likelihood'
        ELSE 'Low Repeat Likelihood'
    END AS repeat_likelihood_tier,

    CASE
        WHEN lapsed_risk_score >= 75 THEN 'High Lapse Risk'
        WHEN lapsed_risk_score >= 45 THEN 'Medium Lapse Risk'
        ELSE 'Low Lapse Risk'
    END AS lapsed_risk_tier,

    CASE
        WHEN group_sales_score >= 80 THEN 'Priority Group Lead'
        WHEN group_sales_score >= 60 THEN 'Group Sales Watchlist'
        ELSE 'Lower Group Sales Fit'
    END AS group_sales_tier,

    CASE
        WHEN upgrade_potential_score >= 75 THEN 'High Upgrade Potential'
        WHEN upgrade_potential_score >= 45 THEN 'Medium Upgrade Potential'
        ELSE 'Low Upgrade Potential'
    END AS upgrade_potential_tier,

    CASE
        WHEN group_sales_score >= 80 THEN 'Priority 1'
        WHEN lapsed_risk_score >= 75 AND fan_value_score >= 40 THEN 'Priority 2'
        WHEN upgrade_potential_score >= 70 THEN 'Priority 3'
        WHEN repeat_likelihood_score >= 70 THEN 'Priority 4'
        ELSE 'Nurture'
    END AS crm_priority_tier

FROM crm_fan_scoring_model;


CREATE VIEW tableau_game_performance_export AS
SELECT
    game_id,
    season,
    planned_game_date,
    actual_game_date,
    opponent,
    day_of_week,
    game_time,

    real_attendance,
    synthetic_orders,
    unique_buyers,
    synthetic_tickets,
    estimated_ticket_revenue,
    avg_tickets_per_order,

    group_tickets,
    repeat_buyer_tickets,

    ROUND(group_tickets / NULLIF(synthetic_tickets, 0), 4) AS group_ticket_share,
    ROUND(repeat_buyer_tickets / NULLIF(synthetic_tickets, 0), 4) AS repeat_buyer_ticket_share,
    ROUND(estimated_ticket_revenue / NULLIF(real_attendance, 0), 2) AS estimated_revenue_per_attendee,

    promo_record_count,
    has_promotion,
    has_fireworks,
    has_giveaway,
    has_theme_night,
    has_weekly_promo,
    has_group_sales,
    has_community_promo,
    has_appearance,
    has_jersey_auction,
    promo_categories,
    promo_names,

    zero_attendance_flag,
    is_doubleheader_date,
    date_match_flag,

    CASE
        WHEN day_of_week IN ('Friday', 'Saturday', 'Sunday') THEN 1
        ELSE 0
    END AS is_weekend_game,

    CASE
        WHEN real_attendance >= 5500 THEN 'High Attendance'
        WHEN real_attendance >= 4000 THEN 'Mid Attendance'
        WHEN real_attendance > 0 THEN 'Low Attendance'
        ELSE 'Zero Attendance / Doubleheader Gate'
    END AS attendance_tier,

    CASE
        WHEN has_fireworks = 1 THEN 'Fireworks'
        WHEN has_giveaway = 1 THEN 'Giveaway'
        WHEN has_theme_night = 1 THEN 'Theme Night'
        WHEN has_group_sales = 1 THEN 'Group Sales'
        WHEN has_community_promo = 1 THEN 'Community'
        WHEN has_promotion = 1 THEN 'Other Promo'
        ELSE 'No Promo'
    END AS primary_promo_type

FROM crm_game_performance_summary;


CREATE VIEW tableau_group_sales_opportunities_export AS
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
    recommended_crm_action,

    CASE
        WHEN group_sales_score >= 85 OR total_revenue >= 1000 THEN 'Priority 1: Rep Follow-Up'
        WHEN group_sales_score >= 70 OR avg_tickets_per_order >= 20 THEN 'Priority 2: Group Package Offer'
        ELSE 'Priority 3: Nurture'
    END AS group_sales_priority,

    CASE
        WHEN email_opt_in = 1 THEN 'Email'
        WHEN sms_opt_in = 1 THEN 'SMS'
        ELSE 'Rep Call / Manual Research'
    END AS recommended_contact_channel

FROM crm_group_sales_opportunities;


CREATE VIEW tableau_promo_performance_export AS
SELECT
    pgc.season,
    pgc.promo_category,

    COUNT(DISTINCT pgc.game_id) AS home_games,
    SUM(gps.real_attendance) AS total_attendance,
    ROUND(AVG(gps.real_attendance), 0) AS avg_attendance,

    SUM(gps.synthetic_orders) AS synthetic_orders,
    SUM(gps.unique_buyers) AS unique_buyers,
    SUM(gps.synthetic_tickets) AS synthetic_tickets,
    ROUND(SUM(gps.estimated_ticket_revenue), 2) AS estimated_ticket_revenue,

    SUM(gps.group_tickets) AS group_tickets,
    SUM(gps.repeat_buyer_tickets) AS repeat_buyer_tickets,

    ROUND(SUM(gps.group_tickets) / NULLIF(SUM(gps.synthetic_tickets), 0), 4) AS group_ticket_share,
    ROUND(SUM(gps.repeat_buyer_tickets) / NULLIF(SUM(gps.synthetic_tickets), 0), 4) AS repeat_buyer_ticket_share,
    ROUND(SUM(gps.estimated_ticket_revenue) / NULLIF(SUM(gps.real_attendance), 0), 2) AS estimated_revenue_per_attendee

FROM (
    SELECT DISTINCT
        g.game_id,
        g.season,
        p.promo_category
    FROM games g
    INNER JOIN promotions p
        ON g.game_date = p.game_date
        AND g.season = p.season
        AND g.home_away = 'Home'
) pgc
INNER JOIN crm_game_performance_summary gps
    ON pgc.game_id = gps.game_id
GROUP BY
    pgc.season,
    pgc.promo_category;


CREATE VIEW tableau_season_summary_export AS
SELECT
    gps.season,
    COUNT(*) AS home_games,
    SUM(gps.real_attendance) AS total_attendance,
    ROUND(AVG(gps.real_attendance), 0) AS avg_attendance,
    MIN(gps.real_attendance) AS min_attendance,
    MAX(gps.real_attendance) AS max_attendance,

    SUM(gps.synthetic_orders) AS synthetic_orders,
    SUM(gps.unique_buyers) AS unique_buyers,
    SUM(gps.synthetic_tickets) AS synthetic_tickets,
    ROUND(SUM(gps.estimated_ticket_revenue), 2) AS estimated_ticket_revenue,

    SUM(gps.group_tickets) AS group_tickets,
    SUM(gps.repeat_buyer_tickets) AS repeat_buyer_tickets,

    ROUND(SUM(gps.group_tickets) / NULLIF(SUM(gps.synthetic_tickets), 0), 4) AS group_ticket_share,
    ROUND(SUM(gps.repeat_buyer_tickets) / NULLIF(SUM(gps.synthetic_tickets), 0), 4) AS repeat_buyer_ticket_share,

    SUM(CASE WHEN gps.has_promotion = 1 THEN 1 ELSE 0 END) AS promo_games,
    SUM(CASE WHEN gps.has_fireworks = 1 THEN 1 ELSE 0 END) AS fireworks_games,
    SUM(CASE WHEN gps.has_giveaway = 1 THEN 1 ELSE 0 END) AS giveaway_games,
    SUM(CASE WHEN gps.has_theme_night = 1 THEN 1 ELSE 0 END) AS theme_night_games,
    SUM(CASE WHEN gps.has_group_sales = 1 THEN 1 ELSE 0 END) AS group_sales_games,

    ROUND(SUM(gps.estimated_ticket_revenue) / NULLIF(SUM(gps.real_attendance), 0), 2) AS estimated_revenue_per_attendee

FROM crm_game_performance_summary gps
GROUP BY gps.season;


CREATE VIEW tableau_crm_action_summary_export AS
SELECT
    recommended_crm_action,
    fan_segment,

    COUNT(*) AS fans,
    SUM(total_tickets) AS total_tickets,
    ROUND(SUM(total_revenue), 2) AS total_revenue,
    ROUND(AVG(total_orders), 2) AS avg_orders,
    ROUND(AVG(total_tickets), 2) AS avg_tickets,
    ROUND(AVG(total_revenue), 2) AS avg_revenue,

    ROUND(AVG(fan_value_score), 1) AS avg_fan_value_score,
    ROUND(AVG(repeat_likelihood_score), 1) AS avg_repeat_likelihood_score,
    ROUND(AVG(lapsed_risk_score), 1) AS avg_lapsed_risk_score,
    ROUND(AVG(group_sales_score), 1) AS avg_group_sales_score,
    ROUND(AVG(upgrade_potential_score), 1) AS avg_upgrade_potential_score,

    SUM(CASE WHEN email_opt_in = 1 THEN 1 ELSE 0 END) AS email_opt_in_fans,
    SUM(CASE WHEN sms_opt_in = 1 THEN 1 ELSE 0 END) AS sms_opt_in_fans

FROM crm_fan_scoring_model
GROUP BY
    recommended_crm_action,
    fan_segment;


SELECT 'FAN EXPORT ROWS' AS check_name, COUNT(*) AS value
FROM tableau_fan_scoring_export;

SELECT 'GAME EXPORT ROWS' AS check_name, COUNT(*) AS value
FROM tableau_game_performance_export;

SELECT 'GROUP SALES EXPORT ROWS' AS check_name, COUNT(*) AS value
FROM tableau_group_sales_opportunities_export;

SELECT 'PROMO PERFORMANCE EXPORT ROWS' AS check_name, COUNT(*) AS value
FROM tableau_promo_performance_export;

SELECT 'SEASON SUMMARY EXPORT ROWS' AS check_name, COUNT(*) AS value
FROM tableau_season_summary_export;

SELECT 'CRM ACTION SUMMARY EXPORT ROWS' AS check_name, COUNT(*) AS value
FROM tableau_crm_action_summary_export;

SELECT
    'TABLEAU ATTENDANCE CONTROL CHECK' AS check_name,
    SUM(real_attendance) AS real_attendance,
    SUM(synthetic_tickets) AS synthetic_tickets,
    SUM(real_attendance) - SUM(synthetic_tickets) AS difference
FROM tableau_game_performance_export;