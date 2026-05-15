import csv
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

games_path = Path("data/processed/games_clean.csv")
fans_path = Path("data/synthetic/fans.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
items_path = Path("data/synthetic/ticket_order_items.csv")
output_path = Path("data/synthetic/ticket_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def to_int(value):
    return int(float(str(value).strip()))

def to_float(value):
    return float(str(value).strip())

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

games = read_csv(games_path)
fans = read_csv(fans_path)
orders = read_csv(orders_path)
items = read_csv(items_path)

game_ids = {row["game_id"] for row in games}
fan_ids = {row["fan_id"] for row in fans}

game_dates = {
    row["game_id"]: parse_date(row["game_date"])
    for row in games
}

checks = []

def add_check(check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

order_count = len(orders)
item_count = len(items)

add_check(
    "ticket_order_rows",
    "Count ticket order rows",
    "> 0",
    str(order_count),
    "PASS" if order_count > 0 else "FAIL"
)

add_check(
    "ticket_order_item_rows",
    "Count ticket order item rows",
    "> 0",
    str(item_count),
    "PASS" if item_count > 0 else "FAIL"
)

order_ids = [row["order_id"] for row in orders]
item_ids = [row["order_item_id"] for row in items]

duplicate_order_ids = [
    order_id for order_id, count in Counter(order_ids).items() if count > 1
]

duplicate_item_ids = [
    item_id for item_id, count in Counter(item_ids).items() if count > 1
]

add_check(
    "duplicate_order_ids",
    "Check duplicate order_id values",
    "0",
    str(len(duplicate_order_ids)),
    "PASS" if len(duplicate_order_ids) == 0 else "FAIL"
)

add_check(
    "duplicate_order_item_ids",
    "Check duplicate order_item_id values",
    "0",
    str(len(duplicate_item_ids)),
    "PASS" if len(duplicate_item_ids) == 0 else "FAIL"
)

order_id_set = set(order_ids)

invalid_order_game_ids = [
    row for row in orders if row["game_id"] not in game_ids
]

invalid_item_game_ids = [
    row for row in items if row["game_id"] not in game_ids
]

invalid_order_fan_ids = [
    row for row in orders if row["fan_id"] not in fan_ids
]

invalid_item_fan_ids = [
    row for row in items if row["fan_id"] not in fan_ids
]

invalid_item_order_ids = [
    row for row in items if row["order_id"] not in order_id_set
]

add_check(
    "invalid_order_game_ids",
    "Check all ticket order game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_order_game_ids)),
    "PASS" if len(invalid_order_game_ids) == 0 else "FAIL"
)

add_check(
    "invalid_item_game_ids",
    "Check all ticket order item game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_item_game_ids)),
    "PASS" if len(invalid_item_game_ids) == 0 else "FAIL"
)

add_check(
    "invalid_order_fan_ids",
    "Check all ticket order fan_id values exist in fans.csv",
    "0",
    str(len(invalid_order_fan_ids)),
    "PASS" if len(invalid_order_fan_ids) == 0 else "FAIL"
)

add_check(
    "invalid_item_fan_ids",
    "Check all ticket order item fan_id values exist in fans.csv",
    "0",
    str(len(invalid_item_fan_ids)),
    "PASS" if len(invalid_item_fan_ids) == 0 else "FAIL"
)

add_check(
    "invalid_item_order_ids",
    "Check all ticket order item order_id values exist in ticket_orders.csv",
    "0",
    str(len(invalid_item_order_ids)),
    "PASS" if len(invalid_item_order_ids) == 0 else "FAIL"
)

orders_per_game = Counter(row["game_id"] for row in orders)
games_without_orders = [
    game_id for game_id in game_ids if orders_per_game.get(game_id, 0) == 0
]

add_check(
    "games_without_ticket_orders",
    "Check every game has ticket orders",
    "0",
    str(len(games_without_orders)),
    "PASS" if len(games_without_orders) == 0 else "FAIL"
)

bad_order_dates = []

for row in orders:
    try:
        order_date = parse_date(row["order_date"])
        game_date = game_dates[row["game_id"]]
        if order_date > game_date:
            bad_order_dates.append(row)
    except Exception:
        bad_order_dates.append(row)

add_check(
    "bad_order_dates",
    "Check order_date is not after game_date",
    "0",
    str(len(bad_order_dates)),
    "PASS" if len(bad_order_dates) == 0 else "FAIL"
)

bad_quantities = []

for row in orders:
    try:
        if to_int(row["ticket_quantity"]) <= 0:
            bad_quantities.append(row)
    except Exception:
        bad_quantities.append(row)

for row in items:
    try:
        if to_int(row["ticket_quantity"]) <= 0:
            bad_quantities.append(row)
    except Exception:
        bad_quantities.append(row)

add_check(
    "bad_ticket_quantities",
    "Check ticket quantities are positive",
    "0",
    str(len(bad_quantities)),
    "PASS" if len(bad_quantities) == 0 else "FAIL"
)

bad_revenue_values = []

for row in orders:
    try:
        gross = to_float(row["gross_ticket_revenue"])
        discount = to_float(row["discount_amount"])
        net = to_float(row["net_ticket_revenue"])
        if gross < 0 or discount < 0 or net < 0:
            bad_revenue_values.append(row)
        if discount > gross:
            bad_revenue_values.append(row)
        if abs((gross - discount) - net) > 0.02:
            bad_revenue_values.append(row)
    except Exception:
        bad_revenue_values.append(row)

add_check(
    "bad_order_revenue_values",
    "Check gross, discount, and net ticket revenue logic",
    "0",
    str(len(bad_revenue_values)),
    "PASS" if len(bad_revenue_values) == 0 else "FAIL"
)

item_rollup = defaultdict(lambda: {"quantity": 0, "net": 0.0})

for row in items:
    item_rollup[row["order_id"]]["quantity"] += to_int(row["ticket_quantity"])
    item_rollup[row["order_id"]]["net"] += to_float(row["net_ticket_revenue"])

bad_order_item_rollups = []

for row in orders:
    order_id = row["order_id"]
    order_quantity = to_int(row["ticket_quantity"])
    order_net = to_float(row["net_ticket_revenue"])

    item_quantity = item_rollup[order_id]["quantity"]
    item_net = item_rollup[order_id]["net"]

    if order_quantity != item_quantity:
        bad_order_item_rollups.append(row)

    if abs(order_net - item_net) > 0.02:
        bad_order_item_rollups.append(row)

add_check(
    "order_item_rollup_mismatches",
    "Check item quantity and net revenue roll up to order",
    "0",
    str(len(bad_order_item_rollups)),
    "PASS" if len(bad_order_item_rollups) == 0 else "FAIL"
)

valid_boolean_values = {"True", "False", "true", "false", "TRUE", "FALSE"}

order_boolean_fields = [
    "group_order_flag",
    "premium_flag",
    "synthetic_data_flag"
]

item_boolean_fields = [
    "synthetic_data_flag"
]

bad_boolean_values = []

for row in orders:
    for field in order_boolean_fields:
        if row[field] not in valid_boolean_values:
            bad_boolean_values.append((row["order_id"], field, row[field]))

for row in items:
    for field in item_boolean_fields:
        if row[field] not in valid_boolean_values:
            bad_boolean_values.append((row["order_item_id"], field, row[field]))

add_check(
    "boolean_field_values",
    "Check boolean-like fields use true/false values",
    "0 invalid values",
    str(len(bad_boolean_values)),
    "PASS" if len(bad_boolean_values) == 0 else "FAIL"
)

ticket_type_counts = Counter(row["ticket_type"] for row in orders)

required_ticket_types = [
    "single_game",
    "mini_plan",
    "season_ticket",
    "premium",
    "comp"
]

for ticket_type in required_ticket_types:
    actual = ticket_type_counts.get(ticket_type, 0)
    add_check(
        f"ticket_type_exists_{ticket_type}",
        f"Check ticket type exists: {ticket_type}",
        "> 0",
        str(actual),
        "PASS" if actual > 0 else "FAIL"
    )

tickets_by_game = defaultdict(int)

for row in orders:
    tickets_by_game[row["game_id"]] += to_int(row["ticket_quantity"])

low_ticket_games = {
    game_id: qty for game_id, qty in tickets_by_game.items() if qty < 2500
}

high_ticket_games = {
    game_id: qty for game_id, qty in tickets_by_game.items() if qty > 8000
}

add_check(
    "low_ticket_games",
    "Check games with unusually low synthetic tickets sold",
    "0 below 2500",
    str(len(low_ticket_games)),
    "REVIEW" if len(low_ticket_games) > 0 else "PASS"
)

add_check(
    "high_ticket_games",
    "Check games with unusually high synthetic tickets sold",
    "0 above 8000",
    str(len(high_ticket_games)),
    "REVIEW" if len(high_ticket_games) > 0 else "PASS"
)

total_ticket_quantity = sum(to_int(row["ticket_quantity"]) for row in orders)
total_net_ticket_revenue = sum(to_float(row["net_ticket_revenue"]) for row in orders)

add_check(
    "total_ticket_quantity",
    "Report total synthetic ticket quantity",
    "Review only",
    str(total_ticket_quantity),
    "PASS"
)

add_check(
    "total_net_ticket_revenue",
    "Report total synthetic net ticket revenue",
    "Review only",
    f"{total_net_ticket_revenue:.2f}",
    "PASS"
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