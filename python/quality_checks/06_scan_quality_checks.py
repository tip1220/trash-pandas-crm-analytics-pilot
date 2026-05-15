import csv
from pathlib import Path
from collections import Counter

items_path = Path("data/synthetic/ticket_order_items.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")
games_path = Path("data/processed/games_clean.csv")
fans_path = Path("data/synthetic/fans.csv")
output_path = Path("data/synthetic/scan_quality_summary.csv")

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

print("Loading reference files...")

items = read_csv(items_path)
orders = read_csv(orders_path)
games = read_csv(games_path)
fans = read_csv(fans_path)

item_ids = set()
item_quantity_by_id = {}

for row in items:
    item_ids.add(row["order_item_id"])
    item_quantity_by_id[row["order_item_id"]] = to_int(row["ticket_quantity"])

order_ids = {row["order_id"] for row in orders}
game_ids = {row["game_id"] for row in games}
fan_ids = {row["fan_id"] for row in fans}

print("Checking scan file...")

checks = []

scan_count = 0
scan_ids = set()
scan_order_item_ids = set()

duplicate_scan_ids = 0
duplicate_scan_order_item_ids = 0
invalid_order_item_ids = 0
invalid_order_ids = 0
invalid_game_ids = 0
invalid_fan_ids = 0
bad_quantity_logic = 0
scan_item_quantity_mismatches = 0
invalid_scan_statuses = 0
bad_scan_status_logic = 0
bad_boolean_values = 0
bad_no_show_flag_logic = 0
bad_scan_time_logic = 0
bad_gate_logic = 0
bad_scan_match_confidence = 0

total_ticket_quantity = 0
total_scanned_quantity = 0
total_no_show_quantity = 0

status_counts = Counter()
game_ticket_totals = Counter()
game_scanned_totals = Counter()

valid_scan_statuses = {"scanned", "not_scanned", "partial_scanned"}
valid_boolean_values = {"True", "False", "true", "false", "TRUE", "FALSE"}

