USE ROLE ACCOUNTADMIN;
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
    revenue_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    homestand_total_value_index,
    recommended_focus
FROM ANALYTICS.V_HOMESTAND_SUMMARY
ORDER BY
    total_revenue_indicator DESC,
    homestand_total_value_index DESC
LIMIT 10;


-- 2. Which homestands had the strongest in-park spend per scanned fan?

SELECT
    season,
    homestand_id,
    homestand_start_date,
    homestand_end_date,
    game_count,
    opponents,
    scanned_attendance,
    merch_net_sales,
    concession_net_sales,
    in_park_spend_per_scanned_fan,
    total_revenue_indicator,
    recommended_focus
FROM ANALYTICS.V_HOMESTAND_SUMMARY
ORDER BY
    in_park_spend_per_scanned_fan DESC,
    total_revenue_indicator DESC
LIMIT 10;


-- 3. Which homestands had the most no-show recovery opportunity?

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
    high_priority_opportunity_count,
    crm_follow_up_task_count,
    future_revenue_opportunity,
    recommended_focus
FROM ANALYTICS.V_HOMESTAND_SUMMARY
ORDER BY
    no_show_ticket_quantity DESC,
    future_revenue_opportunity DESC
LIMIT 10;


-- 4. Which promotions should return?

SELECT
    season,
    game_date,
    opponent,
    day_of_week,
    promo_name,
    promo_category,
    promo_type,
    tickets_sold,
    scanned_attendance,
    scan_rate,
    revenue_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    repeat_buyer_rate,
    total_value_index,
    recommendation,
    recommendation_reason
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE LOWER(recommendation) = 'return'
ORDER BY
    total_value_index DESC,
    revenue_per_scanned_fan DESC;


-- 5. Which promotions should be reworked?

SELECT
    season,
    game_date,
    opponent,
    day_of_week,
    promo_name,
    promo_category,
    promo_type,
    scanned_attendance,
    scan_rate,
    no_show_rate,
    revenue_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    total_value_index,
    recommendation,
    recommendation_reason
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE LOWER(recommendation) = 'rework'
ORDER BY
    total_value_index DESC,
    scanned_attendance DESC
LIMIT 25;


-- 6. Which promotions should be retired?

SELECT
    season,
    game_date,
    opponent,
    day_of_week,
    promo_name,
    promo_category,
    promo_type,
    scanned_attendance,
    scan_rate,
    no_show_rate,
    revenue_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    total_value_index,
    recommendation,
    recommendation_reason
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE LOWER(recommendation) = 'retire'
ORDER BY
    total_value_index ASC,
    revenue_per_scanned_fan ASC;


-- 7. Which promotion categories produced the strongest average value?

SELECT
    promo_category,
    COUNT(*) AS promotion_count,
    ROUND(AVG(total_value_index), 2) AS avg_total_value_index,
    ROUND(AVG(scanned_attendance), 2) AS avg_scanned_attendance,
    ROUND(AVG(scan_rate), 4) AS avg_scan_rate,
    ROUND(AVG(no_show_rate), 4) AS avg_no_show_rate,
    ROUND(AVG(revenue_per_scanned_fan), 2) AS avg_revenue_per_scanned_fan,
    ROUND(AVG(in_park_spend_per_scanned_fan), 2) AS avg_in_park_spend_per_scanned_fan,
    ROUND(SUM(future_revenue_opportunity), 2) AS total_future_revenue_opportunity
FROM ANALYTICS.V_PROMOTION_SCORECARD
GROUP BY promo_category
ORDER BY
    avg_total_value_index DESC,
    avg_revenue_per_scanned_fan DESC;


-- 8. Which promotions drove attendance lift but weak revenue lift?

SELECT
    season,
    game_date,
    opponent,
    day_of_week,
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
    recommendation
FROM ANALYTICS.V_PROMOTION_SCORECARD
WHERE scanned_attendance_lift_vs_slot > 0
  AND revenue_lift_per_scanned_fan < 0
ORDER BY
    scanned_attendance_lift_vs_slot DESC,
    revenue_lift_per_scanned_fan ASC
LIMIT 25;


-- 9. Which promotions drove the strongest in-park spend?

