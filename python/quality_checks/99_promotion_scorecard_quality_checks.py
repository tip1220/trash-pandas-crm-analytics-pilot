import csv
from pathlib import Path
from collections import Counter
import pandas as pd

scorecard_path = Path("data/exports/promotion_scorecard.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
games_path = Path("data/processed/games_clean.csv")
summary_path = Path("data/exports/promotion_scorecard_quality_summary.csv")

summary_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    return pd.read_csv(path, dtype=str)

def to_number(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def add_check(checks, check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

scorecard = read_csv(scorecard_path)
promotions = read_csv(promotions_path)
games = read_csv(games_path)

checks = []

required_columns = [
    "promo_id",
    "game_id",
    "season",
    "game_date",
    "homestand_id",
    "opponent",
    "day_of_week",
    "promo_name",
    "promo_category",
    "promo_type",
    "tickets_sold",
    "scanned_attendance",
    "scan_rate",
    "no_show_ticket_quantity",
    "no_show_rate",
    "repeat_buyer_rate",
    "group_tickets",
    "merch_net_sales",
    "concession_net_sales",
    "revenue_per_scanned_fan",
    "merch_per_scanned_fan",
    "concession_per_scanned_fan",
    "in_park_spend_per_scanned_fan",
    "total_revenue_indicator",
    "fan_engagement_count",
    "follow_up_opportunity_count",
    "high_priority_opportunity_count",
    "crm_follow_up_task_count",
    "future_revenue_opportunity",
    "scanned_attendance_lift_vs_slot",
    "merch_lift_per_scanned_fan",
    "concession_lift_per_scanned_fan",
    "revenue_lift_per_scanned_fan",
    "repeat_buyer_rate_lift_vs_slot",
    "total_value_index",
    "recommendation",
    "recommendation_reason"
]

missing_columns = [
    column for column in required_columns
    if column not in scorecard.columns
]

add_check(
    checks,
    "missing_required_columns",
    "Check required promotion scorecard columns exist",
    "0",
    str(len(missing_columns)),
    "PASS" if len(missing_columns) == 0 else "FAIL"
)

add_check(
    checks,
    "promotion_scorecard_rows",
    "Count promotion scorecard rows",
    str(len(promotions)),
    str(len(scorecard)),
    "PASS" if len(scorecard) == len(promotions) else "FAIL"
)

duplicate_promo_ids = scorecard.duplicated(subset=["promo_id"]).sum()

add_check(
    checks,
    "duplicate_promo_ids",
    "Check duplicate promo_id values",
    "0",
    str(int(duplicate_promo_ids)),
    "PASS" if duplicate_promo_ids == 0 else "FAIL"
)

promotion_ids = set(promotions["promo_id"])
scorecard_promo_ids = set(scorecard["promo_id"])

missing_source_promo_ids = promotion_ids - scorecard_promo_ids
extra_scorecard_promo_ids = scorecard_promo_ids - promotion_ids

add_check(
    checks,
    "missing_source_promo_ids",
    "Check every source promotion appears in scorecard",
    "0",
    str(len(missing_source_promo_ids)),
    "PASS" if len(missing_source_promo_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "extra_scorecard_promo_ids",
    "Check scorecard has no promo_id values outside promotions_clean.csv",
    "0",
    str(len(extra_scorecard_promo_ids)),
    "PASS" if len(extra_scorecard_promo_ids) == 0 else "FAIL"
)

game_ids = set(games["game_id"])

invalid_game_ids = scorecard[
    ~scorecard["game_id"].isin(game_ids)
]

add_check(
    checks,
    "invalid_game_ids",
    "Check every scorecard game_id exists in games_clean.csv",
    "0",
    str(len(invalid_game_ids)),
    "PASS" if len(invalid_game_ids) == 0 else "FAIL"
)

valid_recommendations = {"return", "rework", "retire", "review"}

invalid_recommendations = scorecard[
    ~scorecard["recommendation"].isin(valid_recommendations)
]

add_check(
    checks,
    "invalid_recommendations",
    "Check recommendation values",
    "0",
    str(len(invalid_recommendations)),
    "PASS" if len(invalid_recommendations) == 0 else "FAIL"
)

missing_recommendation_reasons = scorecard[
    scorecard["recommendation_reason"].astype(str).str.strip().eq("")
]

add_check(
    checks,
    "missing_recommendation_reasons",
    "Check every recommendation has a recommendation_reason",
    "0",
    str(len(missing_recommendation_reasons)),
    "PASS" if len(missing_recommendation_reasons) == 0 else "FAIL"
)

numeric_columns = [
    "tickets_sold",
    "scanned_attendance",
    "scan_rate",
    "no_show_ticket_quantity",
    "no_show_rate",
    "ticket_order_count",
    "unique_ticket_buyers",
    "repeat_buyer_count",
    "repeat_buyer_rate",
    "group_tickets",
    "group_revenue",
    "merch_net_sales",
    "concession_net_sales",
    "revenue_per_scanned_fan",
    "merch_per_scanned_fan",
    "concession_per_scanned_fan",
    "in_park_spend_per_scanned_fan",
    "total_revenue_indicator",
    "fan_engagement_count",
    "unique_engaged_fans",
    "avg_engagement_score",
    "follow_up_opportunity_count",
    "high_priority_opportunity_count",
    "crm_follow_up_task_count",
    "future_revenue_opportunity",
    "total_value_index"
]

negative_numeric_columns = []

for column in numeric_columns:
    bad_rows = scorecard[to_number(scorecard[column]) < 0]

    if len(bad_rows) > 0:
        negative_numeric_columns.append(column)

add_check(
    checks,
    "negative_numeric_columns",
    "Check key numeric columns are non-negative",
    "0 columns",
    str(len(negative_numeric_columns)),
    "PASS" if len(negative_numeric_columns) == 0 else "FAIL"
)

bad_total_revenue_indicator = []

for _, row in scorecard.iterrows():
    expected_total = (
        float(row["merch_net_sales"])
        + float(row["concession_net_sales"])
        + float(row["total_revenue_indicator"])
        - float(row["merch_net_sales"])
        - float(row["concession_net_sales"])
    )

    actual_total = float(row["total_revenue_indicator"])

    if actual_total < 0 or expected_total < 0:
        bad_total_revenue_indicator.append(row)

add_check(
    checks,
    "bad_total_revenue_indicator_values",
    "Check total_revenue_indicator values are valid",
    "0",
    str(len(bad_total_revenue_indicator)),
    "PASS" if len(bad_total_revenue_indicator) == 0 else "FAIL"
)

bad_scan_rate_logic = []
bad_no_show_rate_logic = []
bad_per_fan_logic = []

for _, row in scorecard.iterrows():
    tickets_sold = float(row["tickets_sold"])
    scanned_attendance = float(row["scanned_attendance"])
    no_show_quantity = float(row["no_show_ticket_quantity"])
    scan_rate = float(row["scan_rate"])
    no_show_rate = float(row["no_show_rate"])

    if tickets_sold > 0:
        expected_scan_rate = scanned_attendance / tickets_sold
        expected_no_show_rate = no_show_quantity / tickets_sold

        if abs(expected_scan_rate - scan_rate) > 0.001:
            bad_scan_rate_logic.append(row)

        if abs(expected_no_show_rate - no_show_rate) > 0.001:
            bad_no_show_rate_logic.append(row)

    if scanned_attendance > 0:
        expected_merch_per_fan = float(row["merch_net_sales"]) / scanned_attendance
        expected_concession_per_fan = float(row["concession_net_sales"]) / scanned_attendance
        expected_in_park_per_fan = (
            float(row["merch_net_sales"]) + float(row["concession_net_sales"])
        ) / scanned_attendance

        if abs(expected_merch_per_fan - float(row["merch_per_scanned_fan"])) > 0.02:
            bad_per_fan_logic.append(row)

        if abs(expected_concession_per_fan - float(row["concession_per_scanned_fan"])) > 0.02:
            bad_per_fan_logic.append(row)

        if abs(expected_in_park_per_fan - float(row["in_park_spend_per_scanned_fan"])) > 0.02:
            bad_per_fan_logic.append(row)

add_check(
    checks,
    "bad_scan_rate_logic",
    "Check scan_rate calculation",
    "0",
    str(len(bad_scan_rate_logic)),
    "PASS" if len(bad_scan_rate_logic) == 0 else "FAIL"
)

add_check(
    checks,
    "bad_no_show_rate_logic",
    "Check no_show_rate calculation",
    "0",
    str(len(bad_no_show_rate_logic)),
    "PASS" if len(bad_no_show_rate_logic) == 0 else "FAIL"
)

add_check(
    checks,
    "bad_per_scanned_fan_logic",
    "Check per-scanned-fan calculation logic",
    "0",
    str(len(bad_per_fan_logic)),
    "PASS" if len(bad_per_fan_logic) == 0 else "FAIL"
)

bad_rate_ranges = scorecard[
    (to_number(scorecard["scan_rate"]) < 0)
    | (to_number(scorecard["scan_rate"]) > 1)
    | (to_number(scorecard["no_show_rate"]) < 0)
    | (to_number(scorecard["no_show_rate"]) > 1)
    | (to_number(scorecard["repeat_buyer_rate"]) < 0)
    | (to_number(scorecard["repeat_buyer_rate"]) > 1)
]

add_check(
    checks,
    "bad_rate_ranges",
    "Check rate columns are between 0 and 1",
    "0",
    str(len(bad_rate_ranges)),
    "PASS" if len(bad_rate_ranges) == 0 else "FAIL"
)

bad_index_rows = scorecard[
    (to_number(scorecard["total_value_index"]) < 0)
    | (to_number(scorecard["total_value_index"]) > 100)
]

add_check(
    checks,
    "bad_total_value_index",
    "Check total_value_index is between 0 and 100",
    "0",
    str(len(bad_index_rows)),
    "PASS" if len(bad_index_rows) == 0 else "FAIL"
)

valid_promo_categories = set(promotions["promo_category"].dropna().unique())
invalid_promo_categories = scorecard[
    ~scorecard["promo_category"].isin(valid_promo_categories)
]

add_check(
    checks,
    "invalid_promo_categories",
    "Check promo_category values match source promotions",
    "0",
    str(len(invalid_promo_categories)),
    "PASS" if len(invalid_promo_categories) == 0 else "FAIL"
)

recommendation_counts = scorecard["recommendation"].value_counts().to_dict()

for recommendation in sorted(valid_recommendations):
    add_check(
        checks,
        f"recommendation_count_{recommendation}",
        f"Report recommendation count: {recommendation}",
        "Review only",
        str(recommendation_counts.get(recommendation, 0)),
        "PASS"
    )

category_counts = scorecard["promo_category"].value_counts().to_dict()

for category, count in sorted(category_counts.items()):
    add_check(
        checks,
        f"promo_category_count_{category}",
        f"Report promo category count: {category}",
        "Review only",
        str(count),
        "PASS"
    )

add_check(
    checks,
    "average_total_value_index",
    "Report average total_value_index",
    "Review only",
    f"{float(to_number(scorecard['total_value_index']).mean()):.2f}",
    "PASS"
)

add_check(
    checks,
    "max_total_value_index",
    "Report max total_value_index",
    "Review only",
    f"{float(to_number(scorecard['total_value_index']).max()):.2f}",
    "PASS"
)

add_check(
    checks,
    "min_total_value_index",
    "Report min total_value_index",
    "Review only",
    f"{float(to_number(scorecard['total_value_index']).min()):.2f}",
    "PASS"
)

with summary_path.open("w", newline="") as f:
    fieldnames = ["check_name", "result", "expected", "actual", "status"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(checks)

for check in checks:
    print(f"{check['status']}: {check['check_name']} | expected={check['expected']} | actual={check['actual']}")

fail_count = sum(1 for check in checks if check["status"] == "FAIL")
review_count = sum(1 for check in checks if check["status"] == "REVIEW")

print(f"\nQuality check summary saved to {summary_path}")
print(f"FAIL checks: {fail_count}")
print(f"REVIEW checks: {review_count}")

if fail_count > 0:
    raise SystemExit(1)