with scans_path.open("r", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        scan_count += 1

        scan_id = row["scan_id"]
        order_item_id = row["order_item_id"]
        order_id = row["order_id"]
        game_id = row["game_id"]
        fan_id = row["fan_id"]
        scan_status = row["scan_status"]

        if scan_id in scan_ids:
            duplicate_scan_ids += 1
        scan_ids.add(scan_id)

        if order_item_id in scan_order_item_ids:
            duplicate_scan_order_item_ids += 1
        scan_order_item_ids.add(order_item_id)

        if order_item_id not in item_ids:
            invalid_order_item_ids += 1

        if order_id not in order_ids:
            invalid_order_ids += 1

        if game_id not in game_ids:
            invalid_game_ids += 1

        if fan_id not in fan_ids:
            invalid_fan_ids += 1

        try:
            ticket_quantity = to_int(row["ticket_quantity"])
            scanned_quantity = to_int(row["scanned_ticket_quantity"])
            no_show_quantity = to_int(row["no_show_ticket_quantity"])

            total_ticket_quantity += ticket_quantity
            total_scanned_quantity += scanned_quantity
            total_no_show_quantity += no_show_quantity

            game_ticket_totals[game_id] += ticket_quantity
            game_scanned_totals[game_id] += scanned_quantity

            if ticket_quantity <= 0:
                bad_quantity_logic += 1

            if scanned_quantity < 0 or no_show_quantity < 0:
                bad_quantity_logic += 1

            if scanned_quantity + no_show_quantity != ticket_quantity:
                bad_quantity_logic += 1

            if scanned_quantity > ticket_quantity or no_show_quantity > ticket_quantity:
                bad_quantity_logic += 1

            if order_item_id in item_quantity_by_id:
                if ticket_quantity != item_quantity_by_id[order_item_id]:
                    scan_item_quantity_mismatches += 1

            if scan_status not in valid_scan_statuses:
                invalid_scan_statuses += 1

            if scanned_quantity == ticket_quantity and scan_status != "scanned":
                bad_scan_status_logic += 1

            if scanned_quantity == 0 and scan_status != "not_scanned":
                bad_scan_status_logic += 1

            if scanned_quantity > 0 and no_show_quantity > 0 and scan_status != "partial_scanned":
                bad_scan_status_logic += 1

            no_show_flag = row["no_show_flag"].strip().lower() == "true"

            if row["no_show_flag"] not in valid_boolean_values:
                bad_boolean_values += 1

            if row["synthetic_data_flag"] not in valid_boolean_values:
                bad_boolean_values += 1

            if no_show_quantity > 0 and not no_show_flag:
                bad_no_show_flag_logic += 1

            if no_show_quantity == 0 and no_show_flag:
                bad_no_show_flag_logic += 1

            scan_time = row["scan_time"].strip()
            gate = row["gate"].strip()

            if scanned_quantity > 0 and scan_time == "":
                bad_scan_time_logic += 1

            if scanned_quantity == 0 and scan_time != "":
                bad_scan_time_logic += 1

            if scanned_quantity > 0 and gate == "":
                bad_gate_logic += 1

            if scanned_quantity == 0 and gate != "":
                bad_gate_logic += 1

            confidence = to_float(row["scan_match_confidence"])

            if confidence < 0 or confidence > 100:
                bad_scan_match_confidence += 1

        except Exception:
            bad_quantity_logic += 1

        status_counts[scan_status] += 1

missing_scan_rows_for_order_items = len(item_ids - scan_order_item_ids)

overall_scan_rate = total_scanned_quantity / total_ticket_quantity
overall_no_show_rate = total_no_show_quantity / total_ticket_quantity

low_game_scan_rates = 0
high_game_scan_rates = 0

for game_id, ticket_total in game_ticket_totals.items():
    if ticket_total == 0:
        continue

    rate = game_scanned_totals[game_id] / ticket_total

    if rate < 0.70:
        low_game_scan_rates += 1

    if rate > 0.97:
        high_game_scan_rates += 1

add_check(checks, "ticket_scan_rows", "Count ticket scan rows", str(len(items)), str(scan_count), "PASS" if scan_count == len(items) else "FAIL")
add_check(checks, "duplicate_scan_ids", "Check duplicate scan_id values", "0", str(duplicate_scan_ids), "PASS" if duplicate_scan_ids == 0 else "FAIL")
add_check(checks, "duplicate_scan_order_item_ids", "Check each order_item_id has only one scan row", "0", str(duplicate_scan_order_item_ids), "PASS" if duplicate_scan_order_item_ids == 0 else "FAIL")
add_check(checks, "missing_scan_rows_for_order_items", "Check every ticket order item has a scan row", "0", str(missing_scan_rows_for_order_items), "PASS" if missing_scan_rows_for_order_items == 0 else "FAIL")
add_check(checks, "invalid_scan_order_item_ids", "Check scan order_item_id values exist in ticket_order_items.csv", "0", str(invalid_order_item_ids), "PASS" if invalid_order_item_ids == 0 else "FAIL")
add_check(checks, "invalid_scan_order_ids", "Check scan order_id values exist in ticket_orders.csv", "0", str(invalid_order_ids), "PASS" if invalid_order_ids == 0 else "FAIL")
add_check(checks, "invalid_scan_game_ids", "Check scan game_id values exist in games_clean.csv", "0", str(invalid_game_ids), "PASS" if invalid_game_ids == 0 else "FAIL")
add_check(checks, "invalid_scan_fan_ids", "Check scan fan_id values exist in fans.csv", "0", str(invalid_fan_ids), "PASS" if invalid_fan_ids == 0 else "FAIL")
add_check(checks, "bad_scan_quantity_logic", "Check scan quantity logic", "0", str(bad_quantity_logic), "PASS" if bad_quantity_logic == 0 else "FAIL")
add_check(checks, "scan_item_quantity_mismatches", "Check scan ticket quantity matches order item ticket quantity", "0", str(scan_item_quantity_mismatches), "PASS" if scan_item_quantity_mismatches == 0 else "FAIL")
add_check(checks, "invalid_scan_statuses", "Check scan_status values", "0", str(invalid_scan_statuses), "PASS" if invalid_scan_statuses == 0 else "FAIL")
add_check(checks, "bad_scan_status_logic", "Check scan_status matches scanned and no-show quantities", "0", str(bad_scan_status_logic), "PASS" if bad_scan_status_logic == 0 else "FAIL")
add_check(checks, "boolean_field_values", "Check boolean-like scan fields use true/false values", "0", str(bad_boolean_values), "PASS" if bad_boolean_values == 0 else "FAIL")
add_check(checks, "bad_no_show_flag_logic", "Check no_show_flag matches no_show_ticket_quantity", "0", str(bad_no_show_flag_logic), "PASS" if bad_no_show_flag_logic == 0 else "FAIL")
add_check(checks, "bad_scan_time_logic", "Check scan_time exists only when scanned", "0", str(bad_scan_time_logic), "PASS" if bad_scan_time_logic == 0 else "FAIL")
add_check(checks, "bad_gate_logic", "Check gate exists only when scanned", "0", str(bad_gate_logic), "PASS" if bad_gate_logic == 0 else "FAIL")
add_check(checks, "bad_scan_match_confidence", "Check scan_match_confidence is between 0 and 100", "0", str(bad_scan_match_confidence), "PASS" if bad_scan_match_confidence == 0 else "FAIL")
add_check(checks, "overall_scan_rate", "Report overall scan rate", "0.75-0.93", f"{overall_scan_rate:.4f}", "PASS" if 0.75 <= overall_scan_rate <= 0.93 else "REVIEW")
add_check(checks, "overall_no_show_rate", "Report overall no-show rate", "0.07-0.25", f"{overall_no_show_rate:.4f}", "PASS" if 0.07 <= overall_no_show_rate <= 0.25 else "REVIEW")
add_check(checks, "low_game_scan_rates", "Check games with unusually low scan rates", "0 below 0.70", str(low_game_scan_rates), "REVIEW" if low_game_scan_rates > 0 else "PASS")
add_check(checks, "high_game_scan_rates", "Check games with unusually high scan rates", "0 above 0.97", str(high_game_scan_rates), "REVIEW" if high_game_scan_rates > 0 else "PASS")

for status in sorted(valid_scan_statuses):
    add_check(checks, f"scan_status_count_{status}", f"Report scan status count: {status}", "Review only", str(status_counts.get(status, 0)), "PASS")

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