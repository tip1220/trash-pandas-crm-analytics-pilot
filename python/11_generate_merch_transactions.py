import csv
import random
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta

random.seed(46)

games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
fans_path = Path("data/synthetic/fans.csv")
segments_path = Path("data/synthetic/fan_segments.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")

output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

merch_path = output_dir / "merch_transactions.csv"
summary_path = output_dir / "merch_generation_summary.csv"

fan_match_rate = 0.68

item_categories = [
    ("hat", 0.28),
    ("apparel", 0.22),
    ("souvenir", 0.18),
    ("kids", 0.10),
    ("novelty", 0.09),
    ("theme_item", 0.08),
    ("jersey", 0.04),
    ("collectible", 0.01)
]

channels = [
    ("stadium_store", 0.45),
    ("kiosk", 0.30),
    ("mobile", 0.15),
    ("online", 0.10)
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
        (-35, 0.10),
        (-20, 0.16),
        (-5, 0.20),
        (15, 0.20),
        (35, 0.18),
        (60, 0.10),
        (90, 0.06)
    ])
    jitter = random.randint(-5, 5)
    return start + timedelta(minutes=offset + jitter)

def price_for_item(item_category):
    if item_category == "jersey":
        return round(random.uniform(65, 115), 2)

    if item_category == "apparel":
        return round(random.uniform(24, 55), 2)

    if item_category == "hat":
        return round(random.uniform(22, 42), 2)

    if item_category == "theme_item":
        return round(random.uniform(18, 48), 2)

    if item_category == "collectible":
        return round(random.uniform(16, 38), 2)

    if item_category == "kids":
        return round(random.uniform(10, 28), 2)

    if item_category == "novelty":
        return round(random.uniform(8, 24), 2)

    return round(random.uniform(6, 22), 2)

def merch_purchase_rate(game, promo_categories):
    rate = 0.030

    if game["day_of_week"] in ["Friday", "Saturday"]:
        rate += 0.010

    if game["day_of_week"] == "Sunday":
        rate += 0.006

    if "fireworks" in promo_categories:
        rate += 0.006

    if "family" in promo_categories:
        rate += 0.005

    if "bobblehead_giveaway" in promo_categories:
        rate += 0.012

    if "jersey_giveaway" in promo_categories:
        rate += 0.014

    if "weekly_promo" in promo_categories:
        rate += 0.003

    return max(0.018, min(0.075, rate))

def choose_item_category(fan_segments, promo_categories):
    adjusted = list(item_categories)

    if "High In-Park Spender" in fan_segments:
        adjusted.extend([
            ("jersey", 0.05),
            ("apparel", 0.05),
            ("collectible", 0.03)
        ])

    if "Family Buyer" in fan_segments:
        adjusted.extend([
            ("kids", 0.08),
            ("souvenir", 0.05),
            ("novelty", 0.03)
        ])

    if "Theme Night Buyer" in fan_segments or "bobblehead_giveaway" in promo_categories or "jersey_giveaway" in promo_categories:
        adjusted.extend([
            ("theme_item", 0.10),
            ("collectible", 0.05),
            ("apparel", 0.03)
        ])

    return weighted_choice(adjusted)

games = read_csv(games_path)
promotions = read_csv(promotions_path)
fans = read_csv(fans_path)
segments = read_csv(segments_path)
scans = read_csv(scans_path)

games_by_id = {row["game_id"]: row for row in games}

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

merch_rows = []
transaction_counter = 1

for game in games:
    game_id = game["game_id"]
    scanned_qty = scanned_ticket_qty_by_game.get(game_id, 0)

    if scanned_qty <= 0:
        continue

    promo_categories = promo_categories_by_game.get(game_id, set())
    rate = merch_purchase_rate(game, promo_categories)

    transaction_count = int(scanned_qty * rate * random.uniform(0.85, 1.15))

    if transaction_count < 5:
        transaction_count = random.randint(5, 12)

    available_fans = scanned_fans_by_game.get(game_id, [])

    for _ in range(transaction_count):
        matched_to_fan = random.random() < fan_match_rate and len(available_fans) > 0
        fan_id = random.choice(available_fans) if matched_to_fan else ""
        fan_segments = segments_by_fan.get(fan_id, set()) if fan_id else set()

        item_category = choose_item_category(fan_segments, promo_categories)
        quantity = weighted_choice([(1, 0.72), (2, 0.21), (3, 0.05), (4, 0.02)])

        unit_price = price_for_item(item_category)
        gross_sales = round(unit_price * quantity, 2)

        if item_category in ["theme_item", "collectible", "jersey"]:
            discount_rate = random.uniform(0.00, 0.05)
        else:
            discount_rate = random.uniform(0.00, 0.12)

        discount_amount = round(gross_sales * discount_rate, 2)
        net_sales = round(gross_sales - discount_amount, 2)

        timestamp = transaction_time(game)

        promo_related_flag = (
            item_category in ["theme_item", "collectible", "jersey"]
            or "bobblehead_giveaway" in promo_categories
            or "jersey_giveaway" in promo_categories
        )

        merch_rows.append({
            "merch_transaction_id": f"MERCH_{transaction_counter:08d}",
            "game_id": game_id,
            "fan_id": fan_id,
            "transaction_date": timestamp.date().isoformat(),
            "transaction_time": timestamp.strftime("%H:%M:%S"),
            "item_category": item_category,
            "quantity": quantity,
            "gross_sales": f"{gross_sales:.2f}",
            "discount_amount": f"{discount_amount:.2f}",
            "net_sales": f"{net_sales:.2f}",
            "channel": weighted_choice(channels),
            "promo_related_flag": promo_related_flag,
            "fan_match_flag": matched_to_fan,
            "synthetic_data_flag": True
        })

        transaction_counter += 1

fields = [
    "merch_transaction_id",
    "game_id",
    "fan_id",
    "transaction_date",
    "transaction_time",
    "item_category",
    "quantity",
    "gross_sales",
    "discount_amount",
    "net_sales",
    "channel",
    "promo_related_flag",
    "fan_match_flag",
    "synthetic_data_flag"
]

write_csv(merch_path, merch_rows, fields)

total_net_sales = sum(float(row["net_sales"]) for row in merch_rows)
fan_matched_count = sum(1 for row in merch_rows if str(row["fan_match_flag"]).lower() == "true")
fan_match_share = fan_matched_count / len(merch_rows)

category_counts = Counter(row["item_category"] for row in merch_rows)
channel_counts = Counter(row["channel"] for row in merch_rows)

summary_rows = [
    {"metric": "merch_transaction_rows", "value": len(merch_rows)},
    {"metric": "total_merch_net_sales", "value": f"{total_net_sales:.2f}"},
    {"metric": "fan_matched_merch_transactions", "value": fan_matched_count},
    {"metric": "fan_match_share", "value": f"{fan_match_share:.4f}"},
    {"metric": "average_net_sales_per_transaction", "value": f"{total_net_sales / len(merch_rows):.2f}"}
]

for category, count in sorted(category_counts.items()):
    summary_rows.append({"metric": f"item_category_count_{category}", "value": count})

for channel, count in sorted(channel_counts.items()):
    summary_rows.append({"metric": f"channel_count_{channel}", "value": count})

write_csv(summary_path, summary_rows, ["metric", "value"])

print(f"Wrote {merch_path} with {len(merch_rows)} transactions")
print(f"Total merch net sales: {total_net_sales:.2f}")
print(f"Fan match share: {fan_match_share:.4f}")
print(f"Wrote {summary_path}")