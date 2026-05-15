import csv
from pathlib import Path
from collections import Counter

accounts_path = Path("data/synthetic/group_accounts.csv")
group_sales_path = Path("data/synthetic/group_sales.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
games_path = Path("data/processed/games_clean.csv")
output_path = Path("data/synthetic/group_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def to_int(value):
    return int(float(str(value).strip()))

def to_float(value):
    return float(str(value).strip())

def add_check(checks, check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

accounts = read_csv(accounts_path)
group_sales = read_csv(group_sales_path)
orders = read_csv(orders_path)
games = read_csv(games_path)

account_ids = {row["account_id"] for row in accounts}
order_ids = {row["order_id"] for row in orders}
game_ids = {row["game_id"] for row in games}

orders_by_id = {row["order_id"]: row for row in orders}

checks = []

add_check(
    checks,
    "group_account_rows",
    "Count group account rows",
    "1200",
    str(len(accounts)),
    "PASS" if len(accounts) == 1200 else "FAIL"
)

add_check(
    checks,
    "group_sales_rows",
    "Count group sales rows",
    "3600",
    str(len(group_sales)),
    "PASS" if len(group_sales) == 3600 else "FAIL"
)

duplicate_account_ids = [
    account_id for account_id, count in Counter(row["account_id"] for row in accounts).items() if count > 1
]

duplicate_group_sale_ids = [
    group_sale_id for group_sale_id, count in Counter(row["group_sale_id"] for row in group_sales).items() if count > 1
]

add_check(
    checks,
    "duplicate_account_ids",
    "Check duplicate account_id values",
    "0",
    str(len(duplicate_account_ids)),
    "PASS" if len(duplicate_account_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "duplicate_group_sale_ids",
    "Check duplicate group_sale_id values",
    "0",
    str(len(duplicate_group_sale_ids)),
    "PASS" if len(duplicate_group_sale_ids) == 0 else "FAIL"
)

invalid_group_sale_account_ids = [
    row for row in group_sales if row["account_id"] not in account_ids
]

invalid_group_sale_game_ids = [
    row for row in group_sales if row["game_id"] not in game_ids
]

invalid_group_sale_order_ids = [
    row for row in group_sales if row["order_id"] not in order_ids
]

add_check(
    checks,
    "invalid_group_sale_account_ids",
    "Check group_sales account_id values exist in group_accounts.csv",
    "0",
    str(len(invalid_group_sale_account_ids)),
    "PASS" if len(invalid_group_sale_account_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "invalid_group_sale_game_ids",
    "Check group_sales game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_group_sale_game_ids)),
    "PASS" if len(invalid_group_sale_game_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "invalid_group_sale_order_ids",
    "Check group_sales order_id values exist in ticket_orders.csv",
    "0",
    str(len(invalid_group_sale_order_ids)),
    "PASS" if len(invalid_group_sale_order_ids) == 0 else "FAIL"
)

bad_group_order_links = []

for row in group_sales:
    order = orders_by_id.get(row["order_id"])

    if not order:
        continue

    if order["ticket_type"] != "group":
        bad_group_order_links.append(row)

    if str(order["group_order_flag"]).strip().lower() != "true":
        bad_group_order_links.append(row)

    if order["account_id"] != row["account_id"]:
        bad_group_order_links.append(row)

    if order["game_id"] != row["game_id"]:
        bad_group_order_links.append(row)

    if to_int(order["ticket_quantity"]) != to_int(row["group_ticket_quantity"]):
        bad_group_order_links.append(row)

    if abs(to_float(order["net_ticket_revenue"]) - to_float(row["group_ticket_revenue"])) > 0.02:
        bad_group_order_links.append(row)

add_check(
    checks,
    "bad_group_order_links",
    "Check group sales connect correctly to ticket orders",
    "0",
    str(len(bad_group_order_links)),
    "PASS" if len(bad_group_order_links) == 0 else "FAIL"
)

bad_group_quantities = []

for row in group_sales:
    try:
        quantity = to_int(row["group_ticket_quantity"])

        if quantity <= 0:
            bad_group_quantities.append(row)
    except Exception:
        bad_group_quantities.append(row)

add_check(
    checks,
    "bad_group_ticket_quantities",
    "Check group ticket quantities are positive",
    "0",
    str(len(bad_group_quantities)),
    "PASS" if len(bad_group_quantities) == 0 else "FAIL"
)

bad_group_revenue = []

for row in group_sales:
    try:
        revenue = to_float(row["group_ticket_revenue"])

        if revenue < 0:
            bad_group_revenue.append(row)
    except Exception:
        bad_group_revenue.append(row)

add_check(
    checks,
    "bad_group_revenue",
    "Check group ticket revenue is non-negative",
    "0",
    str(len(bad_group_revenue)),
    "PASS" if len(bad_group_revenue) == 0 else "FAIL"
)

bad_scan_rates = []

for row in group_sales:
    try:
        scan_rate = to_float(row["group_scan_rate"])

        if scan_rate < 0 or scan_rate > 1:
            bad_scan_rates.append(row)
    except Exception:
        bad_scan_rates.append(row)

add_check(
    checks,
    "bad_group_scan_rates",
    "Check group scan rate is between 0 and 1",
    "0",
    str(len(bad_scan_rates)),
    "PASS" if len(bad_scan_rates) == 0 else "FAIL"
)

valid_boolean_values = {"True", "False", "true", "false", "TRUE", "FALSE"}

bad_boolean_values = []

for row in accounts:
    for field in ["corporate_prospect_flag", "synthetic_data_flag"]:
        if row[field] not in valid_boolean_values:
            bad_boolean_values.append((row["account_id"], field, row[field]))

for row in group_sales:
    for field in ["renewal_flag", "upsell_flag", "synthetic_data_flag"]:
        if row[field] not in valid_boolean_values:
            bad_boolean_values.append((row["group_sale_id"], field, row[field]))

add_check(
    checks,
    "boolean_field_values",
    "Check boolean-like group fields use true/false values",
    "0",
    str(len(bad_boolean_values)),
    "PASS" if len(bad_boolean_values) == 0 else "FAIL"
)

account_type_counts = Counter(row["account_type"] for row in accounts)
group_type_counts = Counter(row["group_type"] for row in group_sales)

required_account_types = [
    "corporate",
    "school",
    "church",
    "youth_sports",
    "nonprofit",
    "community_group",
    "local_business",
    "healthcare"
]

for account_type in required_account_types:
    add_check(
        checks,
        f"account_type_exists_{account_type}",
        f"Check account type exists: {account_type}",
        "> 0",
        str(account_type_counts.get(account_type, 0)),
        "PASS" if account_type_counts.get(account_type, 0) > 0 else "FAIL"
    )

for group_type in required_account_types:
    add_check(
        checks,
        f"group_type_exists_{group_type}",
        f"Check group sale type exists: {group_type}",
        "> 0",
        str(group_type_counts.get(group_type, 0)),
        "PASS" if group_type_counts.get(group_type, 0) > 0 else "FAIL"
    )

total_group_tickets = sum(to_int(row["group_ticket_quantity"]) for row in group_sales)
total_group_revenue = sum(to_float(row["group_ticket_revenue"]) for row in group_sales)
average_group_size = total_group_tickets / len(group_sales)
average_group_scan_rate = sum(to_float(row["group_scan_rate"]) for row in group_sales) / len(group_sales)

renewal_count = sum(1 for row in group_sales if str(row["renewal_flag"]).strip().lower() == "true")
upsell_count = sum(1 for row in group_sales if str(row["upsell_flag"]).strip().lower() == "true")

add_check(
    checks,
    "total_group_tickets",
    "Report total group ticket quantity",
    "Review only",
    str(total_group_tickets),
    "PASS"
)

add_check(
    checks,
    "total_group_revenue",
    "Report total group revenue",
    "Review only",
    f"{total_group_revenue:.2f}",
    "PASS"
)

add_check(
    checks,
    "average_group_size",
    "Report average group size",
    "10-120",
    f"{average_group_size:.2f}",
    "PASS" if 10 <= average_group_size <= 120 else "REVIEW"
)

add_check(
    checks,
    "average_group_scan_rate",
    "Report average group scan rate",
    "0.65-0.95",
    f"{average_group_scan_rate:.4f}",
    "PASS" if 0.65 <= average_group_scan_rate <= 0.95 else "REVIEW"
)

add_check(
    checks,
    "renewal_flag_count",
    "Report group renewal opportunity count",
    "> 0",
    str(renewal_count),
    "PASS" if renewal_count > 0 else "REVIEW"
)

add_check(
    checks,
    "upsell_flag_count",
    "Report group upsell opportunity count",
    "> 0",
    str(upsell_count),
    "PASS" if upsell_count > 0 else "REVIEW"
)

with output_path.open("w", newline="") as f:
    fieldnames = ["check_name", "result", "expected", "actual", "status"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(checks)

for check in checks:
    print(f"{check['status']}: {check['check_name']} | expected={check['expected']} | actual={check['actual']}")

fail_count = sum(1 for check in checks if check["status"] == "FAIL")
review_count = sum(1 for check in checks if check["status"] == "REVIEW")

print(f"\nQuality check summary saved to {output_path}")
print(f"FAIL checks: {fail_count}")
print(f"REVIEW checks: {review_count}")

if fail_count > 0:
    raise SystemExit(1)