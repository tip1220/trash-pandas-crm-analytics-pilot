import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

random.seed(43)

games_path = Path("data/processed/games_clean.csv")
attendance_path = Path("data/processed/attendance_clean.csv")
fans_path = Path("data/synthetic/fans.csv")
segments_path = Path("data/synthetic/fan_segments.csv")

output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

orders_path = output_dir / "ticket_orders.csv"
items_path = output_dir / "ticket_order_items.csv"
summary_path = output_dir / "ticket_generation_summary.csv"

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def to_bool(value):
    return str(value).strip().lower() == "true"

def to_int(value, default=0):
    if value is None or str(value).strip() == "":
        return default
    return int(float(str(value).strip()))

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

def weighted_choice(options):
    total = sum(weight for _, weight in options)
    roll = random.uniform(0, total)
    current = 0

    for value, weight in options:
        current += weight
        if roll <= current:
            return value

    return options[-1][0]

def choose_quantity(ticket_type, fan_segments):
    if ticket_type == "season_ticket":
        return weighted_choice([(1, 0.20), (2, 0.50), (3, 0.15), (4, 0.15)])

    if ticket_type == "mini_plan":
        return weighted_choice([(2, 0.25), (3, 0.20), (4, 0.30), (5, 0.10), (6, 0.15)])

    if ticket_type == "premium":
        return weighted_choice([(2, 0.25), (3, 0.15), (4, 0.30), (5, 0.10), (6, 0.10), (8, 0.10)])

    if ticket_type == "comp":
        return weighted_choice([(1, 0.25), (2, 0.35), (3, 0.15), (4, 0.15), (6, 0.10)])

    if "Family Buyer" in fan_segments:
        return weighted_choice([(2, 0.10), (3, 0.25), (4, 0.35), (5, 0.15), (6, 0.15)])

    return weighted_choice([(1, 0.20), (2, 0.38), (3, 0.14), (4, 0.18), (5, 0.05), (6, 0.05)])

def price_for_ticket(ticket_type, section_type, day_of_week, promo_categories):
    if ticket_type == "comp":
        return 0.00

    if ticket_type == "season_ticket":
        base = random.uniform(8.00, 14.00)
    elif ticket_type == "mini_plan":
        base = random.uniform(9.00, 16.00)
    elif ticket_type == "premium":
        base = random.uniform(24.00, 42.00)
    else:
        base = random.uniform(10.00, 22.00)

    if section_type == "premium":
        base *= 1.45
    elif section_type == "club":
        base *= 1.25
    elif section_type == "berm":
        base *= 0.75

    if day_of_week in ["Friday", "Saturday"]:
        base *= 1.08

    if "fireworks" in promo_categories:
        base *= 1.06

    if "bobblehead_giveaway" in promo_categories or "jersey_giveaway" in promo_categories:
        base *= 1.05

    return round(base, 2)

def choose_section(ticket_type):
    if ticket_type == "premium":
        return weighted_choice([("premium", 0.60), ("club", 0.25), ("reserved", 0.15)])

    if ticket_type == "season_ticket":
        return weighted_choice([("reserved", 0.50), ("club", 0.25), ("premium", 0.15), ("berm", 0.10)])

    if ticket_type == "mini_plan":
        return weighted_choice([("reserved", 0.55), ("berm", 0.20), ("club", 0.15), ("premium", 0.10)])

    if ticket_type == "comp":
        return weighted_choice([("reserved", 0.60), ("berm", 0.30), ("club", 0.10)])

    return weighted_choice([("reserved", 0.52), ("berm", 0.28), ("club", 0.12), ("premium", 0.08)])

def purchase_channel(ticket_type):
    if ticket_type == "season_ticket":
        return weighted_choice([("account_rep", 0.55), ("online_account_manager", 0.35), ("box_office", 0.10)])

    if ticket_type == "mini_plan":
        return weighted_choice([("online", 0.45), ("account_rep", 0.35), ("phone", 0.10), ("box_office", 0.10)])

    if ticket_type == "premium":
        return weighted_choice([("account_rep", 0.45), ("online", 0.25), ("phone", 0.20), ("box_office", 0.10)])

    if ticket_type == "comp":
        return weighted_choice([("partner", 0.45), ("community", 0.30), ("box_office", 0.25)])

    return weighted_choice([("online", 0.62), ("box_office", 0.18), ("phone", 0.08), ("mobile", 0.12)])