SELECT
    season,
    game_date,
    opponent,
    day_of_week,
    promo_name,
    promo_category,
    promo_type,
    scanned_attendance,
    merch_net_sales,
    concession_net_sales,
    in_park_revenue,
    merch_per_scanned_fan,
    concession_per_scanned_fan,
    in_park_spend_per_scanned_fan,
    merch_lift_per_scanned_fan,
    concession_lift_per_scanned_fan,
    total_value_index,
    recommendation
FROM ANALYTICS.V_PROMOTION_SCORECARD
ORDER BY
    in_park_spend_per_scanned_fan DESC,
    in_park_revenue DESC
LIMIT 25;


-- 10. Which fans or accounts should be prioritized for follow-up?

SELECT
    priority_rank,
    entity_type,
    entity_id,
    entity_display_name,
    assigned_team,
    assigned_owner,
    executive_action_bucket,
    priority_score,
    priority_band,
    opportunity_type,
    source_signal,
    suggested_action,
    due_date,
    future_revenue_opportunity,
    repeat_likelihood_score,
    upgrade_potential_score,
    entity_total_value,
    entity_ticket_revenue,
    entity_in_park_revenue,
    dashboard_filter_label
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
ORDER BY priority_rank ASC
LIMIT 100;


-- 11. Which CRM action buckets are driving the queue?

SELECT
    executive_action_bucket,
    SUM(task_count) AS task_count,
    ROUND(SUM(total_future_revenue_opportunity), 2) AS total_future_revenue_opportunity,
    ROUND(AVG(avg_priority_score), 2) AS avg_priority_score,
    ROUND(AVG(avg_repeat_likelihood_score), 2) AS avg_repeat_likelihood_score,
    ROUND(AVG(avg_upgrade_potential_score), 2) AS avg_upgrade_potential_score
FROM ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY
GROUP BY executive_action_bucket
ORDER BY
    task_count DESC,
    total_future_revenue_opportunity DESC;


-- 12. Which teams own the follow-up workload?

SELECT
    assigned_team,
    SUM(task_count) AS task_count,
    ROUND(SUM(total_future_revenue_opportunity), 2) AS total_future_revenue_opportunity,
    ROUND(AVG(avg_priority_score), 2) AS avg_priority_score
FROM ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY
GROUP BY assigned_team
ORDER BY
    task_count DESC,
    total_future_revenue_opportunity DESC;


-- 13. Which assigned teams own each action bucket?

SELECT
    assigned_team,
    executive_action_bucket,
    priority_band,
    task_count,
    total_future_revenue_opportunity,
    avg_priority_score,
    avg_repeat_likelihood_score,
    avg_upgrade_potential_score
FROM ANALYTICS.V_CRM_ACTION_BUCKET_SUMMARY
ORDER BY
    assigned_team,
    executive_action_bucket,
    priority_band;


-- 14. Which hidden-value fans should be reviewed first?

SELECT
    priority_rank,
    fan_id,
    entity_display_name,
    assigned_team,
    executive_action_bucket,
    priority_score,
    priority_band,
    opportunity_type,
    suggested_action,
    fan_segments,
    fan_ticket_revenue,
    fan_in_park_revenue,
    fan_total_value,
    fan_scan_rate,
    fan_no_show_rate,
    fan_engagement_count,
    future_revenue_opportunity
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
WHERE entity_type = 'fan'
  AND fan_hidden_value_flag = TRUE
ORDER BY
    priority_rank ASC
LIMIT 100;


-- 15. Which group accounts should group sales prioritize?

SELECT
    priority_rank,
    account_id,
    account_name,
    account_type,
    account_owner,
    industry,
    city,
    renewal_status,
    assigned_team,
    executive_action_bucket,
    priority_score,
    opportunity_type,
    suggested_action,
    account_group_sale_count,
    account_group_ticket_quantity,
    account_group_revenue,
    account_avg_group_scan_rate,
    account_total_value,
    future_revenue_opportunity
FROM ANALYTICS.V_CRM_FOLLOW_UP_QUEUE
WHERE entity_type = 'account'
ORDER BY
    priority_rank ASC
LIMIT 100;