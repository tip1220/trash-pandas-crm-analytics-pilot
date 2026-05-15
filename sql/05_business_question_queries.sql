USE WAREHOUSE TP_REPORTING_WH;
USE DATABASE TRASH_PANDAS_CONNECTED_REPORTING;

-- 1. Which homestands created the most total value?

SELECT
    season,
    homestand_id,
    homestand_start_date,
    homestand_end_date,
    game_count,
    opponents,
    tickets_sold,
    scanned_attendance,
    scan_rate,
    no_show_rate,
    net_ticket_revenue,
    merch_net_sales,
    concession_net_sales,
    total_revenue_indicator,
    in_park_spend_per_scanned_fan,
    follow_up_opportunity_count,
    crm_follow_up_task_count,
    future_revenue_opportunity,
    homestand_total_value_index,
    recommended_focus
FROM ANALYTICS.V_HOMESTAND_SUMMARY
ORDER BY
    total_revenue_indicator DESC,
    homestand_total_value_index DESC
LIMIT 10;

-- 2. Which homestands need the most no-show recovery attention?

SELECT
    season,
    homestand_id,
    homestand_start_date,
    homestand_end_date,
    game_count,
    opponents,
    tickets_sold,
    scanned_attendance,
    no_show_ticket_quantity,
    no_show_rate,
    follow_up_opportunity_count,
    crm_follow_up_task_count,
    future_revenue_opportunity,
    recommended_focus
FROM ANALYTICS.V_HOMESTAND_SUMMARY
ORDER BY
    no_show_ticket_quantity DESC,
    no_show_rate DESC,
    follow_up_opportunity_count DESC
LIMIT 10;

-- 3. Which homestands created the strongest in-park value?

SELECT
    season,
    homestand_id,
    homestand_start_date,
    homestand_end_date,
    opponents,
    scanned_attendance,
    merch_net_sales,
    concession_net_sales,
    in_park_spend_per_scanned_fan,
    total_revenue_indicator,
    recommended_focus
FROM ANALYTICS.V_HOMESTAND_SUMMARY
WHERE scanned_attendance > 0
ORDER BY
    in_park_spend_per_scanned_fan DESC,
    total_revenue_indicator DESC
LIMIT 10;

-- 4. What is the promotion recommendation mix?

SELECT
    recommendation,
    COUNT(DISTINCT promo_id) AS promotion_count,
    ROUND(AVG(total_value_index), 2) AS avg_total_value_index,
    ROUND(AVG(scanned_attendance), 2) AS avg_scanned_attendance,
    ROUND(AVG(scan_rate), 4) AS avg_scan_rate,
    ROUND(AVG(no_show_rate), 4) AS avg_no_show_rate,
    ROUND(AVG(revenue_per_scanned_fan), 2) AS avg_revenue_per_scanned_fan,
    ROUND(AVG(in_park_spend_per_scanned_fan), 2) AS avg_in_park_spend_per_scanned_fan,
    ROUND(SUM(total_revenue_indicator), 2) AS total_revenue_indicator,
    ROUND(SUM(future_revenue_opportunity), 2) AS total_future_revenue_opportunity
FROM ANALYTICS.V_PROMOTION_SCORECARD
GROUP BY
    recommendation
ORDER BY
    promotion_count DESC;

-- 5. Which promotions should return?

SELECT
    season,
    game_date,
    opponent,
    promo_name,
    promo_category,
    promo_type,
    tickets_sold,
    scanned_attendance,
    scan_rate,
    no_show_rate,
    revenue_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    repeat_buyer_rate,
    total_value_index,
    recommendation,
    recommendation_reason
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE recommendation = 'return'
ORDER BY
    total_value_index DESC,
    revenue_per_scanned_fan DESC;

-- 6. Which promotions should be reworked?

SELECT
    season,
    game_date,
    opponent,
    promo_name,
    promo_category,
    promo_type,
    tickets_sold,
    scanned_attendance,
    scan_rate,
    no_show_rate,
    revenue_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    repeat_buyer_rate,
    total_value_index,
    recommendation,
    recommendation_reason
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE recommendation = 'rework'
ORDER BY
    total_value_index DESC,
    scanned_attendance DESC
LIMIT 25;

-- 7. Which promotions should be retired?

SELECT
    season,
    game_date,
    opponent,
    promo_name,
    promo_category,
    promo_type,
    tickets_sold,
    scanned_attendance,
    scan_rate,
    no_show_rate,
    revenue_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    repeat_buyer_rate,
    total_value_index,
    recommendation,
    recommendation_reason
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE recommendation = 'retire'
ORDER BY
    total_value_index ASC,
    scanned_attendance ASC;

-- 8. Which promotion categories create the strongest connected value?

SELECT
    season,
    promo_category,
    COUNT(DISTINCT promo_id) AS promotion_count,
    ROUND(AVG(total_value_index), 2) AS avg_total_value_index,
    ROUND(AVG(scanned_attendance), 2) AS avg_scanned_attendance,
    ROUND(AVG(scan_rate), 4) AS avg_scan_rate,
    ROUND(AVG(revenue_per_scanned_fan), 2) AS avg_revenue_per_scanned_fan,
    ROUND(AVG(in_park_spend_per_scanned_fan), 2) AS avg_in_park_spend_per_scanned_fan,
    ROUND(AVG(repeat_buyer_rate), 4) AS avg_repeat_buyer_rate,
    ROUND(SUM(total_revenue_indicator), 2) AS total_revenue_indicator
