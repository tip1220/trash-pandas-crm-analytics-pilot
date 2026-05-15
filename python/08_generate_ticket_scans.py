import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

random.seed(44)

games_path = Path("data/processed/games_clean.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
items_path = Path("data/synthetic/ticket_order_items.csv")
segments_path = Path("data/synthetic/fan_segments.csv")
promotions_path = Path("data/processed/promotions_clean.csv")

output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

scans_path = output_dir / "ticket_scans.csv"
summary_path = output_dir / "ticket_scan_generation_summary.csv"

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def to_int(value):
    return int(float(str(value).strip()))

def to_float(value):
    return float(str(value).strip())

def weighted_choice(options):
    total = sum(weight for _, weight in options)
    roll = random.uniform(0, total)
    current = 0

    for value, weight in options:
        current += weight
        if roll <= current:
            return value

    return options[-1][0]

def parse_game_datetime(game_date, start_time, day_of_week):
    if start_time:
        hour, minute = [int(part) for part in start_time.split(":")]
    elif day_of_week == "Sunday":
        hour, minute = 14, 35
    else:
        hour, minute = 18, 35

    return datetime.strptime(game_date, "%Y-%m-%d").replace(hour=hour, minute=minute)

def scan_probability(order, item, game, fan_segments, promo_categories):
    ticket_type = order["ticket_type"]
    day = game["day_of_week"]

    if ticket_type == "season_ticket":
        probability = 0.78
    elif ticket_type == "mini_plan":
        probability = 0.84
    elif ticket_type == "premium":
        probability = 0.88
    elif ticket_type == "comp":
        probability = 0.68
    else:
        probability = 0.86

    if day in ["Friday", "Saturday"]:
        probability += 0.04

    if day in ["Tuesday", "Wednesday"]:
        probability -= 0.04

    if "fireworks" in promo_categories:
        probability += 0.05

    if "family" in promo_categories:
        probability += 0.03

    if "bobblehead_giveaway" in promo_categories or "jersey_giveaway" in promo_categories:
        probability += 0.04

    if "Season Ticket Holder" in fan_segments:
        probability -= 0.04

    if "Lapsed Fan" in fan_segments:
        probability -= 0.10

    if "Family Buyer" in fan_segments and day in ["Friday", "Saturday", "Sunday"]:
        probability += 0.03

    if "High In-Park Spender" in fan_segments:
        probability += 0.02

    if item["section_type"] in ["premium", "club"]:
        probability += 0.03

    return max(0.50, min(0.97, probability))

def scan_time_for_game(game_start_datetime):
    offset_minutes = weighted_choice([
        (-45, 0.05),
        (-35, 0.10),
        (-25, 0.18),
        (-15, 0.24),
        (-5, 0.20),
        (5, 0.13),
        (15, 0.07),
        (30, 0.03)
    ])

    jitter = random.randint(-4, 4)
    return game_start_datetime + timedelta(minutes=offset_minutes + jitter)

games = read_csv(games_path)
orders = read_csv(orders_path)
items = read_csv(items_path)
segments = read_csv(segments_path)
promotions = read_csv(promotions_path)

games_by_id = {row["game_id"]: row for row in games}
orders_by_id = {row["order_id"]: row for row in orders}

segments_by_fan = {}

for row in segments:
    segments_by_fan.setdefault(row["fan_id"], set()).add(row["segment_name"])

promo_categories_by_game = {}

for row in promotions:
    promo_categories_by_game.setdefault(row["game_id"], set()).add(row["promo_category"])

scan_rows = []
scan_counter = 1

for item in items:
    order = orders_by_id[item["order_id"]]
    game = games_by_id[item["game_id"]]
    fan_segments = segments_by_fan.get(item["fan_id"], set())
    promo_categories = promo_categories_by_game.get(item["game_id"], set())

    ticket_quantity = to_int(item["ticket_quantity"])
    probability = scan_probability(order, item, game, fan_segments, promo_categories)

    scanned_ticket_quantity = 0

    for _ in range(ticket_quantity):
        if random.random() < probability:
            scanned_ticket_quantity += 1

    no_show_ticket_quantity = ticket_quantity - scanned_ticket_quantity

    if scanned_ticket_quantity == ticket_quantity:
        scan_status = "scanned"
        no_show_flag = False
    elif scanned_ticket_quantity == 0:
        scan_status = "not_scanned"
        no_show_flag = True
    else:
        scan_status = "partial_scanned"
        no_show_flag = True

    game_start_datetime = parse_game_datetime(
        game["game_date"],
        game["start_time"],
        game["day_of_week"]
    )

    scan_time = ""
    gate = ""

    if scanned_ticket_quantity > 0:
        scan_time = scan_time_for_game(game_start_datetime).strftime("%Y-%m-%d %H:%M:%S")
        gate = weighted_choice([
            ("Main Gate", 0.46),
            ("Third Base Gate", 0.20),
            ("First Base Gate", 0.18),
            ("Outfield Gate", 0.10),
            ("Suite/Premium Entrance", 0.06)
        ])

    if order["ticket_type"] == "comp":
        match_confidence = random.randint(72, 92)
    elif order["purchase_channel"] in ["online", "mobile", "online_account_manager"]:
        match_confidence = random.randint(88, 100)
    elif order["purchase_channel"] in ["account_rep", "phone"]:
        match_confidence = random.randint(82, 98)
    else:
        match_confidence = random.randint(70, 94)

    scan_rows.append({
        "scan_id": f"SCAN_{scan_counter:09d}",
        "order_item_id": item["order_item_id"],
        "order_id": item["order_id"],
        "game_id": item["game_id"],
        "fan_id": item["fan_id"],
        "ticket_quantity": ticket_quantity,
        "scanned_ticket_quantity": scanned_ticket_quantity,
        "no_show_ticket_quantity": no_show_ticket_quantity,
        "scan_status": scan_status,
        "scan_time": scan_time,
        "gate": gate,
        "no_show_flag": no_show_flag,
        "scan_match_confidence": match_confidence,
        "synthetic_data_flag": True
    })

    scan_counter += 1

scan_fields = [
    "scan_id",
    "order_item_id",
    "order_id",
    "game_id",
    "fan_id",
    "ticket_quantity",
    "scanned_ticket_quantity",
    "no_show_ticket_quantity",
    "scan_status",
    "scan_time",
    "gate",
    "no_show_flag",
    "scan_match_confidence",
    "synthetic_data_flag"
]

write_csv(scans_path, scan_rows, scan_fields)

total_ticket_quantity = sum(to_int(row["ticket_quantity"]) for row in scan_rows)
total_scanned_quantity = sum(to_int(row["scanned_ticket_quantity"]) for row in scan_rows)
total_no_show_quantity = sum(to_int(row["no_show_ticket_quantity"]) for row in scan_rows)

scan_status_counts = {}

for row in scan_rows:
    scan_status_counts[row["scan_status"]] = scan_status_counts.get(row["scan_status"], 0) + 1

summary_rows = [
    {"metric": "ticket_scan_rows", "value": len(scan_rows)},
    {"metric": "total_ticket_quantity", "value": total_ticket_quantity},
    {"metric": "total_scanned_ticket_quantity", "value": total_scanned_quantity},
    {"metric": "total_no_show_ticket_quantity", "value": total_no_show_quantity},
    {"metric": "overall_scan_rate", "value": f"{total_scanned_quantity / total_ticket_quantity:.4f}"},
    {"metric": "overall_no_show_rate", "value": f"{total_no_show_quantity / total_ticket_quantity:.4f}"}
]

for status, count in sorted(scan_status_counts.items()):
    summary_rows.append({"metric": f"scan_status_count_{status}", "value": count})

write_csv(summary_path, summary_rows, ["metric", "value"])

print(f"Wrote {scans_path} with {len(scan_rows)} scan rows")
print(f"Total ticket quantity: {total_ticket_quantity}")
print(f"Total scanned ticket quantity: {total_scanned_quantity}")
print(f"Total no-show ticket quantity: {total_no_show_quantity}")
print(f"Overall scan rate: {total_scanned_quantity / total_ticket_quantity:.4f}")
print(f"Wrote {summary_path}")