import csv
import random
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta

random.seed(47)

games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
segments_path = Path("data/synthetic/fan_segments.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")

output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

concessions_path = output_dir / "concession_transactions.csv"
summary_path = output_dir / "concession_generation_summary.csv"

fan_match_rate = 0.46

stand_categories = [
    ("main_stand", 0.42),
    ("portable", 0.22),
    ("beverage", 0.16),
    ("dessert", 0.10),
    ("premium_area", 0.10)
]

item_categories = [
    ("food", 0.34),
    ("beverage", 0.28),
    ("snack", 0.16),
    ("family_item", 0.10),
    ("dessert", 0.08),
    ("premium_item", 0.04)
]

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

def weighted_choice(options):
    total = sum(weight for _, weight in options)
    roll = random.uniform(0, total)
    current = 0

    for value, weight in options:
        current += weight
        if roll <= current:
            return value

    return options[-1][0]

def game_datetime(game_date, day_of_week, start_time):
    if start_time:
        hour, minute = [int(part) for part in start_time.split(":")]
    elif day_of_week == "Sunday":
        hour, minute = 14, 35
    else:
        hour, minute = 18, 35

    return datetime.strptime(game_date, "%Y-%m-%d").replace(hour=hour, minute=minute)

def transaction_time(game):
    start = game_datetime(game["game_date"], game["day_of_week"], game["start_time"])

    offset = weighted_choice([
        (-25, 0.07),
        (-10, 0.10),
        (10, 0.18),
        (25, 0.24),
        (45, 0.22),
        (65, 0.13),
        (90, 0.06)
    ])

    jitter = random.randint(-5, 5)
    return start + timedelta(minutes=offset + jitter)

def concession_purchase_rate(game, promo_categories):
    rate = 0.23

    if game["day_of_week"] in ["Friday", "Saturday"]:
        rate += 0.04

    if game["day_of_week"] == "Sunday":
        rate += 0.03

    if "fireworks" in promo_categories:
        rate += 0.03

    if "family" in promo_categories:
        rate += 0.04

    if "weekly_promo" in promo_categories:
        rate += 0.02

    return max(0.16, min(0.38, rate))

def choose_item_category(fan_segments, promo_categories):
    adjusted = list(item_categories)

    if "Family Buyer" in fan_segments:
        adjusted.extend([
            ("family_item", 0.12),
            ("snack", 0.06),
            ("dessert", 0.05)
        ])

    if "High In-Park Spender" in fan_segments:
        adjusted.extend([
            ("premium_item", 0.08),
            ("beverage", 0.05),
            ("food", 0.04)
        ])

    if "family" in promo_categories:
        adjusted.extend([
            ("family_item", 0.08),
            ("dessert", 0.04)
        ])

    return weighted_choice(adjusted)

def choose_stand_category(item_category):
    if item_category == "beverage":
        return weighted_choice([
            ("beverage", 0.48),
            ("main_stand", 0.24),
            ("portable", 0.18),
            ("premium_area", 0.10)
        ])

    if item_category == "dessert":
        return weighted_choice([
            ("dessert", 0.58),
            ("portable", 0.22),
            ("main_stand", 0.16),
            ("premium_area", 0.04)
        ])

    if item_category == "premium_item":
        return weighted_choice([
            ("premium_area", 0.52),
            ("main_stand", 0.24),
            ("portable", 0.16),
            ("beverage", 0.08)
        ])

    return weighted_choice(stand_categories)

def price_for_item(item_category):
    if item_category == "premium_item":
        return round(random.uniform(18, 36), 2)

    if item_category == "food":
        return round(random.uniform(9, 18), 2)

    if item_category == "beverage":
        return round(random.uniform(5, 14), 2)

    if item_category == "family_item":
        return round(random.uniform(14, 28), 2)

    if item_category == "dessert":
        return round(random.uniform(6, 13), 2)

    return round(random.uniform(4, 11), 2)

games = read_csv(games_path)
promotions = read_csv(promotions_path)
segments = read_csv(segments_path)
scans = read_csv(scans_path)

promo_categories_by_game = defaultdict(set)

for row in promotions:
    promo_categories_by_game[row["game_id"]].add(row["promo_category"])

segments_by_fan = defaultdict(set)

for row in segments:
    segments_by_fan[row["fan_id"]].add(row["segment_name"])

scanned_fans_by_game = defaultdict(list)
scanned_ticket_qty_by_game = defaultdict(int)