def choose_ticket_type(lifecycle_segment, fan_segments, game):
    day = game["day_of_week"]
    promo_categories = game["promo_categories"]

    if lifecycle_segment == "Season Ticket Holder":
        return weighted_choice([("season_ticket", 0.82), ("premium", 0.05), ("single_game", 0.13)])

    if lifecycle_segment == "Mini Plan Buyer":
        return weighted_choice([("mini_plan", 0.70), ("single_game", 0.22), ("premium", 0.08)])

    if lifecycle_segment == "Repeat Single-Game Buyer":
        return weighted_choice([("single_game", 0.78), ("mini_plan", 0.14), ("premium", 0.08)])

    if lifecycle_segment == "Group Buyer":
        return weighted_choice([("single_game", 0.60), ("premium", 0.18), ("mini_plan", 0.12), ("comp", 0.10)])

    if lifecycle_segment == "Lapsed Fan":
        return weighted_choice([("single_game", 0.85), ("comp", 0.10), ("premium", 0.05)])

    if "Corporate Prospect" in fan_segments:
        return weighted_choice([("premium", 0.28), ("single_game", 0.52), ("mini_plan", 0.12), ("comp", 0.08)])

    if "Family Buyer" in fan_segments and day in ["Friday", "Saturday", "Sunday"]:
        return weighted_choice([("single_game", 0.78), ("mini_plan", 0.14), ("premium", 0.04), ("comp", 0.04)])

    if "fireworks" in promo_categories:
        return weighted_choice([("single_game", 0.84), ("mini_plan", 0.08), ("premium", 0.05), ("comp", 0.03)])

    return weighted_choice([("single_game", 0.84), ("mini_plan", 0.06), ("premium", 0.04), ("comp", 0.06)])

def order_date_for_game(game_date, ticket_type):
    if ticket_type == "season_ticket":
        days_before = random.randint(45, 180)
    elif ticket_type == "mini_plan":
        days_before = random.randint(20, 120)
    elif ticket_type == "premium":
        days_before = random.randint(7, 90)
    elif ticket_type == "comp":
        days_before = random.randint(1, 30)
    else:
        days_before = weighted_choice([
            (1, 0.16), (2, 0.12), (3, 0.10), (4, 0.08), (5, 0.08),
            (7, 0.10), (10, 0.10), (14, 0.10), (21, 0.08), (30, 0.08)
        ])

    return game_date - timedelta(days=days_before)

def get_game_ticket_target(game, attendance_by_game, season_avg_attendance):
    game_id = game["game_id"]
    season = game["season"]
    announced = attendance_by_game.get(game_id)

    if announced:
        base = announced
    else:
        base = season_avg_attendance.get(season, 4300)

    multiplier = random.uniform(1.04, 1.16)

    if game["day_of_week"] in ["Friday", "Saturday"]:
        multiplier += 0.04

    if game["day_of_week"] in ["Tuesday", "Wednesday"]:
        multiplier -= 0.04

    if "fireworks" in game["promo_categories"]:
        multiplier += 0.05

    if "family" in game["promo_categories"]:
        multiplier += 0.03

    if "bobblehead_giveaway" in game["promo_categories"] or "jersey_giveaway" in game["promo_categories"]:
        multiplier += 0.04

    target = int(base * multiplier)

    if target < 2800:
        target = random.randint(2800, 3600)

    return target

games = read_csv(games_path)
attendance = read_csv(attendance_path)
fans = read_csv(fans_path)
segments = read_csv(segments_path)

promo_categories_by_game = {}

with Path("data/processed/promotions_clean.csv").open("r", newline="") as f:
    promo_rows = list(csv.DictReader(f))

for row in promo_rows:
    promo_categories_by_game.setdefault(row["game_id"], set()).add(row["promo_category"])

for game in games:
    game["promo_categories"] = promo_categories_by_game.get(game["game_id"], set())