FROM ANALYTICS.V_PROMOTION_SCORECARD
GROUP BY
    season,
    promo_category
ORDER BY
    avg_total_value_index DESC,
    total_revenue_indicator DESC;

-- 9. Which promotions drove attendance lift but weak revenue lift?

SELECT
    season,
    game_date,
    opponent,
    promo_name,
    promo_category,
    promo_type,
    scanned_attendance,
    baseline_scanned_attendance,
    scanned_attendance_lift_vs_slot,
    revenue_per_scanned_fan,
    baseline_revenue_per_scanned_fan,
    revenue_lift_per_scanned_fan,
    total_value_index,
    recommendation,
    recommendation_reason
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE scanned_attendance_lift_vs_slot > 0
  AND revenue_lift_per_scanned_fan < 0
ORDER BY
    scanned_attendance_lift_vs_slot DESC,
    revenue_lift_per_scanned_fan ASC
LIMIT 25;

-- 10. Which promotions drove the most in-park spend?

SELECT
    season,
    game_date,
    opponent,
    promo_name,
    promo_category,
    promo_type,
    scanned_attendance,
    merch_per_scanned_fan,
    concession_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    merch_lift_per_scanned_fan,
    concession_lift_per_scanned_fan,
    total_value_index,
    recommendation
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE scanned_attendance > 0
ORDER BY
    in_park_spend_per_scanned_fan DESC,
    merch_lift_per_scanned_fan DESC,
    concession_lift_per_scanned_fan DESC
LIMIT 25;

-- 11. Who should be prioritized first in the CRM follow-up queue?

SELECT
    priority_rank,
    entity_type,
    entity_id,
    entity_display_name,
    assigned_team,
    assigned_owner,
    executive_action_bucket,
    priority_band,
    opportunity_type,
    source_signal,
    suggested_action,
    future_revenue_opportunity,
    repeat_likelihood_score,
    upgrade_potential_score,
    entity_total_value,
    entity_ticket_revenue,
    entity_in_park_revenue,
    due_date,
    status
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
ORDER BY
    priority_rank ASC
LIMIT 50;

-- 12. Which CRM action buckets are driving the queue?

SELECT
    executive_action_bucket,
    COUNT(DISTINCT follow_up_id) AS task_count,
    ROUND(SUM(future_revenue_opportunity), 2) AS total_future_revenue_opportunity,
    ROUND(AVG(priority_score), 2) AS avg_priority_score,
    ROUND(AVG(repeat_likelihood_score), 2) AS avg_repeat_likelihood_score,
    ROUND(AVG(upgrade_potential_score), 2) AS avg_upgrade_potential_score
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
GROUP BY
    executive_action_bucket
ORDER BY
    task_count DESC;

-- 13. Which teams own the follow-up workload?

SELECT
    assigned_team,
    COUNT(DISTINCT follow_up_id) AS task_count,
    COUNT_IF(priority_band = 'High') AS high_priority_tasks,
    COUNT_IF(priority_band = 'Medium') AS medium_priority_tasks,
    ROUND(SUM(future_revenue_opportunity), 2) AS total_future_revenue_opportunity,
    ROUND(AVG(priority_score), 2) AS avg_priority_score
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
GROUP BY
    assigned_team
ORDER BY
    task_count DESC;

-- 14. Which opportunity types create the most future revenue opportunity?

SELECT
    opportunity_type,
    executive_action_bucket,
    assigned_team,
    COUNT(DISTINCT follow_up_id) AS task_count,
    ROUND(SUM(future_revenue_opportunity), 2) AS total_future_revenue_opportunity,
    ROUND(AVG(future_revenue_opportunity), 2) AS avg_future_revenue_opportunity,
    ROUND(AVG(priority_score), 2) AS avg_priority_score
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
GROUP BY
    opportunity_type,
    executive_action_bucket,
    assigned_team
ORDER BY
    total_future_revenue_opportunity DESC;

-- 15. Which fans show hidden value through in-park spend?

SELECT
    entity_id AS fan_id,
    fan_segments,
    market_distance_band,
    entity_total_value,
    entity_ticket_revenue,
    entity_in_park_revenue,
    fan_merch_revenue,
    fan_concession_revenue,
    fan_engagement_count,
    fan_avg_engagement_score,
    priority_rank,
    opportunity_type,
    suggested_action,
    assigned_team,
    future_revenue_opportunity
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
WHERE entity_type = 'fan'
  AND fan_hidden_value_flag = 'True'
ORDER BY
    entity_in_park_revenue DESC,
    future_revenue_opportunity DESC
LIMIT 50;

-- 16. Which group accounts should be prioritized for renewal or upsell?

SELECT
    entity_id AS account_id,
    account_name,
    account_type,
    account_owner,
    industry,
    city,
    renewal_status,
    account_group_sale_count,
    account_group_ticket_quantity,
    account_group_revenue,
    account_avg_group_scan_rate,
    account_renewal_opportunity_count,
    account_upsell_opportunity_count,
    priority_rank,
    opportunity_type,
    suggested_action,
    future_revenue_opportunity,
    assigned_team,
    due_date
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
WHERE entity_type = 'account'
ORDER BY
    priority_rank ASC,
    account_group_revenue DESC
LIMIT 50;