for row in scans:
    scanned_qty = to_int(row["scanned_ticket_quantity"])

    if scanned_qty <= 0:
        continue

    game_id = row["game_id"]
    fan_id = row["fan_id"]

    scanned_ticket_qty_by_game[game_id] += scanned_qty

    for _ in range(min(scanned_qty, 8)):
        scanned_fans_by_game[game_id].append(fan_id)

concession_rows = []
transaction_counter = 1

for game in games:
    game_id = game["game_id"]
    scanned_qty = scanned_ticket_qty_by_game.get(game_id, 0)

    if scanned_qty <= 0:
        continue

    promo_categories = promo_categories_by_game.get(game_id, set())
    rate = concession_purchase_rate(game, promo_categories)

    transaction_count = int(scanned_qty * rate * random.uniform(0.88, 1.12))

    if transaction_count < 15:
        transaction_count = random.randint(15, 30)

    available_fans = scanned_fans_by_game.get(game_id, [])

    for _ in range(transaction_count):
        matched_to_fan = random.random() < fan_match_rate and len(available_fans) > 0
        fan_id = random.choice(available_fans) if matched_to_fan else ""
        fan_segments = segments_by_fan.get(fan_id, set()) if fan_id else set()

        item_category = choose_item_category(fan_segments, promo_categories)
        stand_category = choose_stand_category(item_category)

        if item_category == "family_item":
            quantity = weighted_choice([(1, 0.55), (2, 0.30), (3, 0.10), (4, 0.05)])
        elif item_category == "snack":
            quantity = weighted_choice([(1, 0.62), (2, 0.26), (3, 0.08), (4, 0.04)])
        else:
            quantity = weighted_choice([(1, 0.70), (2, 0.22), (3, 0.06), (4, 0.02)])

        unit_price = price_for_item(item_category)
        gross_sales = round(unit_price * quantity, 2)

        if item_category in ["family_item", "snack"]:
            discount_rate = random.uniform(0.00, 0.10)
        elif item_category == "premium_item":
            discount_rate = random.uniform(0.00, 0.04)
        else:
            discount_rate = random.uniform(0.00, 0.07)

        discount_amount = round(gross_sales * discount_rate, 2)
        net_sales = round(gross_sales - discount_amount, 2)

        timestamp = transaction_time(game)

        concession_rows.append({
            "concession_transaction_id": f"CONC_{transaction_counter:08d}",
            "game_id": game_id,
            "fan_id": fan_id,
            "transaction_date": timestamp.date().isoformat(),
            "transaction_time": timestamp.strftime("%H:%M:%S"),
            "stand_category": stand_category,
            "item_category": item_category,
            "quantity": quantity,
            "gross_sales": f"{gross_sales:.2f}",
            "discount_amount": f"{discount_amount:.2f}",
            "net_sales": f"{net_sales:.2f}",
            "fan_match_flag": matched_to_fan,
            "synthetic_data_flag": True
        })

        transaction_counter += 1

fields = [
    "concession_transaction_id",
    "game_id",
    "fan_id",
    "transaction_date",
    "transaction_time",
    "stand_category",
    "item_category",
    "quantity",
    "gross_sales",
    "discount_amount",
    "net_sales",
    "fan_match_flag",
    "synthetic_data_flag"
]

write_csv(concessions_path, concession_rows, fields)

total_net_sales = sum(float(row["net_sales"]) for row in concession_rows)
fan_matched_count = sum(1 for row in concession_rows if str(row["fan_match_flag"]).lower() == "true")
fan_match_share = fan_matched_count / len(concession_rows)

item_counts = Counter(row["item_category"] for row in concession_rows)
stand_counts = Counter(row["stand_category"] for row in concession_rows)

summary_rows = [
    {"metric": "concession_transaction_rows", "value": len(concession_rows)},
    {"metric": "total_concession_net_sales", "value": f"{total_net_sales:.2f}"},
    {"metric": "fan_matched_concession_transactions", "value": fan_matched_count},
    {"metric": "fan_match_share", "value": f"{fan_match_share:.4f}"},
    {"metric": "average_net_sales_per_transaction", "value": f"{total_net_sales / len(concession_rows):.2f}"}
]

for item_category, count in sorted(item_counts.items()):
    summary_rows.append({"metric": f"item_category_count_{item_category}", "value": count})

for stand_category, count in sorted(stand_counts.items()):
    summary_rows.append({"metric": f"stand_category_count_{stand_category}", "value": count})

write_csv(summary_path, summary_rows, ["metric", "value"])

print(f"Wrote {concessions_path} with {len(concession_rows)} transactions")
print(f"Total concession net sales: {total_net_sales:.2f}")
print(f"Fan match share: {fan_match_share:.4f}")
print(f"Wrote {summary_path}")