import csv
from pathlib import Path
from collections import Counter

merch_path = Path("data/synthetic/merch_transactions.csv")
games_path = Path("data/processed/games_clean.csv")
fans_path = Path("data/synthetic/fans.csv")
output_path = Path("data/synthetic/merch_quality_summary.csv")

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

merch = read_csv(merch_path)
games = read_csv(games_path)
fans = read_csv(fans_path)

game_ids = {row["game_id"] for row in games}
fan_ids = {row["fan_id"] for row in fans}

checks = []

add_check(
    checks,
    "merch_transaction_rows",
    "Count merch transaction rows",
    "> 0",
    str(len(merch)),
    "PASS" if len(merch) > 0 else "FAIL"
)

transaction_ids = [row["merch_transaction_id"] for row in merch]

duplicate_transaction_ids = [
    transaction_id for transaction_id, count in Counter(transaction_ids).items() if count > 1
]

add_check(
    checks,
    "duplicate_merch_transaction_ids",
    "Check duplicate merch_transaction_id values",
    "0",
    str(len(duplicate_transaction_ids)),
    "PASS" if len(duplicate_transaction_ids) == 0 else "FAIL"
)

invalid_game_ids = [
    row for row in merch if row["game_id"] not in game_ids
]

add_check(
    checks,
    "invalid_merch_game_ids",
    "Check merch game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_game_ids)),
    "PASS" if len(invalid_game_ids) == 0 else "FAIL"
)

bad_fan_match_logic = []

for row in merch:
    fan_id = row["fan_id"].strip()
    fan_match_flag = row["fan_match_flag"].strip().lower() == "true"

    if fan_match_flag and fan_id == "":
        bad_fan_match_logic.append(row)

    if not fan_match_flag and fan_id != "":
        bad_fan_match_logic.append(row)

    if fan_id and fan_id not in fan_ids:
        bad_fan_match_logic.append(row)

add_check(
    checks,
    "bad_fan_match_logic",
    "Check fan_match_flag matches fan_id logic",
    "0",
    str(len(bad_fan_match_logic)),
    "PASS" if len(bad_fan_match_logic) == 0 else "FAIL"
)

bad_quantity_values = []

for row in merch:
    try:
        if to_int(row["quantity"]) <= 0:
            bad_quantity_values.append(row)
    except Exception:
        bad_quantity_values.append(row)

add_check(
    checks,
    "bad_merch_quantities",
    "Check merch quantities are positive",
    "0",
    str(len(bad_quantity_values)),
    "PASS" if len(bad_quantity_values) == 0 else "FAIL"
)

bad_revenue_values = []

for row in merch:
    try:
        gross = to_float(row["gross_sales"])
        discount = to_float(row["discount_amount"])
        net = to_float(row["net_sales"])

        if gross < 0 or discount < 0 or net < 0:
            bad_revenue_values.append(row)

        if discount > gross:
            bad_revenue_values.append(row)

        if abs((gross - discount) - net) > 0.02:
            bad_revenue_values.append(row)
    except Exception:
        bad_revenue_values.append(row)

add_check(
    checks,
    "bad_merch_revenue_values",
    "Check merch gross, discount, and net sales logic",
    "0",
    str(len(bad_revenue_values)),
    "PASS" if len(bad_revenue_values) == 0 else "FAIL"
)

valid_boolean_values = {"True", "False", "true", "false", "TRUE", "FALSE"}

bad_boolean_values = []

for row in merch:
    for field in ["promo_related_flag", "fan_match_flag", "synthetic_data_flag"]:
        if row[field] not in valid_boolean_values:
            bad_boolean_values.append((row["merch_transaction_id"], field, row[field]))

add_check(
    checks,
    "boolean_field_values",
    "Check boolean-like merch fields use true/false values",
    "0",
    str(len(bad_boolean_values)),
    "PASS" if len(bad_boolean_values) == 0 else "FAIL"
)

valid_item_categories = {
    "hat",
    "apparel",
    "souvenir",
    "kids",
    "novelty",
    "theme_item",
    "jersey",
    "collectible"
}

invalid_item_categories = [
    row for row in merch if row["item_category"] not in valid_item_categories
]

add_check(
    checks,
    "invalid_item_categories",
    "Check merch item_category values",
    "0",
    str(len(invalid_item_categories)),
    "PASS" if len(invalid_item_categories) == 0 else "FAIL"
)

valid_channels = {
    "stadium_store",
    "kiosk",
    "mobile",
    "online"
}

invalid_channels = [
    row for row in merch if row["channel"] not in valid_channels
]

add_check(
    checks,
    "invalid_channels",
    "Check merch channel values",
    "0",
    str(len(invalid_channels)),
    "PASS" if len(invalid_channels) == 0 else "FAIL"
)

fan_matched_count = sum(1 for row in merch if row["fan_match_flag"].strip().lower() == "true")
fan_match_share = fan_matched_count / len(merch)

add_check(
    checks,
    "fan_match_share",
    "Check merch fan match share",
    "0.60-0.75",
    f"{fan_match_share:.4f}",
    "PASS" if 0.60 <= fan_match_share <= 0.75 else "REVIEW"
)

total_net_sales = sum(to_float(row["net_sales"]) for row in merch)
average_net_sales = total_net_sales / len(merch)

add_check(
    checks,
    "total_merch_net_sales",
    "Report total merch net sales",
    "Review only",
    f"{total_net_sales:.2f}",
    "PASS"
)

add_check(
    checks,
    "average_merch_net_sales_per_transaction",
    "Report average merch net sales per transaction",
    "10-75",
    f"{average_net_sales:.2f}",
    "PASS" if 10 <= average_net_sales <= 75 else "REVIEW"
)

category_counts = Counter(row["item_category"] for row in merch)

for category in sorted(valid_item_categories):
    add_check(
        checks,
        f"item_category_exists_{category}",
        f"Check item category exists: {category}",
        "> 0",
        str(category_counts.get(category, 0)),
        "PASS" if category_counts.get(category, 0) > 0 else "FAIL"
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