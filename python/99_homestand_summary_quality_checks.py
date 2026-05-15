import csv
from pathlib import Path
import pandas as pd

homestand_path = Path("data/exports/homestand_summary.csv")
games_path = Path("data/processed/games_clean.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")
merch_path = Path("data/synthetic/merch_transactions.csv")
concessions_path = Path("data/synthetic/concession_transactions.csv")
summary_path = Path("data/exports/homestand_summary_quality_summary.csv")

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

homestand = read_csv(homestand_path)
games = read_csv(games_path)
orders = read_csv(orders_path)
scans = read_csv(scans_path)
merch = read_csv(merch_path)
concessions = read_csv(concessions_path)

checks = []

required_columns = [
    "season",
    "homestand_id",
    "homestand_start_date",
    "homestand_end_date",
    "game_count",
    "tickets_sold",
    "scanned_attendance",
    "scan_rate",
    "no_show_ticket_quantity",
    "no_show_rate",
    "net_ticket_revenue",
    "merch_net_sales",
    "concession_net_sales",
    "in_park_spend_per_scanned_fan",
    "total_revenue_indicator",
    "follow_up_opportunity_count",
    "crm_follow_up_task_count",
    "future_revenue_opportunity",
    "homestand_total_value_index",
    "recommended_focus"
]

missing_columns = [
    column for column in required_columns
    if column not in homestand.columns
]

add_check(
    checks,
    "missing_required_columns",
    "Check required homestand summary columns exist",
    "0",
    str(len(missing_columns)),
    "PASS" if len(missing_columns) == 0 else "FAIL"
)

add_check(
    checks,
    "homestand_rows",
    "Count homestand summary rows",
    "> 0",
    str(len(homestand)),
    "PASS" if len(homestand) > 0 else "FAIL"
)

duplicate_homestand_keys = homestand.duplicated(subset=["season", "homestand_id"]).sum()

add_check(
    checks,
    "duplicate_homestand_keys",
    "Check duplicate season/homestand_id rows",
    "0",
    str(int(duplicate_homestand_keys)),
    "PASS" if duplicate_homestand_keys == 0 else "FAIL"
)

total_games_source = len(games)
total_games_export = int(to_number(homestand["game_count"]).sum())

add_check(
    checks,
    "total_game_count_matches_source",
    "Check summed homestand game_count matches games_clean.csv",
    str(total_games_source),
    str(total_games_export),
    "PASS" if total_games_export == total_games_source else "FAIL"
)

bad_game_counts = homestand[
    (to_number(homestand["game_count"]) <= 0)
    | (to_number(homestand["game_count"]) > 12)
]

add_check(
    checks,
    "bad_game_counts",
    "Check homestand game_count values are within expected range",
    "0",
    str(len(bad_game_counts)),
    "PASS" if len(bad_game_counts) == 0 else "REVIEW"
)

date_errors = []

for _, row in homestand.iterrows():
    try:
        start_date = pd.to_datetime(row["homestand_start_date"])
        end_date = pd.to_datetime(row["homestand_end_date"])

        if end_date < start_date:
            date_errors.append(row)
    except Exception:
        date_errors.append(row)

add_check(
    checks,
    "bad_homestand_dates",
    "Check homestand start/end date logic",
    "0",
    str(len(date_errors)),
    "PASS" if len(date_errors) == 0 else "FAIL"
)

source_tickets_sold = int(to_number(orders["ticket_quantity"]).sum())
export_tickets_sold = int(to_number(homestand["tickets_sold"]).sum())

add_check(
    checks,
    "tickets_sold_matches_source",
    "Check homestand tickets_sold matches ticket_orders.csv",
    str(source_tickets_sold),
    str(export_tickets_sold),
    "PASS" if source_tickets_sold == export_tickets_sold else "FAIL"
)

source_scanned_attendance = int(to_number(scans["scanned_ticket_quantity"]).sum())
export_scanned_attendance = int(to_number(homestand["scanned_attendance"]).sum())

add_check(
    checks,
    "scanned_attendance_matches_source",
    "Check homestand scanned_attendance matches ticket_scans.csv",
    str(source_scanned_attendance),
    str(export_scanned_attendance),
    "PASS" if source_scanned_attendance == export_scanned_attendance else "FAIL"
)

source_no_show_quantity = int(to_number(scans["no_show_ticket_quantity"]).sum())
export_no_show_quantity = int(to_number(homestand["no_show_ticket_quantity"]).sum())

add_check(
    checks,
    "no_show_quantity_matches_source",
    "Check homestand no_show_ticket_quantity matches ticket_scans.csv",
    str(source_no_show_quantity),
    str(export_no_show_quantity),
    "PASS" if source_no_show_quantity == export_no_show_quantity else "FAIL"
)

source_ticket_revenue = round(float(to_number(orders["net_ticket_revenue"]).sum()), 2)
export_ticket_revenue = round(float(to_number(homestand["net_ticket_revenue"]).sum()), 2)

add_check(
    checks,
    "ticket_revenue_matches_source",
    "Check homestand net_ticket_revenue matches ticket_orders.csv",
    f"{source_ticket_revenue:.2f}",
    f"{export_ticket_revenue:.2f}",
    "PASS" if abs(source_ticket_revenue - export_ticket_revenue) <= 0.05 else "FAIL"
)

source_merch_revenue = round(float(to_number(merch["net_sales"]).sum()), 2)
export_merch_revenue = round(float(to_number(homestand["merch_net_sales"]).sum()), 2)