attendance_by_game = {}

for row in attendance:
    if row["attendance_match_status"] == "matched" and row["announced_attendance"]:
        attendance_by_game[row["game_id"]] = to_int(row["announced_attendance"])

season_attendance_values = {}

for game in games:
    season = game["season"]
    game_id = game["game_id"]

    if game_id in attendance_by_game:
        season_attendance_values.setdefault(season, []).append(attendance_by_game[game_id])

season_avg_attendance = {
    season: int(sum(values) / len(values))
    for season, values in season_attendance_values.items()
}

fan_profile = {}

for fan in fans:
    fan_profile[fan["fan_id"]] = {
        "fan_id": fan["fan_id"],
        "first_seen_date": parse_date(fan["first_seen_date"]),
        "last_seen_date": parse_date(fan["last_seen_date"]),
        "family_flag": to_bool(fan["family_flag"]),
        "corporate_flag": to_bool(fan["corporate_flag"]),
        "youth_sports_flag": to_bool(fan["youth_sports_flag"]),
        "market_distance_band": fan["market_distance_band"],
        "segments": set(),
        "lifecycle_segment": None
    }

for row in segments:
    fan_id = row["fan_id"]
    segment_name = row["segment_name"]

    if fan_id in fan_profile:
        fan_profile[fan_id]["segments"].add(segment_name)

        if row["segment_type"] == "lifecycle":
            fan_profile[fan_id]["lifecycle_segment"] = segment_name

fans_by_lifecycle = {}

for fan in fan_profile.values():
    lifecycle = fan["lifecycle_segment"]
    fans_by_lifecycle.setdefault(lifecycle, []).append(fan)

all_fans = list(fan_profile.values())

orders = []
items = []

order_counter = 1
item_counter = 1

lifecycle_order_weights = [
    ("One-Time Buyer", 0.24),
    ("Occasional Fan", 0.28),
    ("Repeat Single-Game Buyer", 0.22),
    ("Mini Plan Buyer", 0.10),
    ("Season Ticket Holder", 0.08),
    ("Group Buyer", 0.04),
    ("Lapsed Fan", 0.04)
]

for game in sorted(games, key=lambda row: row["game_date"]):
    game_date = parse_date(game["game_date"])
    ticket_target = get_game_ticket_target(game, attendance_by_game, season_avg_attendance)
    ticket_total = 0
    safety_counter = 0

    while ticket_total < ticket_target and safety_counter < 5000:
        safety_counter += 1

        selected_lifecycle = weighted_choice(lifecycle_order_weights)
        candidate_pool = fans_by_lifecycle.get(selected_lifecycle, all_fans)

        fan = random.choice(candidate_pool)
        retry_count = 0

        while not (fan["first_seen_date"] <= game_date <= fan["last_seen_date"]) and retry_count < 25:
            fan = random.choice(candidate_pool)
            retry_count += 1

        if not (fan["first_seen_date"] <= game_date <= fan["last_seen_date"]):
            candidate_pool = all_fans
            fan = random.choice(candidate_pool)
            retry_count = 0

            while not (fan["first_seen_date"] <= game_date <= fan["last_seen_date"]) and retry_count < 25:
                fan = random.choice(candidate_pool)
                retry_count += 1

        if not (fan["first_seen_date"] <= game_date <= fan["last_seen_date"]):
            continue

        ticket_type = choose_ticket_type(fan["lifecycle_segment"], fan["segments"], game)
        quantity = choose_quantity(ticket_type, fan["segments"])

        if ticket_total + quantity > ticket_target:
            quantity = max(1, ticket_target - ticket_total)

        section_type = choose_section(ticket_type)
        ticket_price = price_for_ticket(ticket_type, section_type, game["day_of_week"], game["promo_categories"])
        gross_ticket_revenue = round(ticket_price * quantity, 2)

        if ticket_type == "comp":
            discount_amount = gross_ticket_revenue
        elif ticket_type in ["season_ticket", "mini_plan"]:
            discount_amount = round(gross_ticket_revenue * random.uniform(0.08, 0.22), 2)
        elif ticket_type == "premium":
            discount_amount = round(gross_ticket_revenue * random.uniform(0.00, 0.06), 2)
        else:
            discount_amount = round(gross_ticket_revenue * random.uniform(0.00, 0.12), 2)

        net_ticket_revenue = round(max(gross_ticket_revenue - discount_amount, 0), 2)
        order_date = order_date_for_game(game_date, ticket_type)

        order_id = f"ORD_{order_counter:08d}"
        order_item_id = f"ITEM_{item_counter:09d}"

        channel = purchase_channel(ticket_type)

        premium_flag = ticket_type == "premium" or section_type in ["premium", "club"]

        orders.append({
            "order_id": order_id,
            "fan_id": fan["fan_id"],
            "account_id": "",
            "game_id": game["game_id"],
            "order_date": order_date.isoformat(),
            "purchase_channel": channel,
            "ticket_type": ticket_type,
            "ticket_quantity": quantity,
            "gross_ticket_revenue": f"{gross_ticket_revenue:.2f}",
            "discount_amount": f"{discount_amount:.2f}",
            "net_ticket_revenue": f"{net_ticket_revenue:.2f}",
            "group_order_flag": False,
            "premium_flag": premium_flag,
            "synthetic_data_flag": True
        })

        items.append({
            "order_item_id": order_item_id,
            "order_id": order_id,
            "game_id": game["game_id"],
            "fan_id": fan["fan_id"],
            "ticket_type": ticket_type,
            "section_type": section_type,
            "ticket_quantity": quantity,
            "ticket_price": f"{ticket_price:.2f}",
            "discount_amount": f"{discount_amount:.2f}",
            "net_ticket_revenue": f"{net_ticket_revenue:.2f}",
            "synthetic_data_flag": True
        })

        ticket_total += quantity
        order_counter += 1
        item_counter += 1

