USE ROLE ACCOUNTADMIN;
USE WAREHOUSE TP_REPORTING_WH;
USE DATABASE TRASH_PANDAS_CONNECTED_REPORTING;
USE SCHEMA RAW;

SELECT
    'HOMESTAND_SUMMARY row count' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    34::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 34 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.HOMESTAND_SUMMARY

UNION ALL

SELECT
    'PROMOTION_SCORECARD row count' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    233::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 233 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.PROMOTION_SCORECARD

UNION ALL

SELECT
    'CRM_FOLLOW_UP_QUEUE row count' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    15000::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 15000 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.CRM_FOLLOW_UP_QUEUE

UNION ALL

SELECT
    'Homestand tickets sold' AS validation_check,
    SUM(tickets_sold)::NUMBER(18,2) AS actual_value,
    1274234::NUMBER(18,2) AS expected_value,
    CASE WHEN SUM(tickets_sold) = 1274234 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.HOMESTAND_SUMMARY

UNION ALL

SELECT
    'Homestand scanned attendance' AS validation_check,
    SUM(scanned_attendance)::NUMBER(18,2) AS actual_value,
    1126560::NUMBER(18,2) AS expected_value,
    CASE WHEN SUM(scanned_attendance) = 1126560 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.HOMESTAND_SUMMARY

UNION ALL

SELECT
    'Homestand total revenue indicator' AS validation_check,
    ROUND(SUM(total_revenue_indicator), 2)::NUMBER(18,2) AS actual_value,
    28655060.87::NUMBER(18,2) AS expected_value,
    CASE
        WHEN ROUND(SUM(total_revenue_indicator), 2) = 28655060.87 THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM RAW.HOMESTAND_SUMMARY

UNION ALL

SELECT
    'CRM future revenue opportunity' AS validation_check,
    ROUND(SUM(future_revenue_opportunity), 2)::NUMBER(18,2) AS actual_value,
    12605270.19::NUMBER(18,2) AS expected_value,
    CASE
        WHEN ROUND(SUM(future_revenue_opportunity), 2) = 12605270.19 THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_status
FROM RAW.CRM_FOLLOW_UP_QUEUE

UNION ALL

SELECT
    'Duplicate homestand keys' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    0::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM (
    SELECT season, homestand_id, COUNT(*) AS record_count
    FROM RAW.HOMESTAND_SUMMARY
    GROUP BY season, homestand_id
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'Duplicate promo IDs' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    0::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM (
    SELECT promo_id, COUNT(*) AS record_count
    FROM RAW.PROMOTION_SCORECARD
    GROUP BY promo_id
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'Duplicate follow-up IDs' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    0::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM (
    SELECT follow_up_id, COUNT(*) AS record_count
    FROM RAW.CRM_FOLLOW_UP_QUEUE
    GROUP BY follow_up_id
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'Invalid promotion recommendations' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    0::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.PROMOTION_SCORECARD
WHERE LOWER(recommendation) NOT IN ('return', 'rework', 'retire', 'review')

UNION ALL

SELECT
    'Invalid CRM entity mapping' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    0::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.CRM_FOLLOW_UP_QUEUE
WHERE entity_id IS NULL
   OR entity_type IS NULL
   OR LOWER(entity_type) NOT IN ('fan', 'account')

UNION ALL

SELECT
    'Invalid homestand scan/no-show rates' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    0::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.HOMESTAND_SUMMARY
WHERE scan_rate < 0
   OR scan_rate > 1
   OR no_show_rate < 0
   OR no_show_rate > 1

UNION ALL

SELECT
    'Negative revenue values' AS validation_check,
    COUNT(*)::NUMBER(18,2) AS actual_value,
    0::NUMBER(18,2) AS expected_value,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS validation_status
FROM RAW.HOMESTAND_SUMMARY
WHERE net_ticket_revenue < 0
   OR merch_net_sales < 0
   OR concession_net_sales < 0
   OR total_revenue_indicator < 0
ORDER BY validation_check;