add_check(
    checks,
    "merch_revenue_matches_source",
    "Check homestand merch_net_sales matches merch_transactions.csv",
    f"{source_merch_revenue:.2f}",
    f"{export_merch_revenue:.2f}",
    "PASS" if abs(source_merch_revenue - export_merch_revenue) <= 0.05 else "FAIL"
)

source_concession_revenue = round(float(to_number(concessions["net_sales"]).sum()), 2)
export_concession_revenue = round(float(to_number(homestand["concession_net_sales"]).sum()), 2)

add_check(
    checks,
    "concession_revenue_matches_source",
    "Check homestand concession_net_sales matches concession_transactions.csv",
    f"{source_concession_revenue:.2f}",
    f"{export_concession_revenue:.2f}",
    "PASS" if abs(source_concession_revenue - export_concession_revenue) <= 0.05 else "FAIL"
)

bad_revenue_indicator = []

for _, row in homestand.iterrows():
    expected_total = (
        float(row["net_ticket_revenue"])
        + float(row["merch_net_sales"])
        + float(row["concession_net_sales"])
    )

    actual_total = float(row["total_revenue_indicator"])

    if abs(expected_total - actual_total) > 0.05:
        bad_revenue_indicator.append(row)

add_check(
    checks,
    "bad_total_revenue_indicator_logic",
    "Check total_revenue_indicator equals ticket + merch + concessions",
    "0",
    str(len(bad_revenue_indicator)),
    "PASS" if len(bad_revenue_indicator) == 0 else "FAIL"
)

bad_scan_rate_logic = []
bad_no_show_rate_logic = []
bad_per_fan_logic = []

for _, row in homestand.iterrows():
    scan_ticket_quantity = float(row.get("tickets_sold", 0))
    scanned_attendance = float(row.get("scanned_attendance", 0))
    no_show_quantity = float(row.get("no_show_ticket_quantity", 0))
    scan_rate = float(row.get("scan_rate", 0))
    no_show_rate = float(row.get("no_show_rate", 0))

    if scan_ticket_quantity > 0:
        expected_scan_rate = scanned_attendance / scan_ticket_quantity
        expected_no_show_rate = no_show_quantity / scan_ticket_quantity

        if abs(expected_scan_rate - scan_rate) > 0.001:
            bad_scan_rate_logic.append(row)

        if abs(expected_no_show_rate - no_show_rate) > 0.001:
            bad_no_show_rate_logic.append(row)

    if scanned_attendance > 0:
        expected_in_park = (
            float(row["merch_net_sales"])
            + float(row["concession_net_sales"])
        ) / scanned_attendance

        actual_in_park = float(row["in_park_spend_per_scanned_fan"])

        if abs(expected_in_park - actual_in_park) > 0.02:
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
    "bad_in_park_spend_per_scanned_fan_logic",
    "Check in_park_spend_per_scanned_fan calculation",
    "0",
    str(len(bad_per_fan_logic)),
    "PASS" if len(bad_per_fan_logic) == 0 else "FAIL"
)

negative_numeric_rows = []

numeric_columns = [
    "game_count",
    "tickets_sold",
    "scanned_attendance",
    "no_show_ticket_quantity",
    "net_ticket_revenue",
    "group_ticket_quantity",
    "group_ticket_revenue",
    "merch_net_sales",
    "concession_net_sales",
    "total_revenue_indicator",
    "follow_up_opportunity_count",
    "crm_follow_up_task_count",
    "future_revenue_opportunity",
    "homestand_total_value_index"
]

for column in numeric_columns:
    bad_rows = homestand[to_number(homestand[column]) < 0]
    if len(bad_rows) > 0:
        negative_numeric_rows.append(column)

add_check(
    checks,
    "negative_numeric_columns",
    "Check key numeric columns are non-negative",
    "0 columns",
    str(len(negative_numeric_rows)),
    "PASS" if len(negative_numeric_rows) == 0 else "FAIL"
)

bad_index_rows = homestand[
    (to_number(homestand["homestand_total_value_index"]) < 0)
    | (to_number(homestand["homestand_total_value_index"]) > 100)
]

add_check(
    checks,
    "bad_homestand_total_value_index",
    "Check homestand_total_value_index is between 0 and 100",
    "0",
    str(len(bad_index_rows)),
    "PASS" if len(bad_index_rows) == 0 else "FAIL"
)

valid_focus_values = {
    "No-show recovery",
    "Group sales renewal",
    "In-park spend growth",
    "Engagement follow-up",
    "Repeat what worked",
    "Baseline review"
}

invalid_focus_rows = homestand[
    ~homestand["recommended_focus"].isin(valid_focus_values)
]

add_check(
    checks,
    "invalid_recommended_focus_values",
    "Check recommended_focus values",
    "0",
    str(len(invalid_focus_rows)),
    "PASS" if len(invalid_focus_rows) == 0 else "FAIL"
)

focus_counts = homestand["recommended_focus"].value_counts().to_dict()

for focus in sorted(valid_focus_values):
    add_check(
        checks,
        f"recommended_focus_count_{focus}",
        f"Report recommended_focus count: {focus}",
        "Review only",
        str(focus_counts.get(focus, 0)),
        "PASS"
    )

add_check(
    checks,
    "total_revenue_indicator",
    "Report total revenue indicator",
    "Review only",
    f"{float(to_number(homestand['total_revenue_indicator']).sum()):.2f}",
    "PASS"
)

add_check(
    checks,
    "average_homestand_total_value_index",
    "Report average homestand total value index",
    "Review only",
    f"{float(to_number(homestand['homestand_total_value_index']).mean()):.2f}",
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