order_fields = [
    "order_id",
    "fan_id",
    "account_id",
    "game_id",
    "order_date",
    "purchase_channel",
    "ticket_type",
    "ticket_quantity",
    "gross_ticket_revenue",
    "discount_amount",
    "net_ticket_revenue",
    "group_order_flag",
    "premium_flag",
    "synthetic_data_flag"
]

item_fields = [
    "order_item_id",
    "order_id",
    "game_id",
    "fan_id",
    "ticket_type",
    "section_type",
    "ticket_quantity",
    "ticket_price",
    "discount_amount",
    "net_ticket_revenue",
    "synthetic_data_flag"
]

write_csv(orders_path, orders, order_fields)
write_csv(items_path, items, item_fields)

total_ticket_quantity = sum(int(row["ticket_quantity"]) for row in orders)
total_net_revenue = sum(float(row["net_ticket_revenue"]) for row in orders)

ticket_type_counts = {}
ticket_type_quantity = {}

for row in orders:
    ticket_type_counts[row["ticket_type"]] = ticket_type_counts.get(row["ticket_type"], 0) + 1
    ticket_type_quantity[row["ticket_type"]] = ticket_type_quantity.get(row["ticket_type"], 0) + int(row["ticket_quantity"])

summary_rows = [
    {"metric": "ticket_order_rows", "value": len(orders)},
    {"metric": "ticket_order_item_rows", "value": len(items)},
    {"metric": "total_ticket_quantity", "value": total_ticket_quantity},
    {"metric": "total_net_ticket_revenue", "value": f"{total_net_revenue:.2f}"},
    {"metric": "average_ticket_quantity_per_order", "value": f"{total_ticket_quantity / len(orders):.2f}"}
]

for ticket_type in sorted(ticket_type_counts):
    summary_rows.append({"metric": f"order_count_{ticket_type}", "value": ticket_type_counts[ticket_type]})
    summary_rows.append({"metric": f"ticket_quantity_{ticket_type}", "value": ticket_type_quantity[ticket_type]})

write_csv(summary_path, summary_rows, ["metric", "value"])

print(f"Wrote {orders_path} with {len(orders)} orders")
print(f"Wrote {items_path} with {len(items)} order item rows")
print(f"Total ticket quantity: {total_ticket_quantity}")
print(f"Total net ticket revenue: {total_net_revenue:.2f}")
print(f"Wrote {summary_path}")