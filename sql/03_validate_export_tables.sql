USE WAREHOUSE TP_REPORTING_WH;
USE DATABASE TRASH_PANDAS_CONNECTED_REPORTING;

CREATE OR REPLACE VIEW QA.V_EXPORT_VALIDATION_RESULTS AS

WITH validation_checks AS (

    SELECT
        'homestand_row_count' AS check_name,
        'RAW.HOMESTAND_SUMMARY' AS table_name,
        '34' AS expected_value,
        TO_VARCHAR(COUNT(*)) AS actual_value,
        IFF(COUNT(*) = 34, 'PASS', 'FAIL') AS check_status
    FROM RAW.HOMESTAND_SUMMARY

    UNION ALL

    SELECT
        'promotion_scorecard_row_count' AS check_name,
        'RAW.PROMOTION_SCORECARD' AS table_name,
        '233' AS expected_value,
        TO_VARCHAR(COUNT(*)) AS actual_value,
        IFF(COUNT(*) = 233, 'PASS', 'FAIL') AS check_status
    FROM RAW.PROMOTION_SCORECARD

    UNION ALL

    SELECT
        'crm_follow_up_queue_row_count' AS check_name,
        'RAW.CRM_FOLLOW_UP_QUEUE' AS table_name,
        '15000' AS expected_value,
        TO_VARCHAR(COUNT(*)) AS actual_value,
        IFF(COUNT(*) = 15000, 'PASS', 'FAIL') AS check_status
    FROM RAW.CRM_FOLLOW_UP_QUEUE

    UNION ALL

    SELECT
        'homestand_tickets_sold_total' AS check_name,
        'RAW.HOMESTAND_SUMMARY' AS table_name,
        '1274234' AS expected_value,
        TO_VARCHAR(SUM(tickets_sold)) AS actual_value,
        IFF(SUM(tickets_sold) = 1274234, 'PASS', 'FAIL') AS check_status
    FROM RAW.HOMESTAND_SUMMARY

    UNION ALL

    SELECT
        'homestand_scanned_attendance_total' AS check_name,
        'RAW.HOMESTAND_SUMMARY' AS table_name,
        '1126560' AS expected_value,
        TO_VARCHAR(SUM(scanned_attendance)) AS actual_value,
        IFF(SUM(scanned_attendance) = 1126560, 'PASS', 'FAIL') AS check_status
    FROM RAW.HOMESTAND_SUMMARY

    UNION ALL

    SELECT
        'homestand_total_revenue_indicator_total' AS check_name,
        'RAW.HOMESTAND_SUMMARY' AS table_name,
        '28655060.87' AS expected_value,
        TO_VARCHAR(ROUND(SUM(total_revenue_indicator), 2)) AS actual_value,
        IFF(ROUND(SUM(total_revenue_indicator), 2) = 28655060.87, 'PASS', 'FAIL') AS check_status
    FROM RAW.HOMESTAND_SUMMARY

    UNION ALL

    SELECT
        'crm_future_revenue_opportunity_total' AS check_name,
        'RAW.CRM_FOLLOW_UP_QUEUE' AS table_name,
        '12605270.19' AS expected_value,
        TO_VARCHAR(ROUND(SUM(future_revenue_opportunity), 2)) AS actual_value,
        IFF(ROUND(SUM(future_revenue_opportunity), 2) = 12605270.19, 'PASS', 'FAIL') AS check_status
    FROM RAW.CRM_FOLLOW_UP_QUEUE

    UNION ALL

    SELECT
        'duplicate_homestand_keys' AS check_name,
        'RAW.HOMESTAND_SUMMARY' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT(*) - COUNT(DISTINCT season || '|' || homestand_id)) AS actual_value,
        IFF(COUNT(*) - COUNT(DISTINCT season || '|' || homestand_id) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.HOMESTAND_SUMMARY

    UNION ALL

    SELECT
        'duplicate_promo_ids' AS check_name,
        'RAW.PROMOTION_SCORECARD' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT(*) - COUNT(DISTINCT promo_id)) AS actual_value,
        IFF(COUNT(*) - COUNT(DISTINCT promo_id) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.PROMOTION_SCORECARD

    UNION ALL

    SELECT
        'duplicate_follow_up_ids' AS check_name,
        'RAW.CRM_FOLLOW_UP_QUEUE' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT(*) - COUNT(DISTINCT follow_up_id)) AS actual_value,
        IFF(COUNT(*) - COUNT(DISTINCT follow_up_id) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.CRM_FOLLOW_UP_QUEUE

    UNION ALL

    SELECT
        'invalid_promotion_recommendations' AS check_name,
        'RAW.PROMOTION_SCORECARD' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT_IF(recommendation NOT IN ('return', 'rework', 'retire', 'review'))) AS actual_value,
        IFF(COUNT_IF(recommendation NOT IN ('return', 'rework', 'retire', 'review')) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.PROMOTION_SCORECARD

    UNION ALL

    SELECT
        'invalid_crm_entity_mapping' AS check_name,
        'RAW.CRM_FOLLOW_UP_QUEUE' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(
            COUNT_IF(
                (entity_type = 'fan' AND (fan_id IS NULL OR fan_id = '' OR account_id IS NOT NULL AND account_id <> '' OR entity_id <> fan_id))
                OR
                (entity_type = 'account' AND (account_id IS NULL OR account_id = '' OR fan_id IS NOT NULL AND fan_id <> '' OR entity_id <> account_id))
                OR
                (entity_type NOT IN ('fan', 'account'))
            )
        ) AS actual_value,
        IFF(
            COUNT_IF(
                (entity_type = 'fan' AND (fan_id IS NULL OR fan_id = '' OR account_id IS NOT NULL AND account_id <> '' OR entity_id <> fan_id))
                OR
                (entity_type = 'account' AND (account_id IS NULL OR account_id = '' OR fan_id IS NOT NULL AND fan_id <> '' OR entity_id <> account_id))
                OR
                (entity_type NOT IN ('fan', 'account'))
            ) = 0,
            'PASS',
            'FAIL'
        ) AS check_status
    FROM RAW.CRM_FOLLOW_UP_QUEUE

    UNION ALL

    SELECT
        'duplicate_priority_ranks' AS check_name,
        'RAW.CRM_FOLLOW_UP_QUEUE' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT(*) - COUNT(DISTINCT priority_rank)) AS actual_value,
        IFF(COUNT(*) - COUNT(DISTINCT priority_rank) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.CRM_FOLLOW_UP_QUEUE

    UNION ALL

    SELECT
        'invalid_homestand_rate_ranges' AS check_name,
        'RAW.HOMESTAND_SUMMARY' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT_IF(scan_rate < 0 OR scan_rate > 1 OR no_show_rate < 0 OR no_show_rate > 1)) AS actual_value,
        IFF(COUNT_IF(scan_rate < 0 OR scan_rate > 1 OR no_show_rate < 0 OR no_show_rate > 1) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.HOMESTAND_SUMMARY

    UNION ALL

    SELECT
        'invalid_promotion_rate_ranges' AS check_name,
        'RAW.PROMOTION_SCORECARD' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT_IF(scan_rate < 0 OR scan_rate > 1 OR no_show_rate < 0 OR no_show_rate > 1 OR repeat_buyer_rate < 0 OR repeat_buyer_rate > 1)) AS actual_value,
        IFF(COUNT_IF(scan_rate < 0 OR scan_rate > 1 OR no_show_rate < 0 OR no_show_rate > 1 OR repeat_buyer_rate < 0 OR repeat_buyer_rate > 1) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.PROMOTION_SCORECARD

    UNION ALL

    SELECT
        'invalid_crm_rate_ranges' AS check_name,
        'RAW.CRM_FOLLOW_UP_QUEUE' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT_IF(fan_scan_rate < 0 OR fan_scan_rate > 1 OR fan_no_show_rate < 0 OR fan_no_show_rate > 1 OR account_avg_group_scan_rate < 0 OR account_avg_group_scan_rate > 1)) AS actual_value,
        IFF(COUNT_IF(fan_scan_rate < 0 OR fan_scan_rate > 1 OR fan_no_show_rate < 0 OR fan_no_show_rate > 1 OR account_avg_group_scan_rate < 0 OR account_avg_group_scan_rate > 1) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.CRM_FOLLOW_UP_QUEUE

    UNION ALL

    SELECT
        'negative_homestand_revenue_values' AS check_name,
        'RAW.HOMESTAND_SUMMARY' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT_IF(net_ticket_revenue < 0 OR group_ticket_revenue < 0 OR merch_net_sales < 0 OR concession_net_sales < 0 OR total_revenue_indicator < 0)) AS actual_value,
        IFF(COUNT_IF(net_ticket_revenue < 0 OR group_ticket_revenue < 0 OR merch_net_sales < 0 OR concession_net_sales < 0 OR total_revenue_indicator < 0) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.HOMESTAND_SUMMARY

    UNION ALL

    SELECT
        'negative_promotion_revenue_values' AS check_name,
        'RAW.PROMOTION_SCORECARD' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT_IF(group_revenue < 0 OR merch_net_sales < 0 OR concession_net_sales < 0 OR total_revenue_indicator < 0 OR future_revenue_opportunity < 0)) AS actual_value,
        IFF(COUNT_IF(group_revenue < 0 OR merch_net_sales < 0 OR concession_net_sales < 0 OR total_revenue_indicator < 0 OR future_revenue_opportunity < 0) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.PROMOTION_SCORECARD

    UNION ALL

    SELECT
        'negative_crm_revenue_values' AS check_name,
        'RAW.CRM_FOLLOW_UP_QUEUE' AS table_name,
        '0' AS expected_value,
        TO_VARCHAR(COUNT_IF(future_revenue_opportunity < 0 OR entity_total_value < 0 OR entity_ticket_revenue < 0 OR entity_in_park_revenue < 0)) AS actual_value,
        IFF(COUNT_IF(future_revenue_opportunity < 0 OR entity_total_value < 0 OR entity_ticket_revenue < 0 OR entity_in_park_revenue < 0) = 0, 'PASS', 'FAIL') AS check_status
    FROM RAW.CRM_FOLLOW_UP_QUEUE

)

SELECT
    check_name,
    table_name,
    expected_value,
    actual_value,
    check_status
FROM validation_checks;

SELECT
    check_name,
    table_name,
    expected_value,
    actual_value,
    check_status
FROM QA.V_EXPORT_VALIDATION_RESULTS
ORDER BY
    CASE check_status
        WHEN 'FAIL' THEN 1
        WHEN 'PASS' THEN 2
        ELSE 3
    END,
    check_name;