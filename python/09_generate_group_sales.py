import csv
import random
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

random.seed(45)

games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
fans_path = Path("data/synthetic/fans.csv")
segments_path = Path("data/synthetic/fan_segments.csv")
ticket_orders_path = Path("data/synthetic/ticket_orders.csv")
ticket_items_path = Path("data/synthetic/ticket_order_items.csv")
ticket_scans_path = Path("data/synthetic/ticket_scans.csv")

output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

group_accounts_path = output_dir / "group_accounts.csv"
group_sales_path = output_dir / "group_sales.csv"
group_summary_path = output_dir / "group_sales_generation_summary.csv"
ticket_summary_path = output_dir / "ticket_generation_summary.csv"
scan_summary_path = output_dir / "ticket_scan_generation_summary.csv"

group_account_count = 1200
group_sale_count = 3600

account_types = [
    ("corporate", 0.24),
    ("school", 0.18),
    ("church", 0.12),
    ("youth_sports", 0.15),
    ("nonprofit", 0.10),
    ("community_group", 0.09),
    ("local_business", 0.08),
    ("healthcare", 0.04)
]

industries = {
    "corporate": ["technology", "finance", "manufacturing", "construction", "professional_services"],
    "school": ["education"],
    "church": ["faith_community"],
    "youth_sports": ["youth_sports"],
    "nonprofit": ["nonprofit"],
    "community_group": ["community"],
    "local_business": ["restaurant", "retail", "service_business"],
    "healthcare": ["healthcare"]
}

cities = [
    ("Huntsville", "35801"),
    ("Madison", "35758"),
    ("Decatur", "35601"),
    ("Athens", "35611"),
    ("Harvest", "35749"),
    ("Owens Cross Roads", "35763"),
    ("Meridianville", "35759"),
    ("Hazel Green", "35750"),
    ("Florence", "35630"),
    ("Cullman", "35055")
]

account_owners = [
    "Sales Rep A",
    "Sales Rep B",
    "Sales Rep C",
    "Group Sales Rep A",
    "Group Sales Rep B",
    "Business Development Rep"
]

event_types = [
    "group_outing",
    "fundraiser",
    "corporate_night",
    "team_event",
    "school_night",
    "community_night",
    "church_night",
    "youth_sports_night"
]

section_types = [
    ("reserved", 0.50),
    ("berm", 0.20),
    ("club", 0.18),
    ("premium", 0.12)
]

purchase_channels = [
    ("account_rep", 0.65),
    ("phone", 0.16),
    ("online", 0.12),
    ("box_office", 0.07)
]

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def weighted_choice(options):
    total = sum(weight for _, weight in options)
    roll = random.uniform(0, total)
    current = 0

    for value, weight in options:
        current += weight
        if roll <= current:
            return value

    return options[-1][0]

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

def next_numeric_id(rows, field, prefix):
    max_value = 0

    for row in rows:
        value = row[field].replace(prefix, "")
        try:
            max_value = max(max_value, int(value))
        except ValueError:
            pass

    return max_value + 1

def choose_group_quantity(account_type):
    if account_type == "corporate":
        return random.randint(18, 90)

    if account_type == "school":
        return random.randint(25, 120)

    if account_type == "youth_sports":
        return random.randint(20, 100)

    if account_type == "church":
        return random.randint(18, 80)

    if account_type == "healthcare":
        return random.randint(15, 70)

    return random.randint(12, 65)

def choose_ticket_price(section_type, account_type):
    if section_type == "premium":
        base = random.uniform(24, 38)
    elif section_type == "club":
        base = random.uniform(18, 28)
    elif section_type == "reserved":
        base = random.uniform(11, 20)
    else:
        base = random.uniform(8, 15)

    if account_type in ["school", "youth_sports", "nonprofit", "church"]:
        base *= random.uniform(0.78, 0.90)
    else:
        base *= random.uniform(0.88, 1.00)

    return round(base, 2)

def scan_rate_for_group(account_type, promo_categories, day_of_week):
    rate = 0.82

    if account_type in ["school", "youth_sports"]:
        rate += 0.04

    if account_type == "corporate":
        rate += 0.02

    if account_type in ["nonprofit", "community_group"]:
        rate -= 0.02

    if day_of_week in ["Friday", "Saturday"]:
        rate += 0.03

    if day_of_week in ["Tuesday", "Wednesday"]:
        rate -= 0.03

    if "fireworks" in promo_categories:
        rate += 0.04

    if "family" in promo_categories:
        rate += 0.03

    return max(0.62, min(0.96, rate))

def scan_status_from_quantities(ticket_quantity, scanned_quantity):
    if scanned_quantity == ticket_quantity:
        return "scanned"

    if scanned_quantity == 0:
        return "not_scanned"

    return "partial_scanned"

def scan_time_for_game(game_date, day_of_week, start_time):
    if start_time:
        hour, minute = [int(part) for part in start_time.split(":")]
    elif day_of_week == "Sunday":
        hour, minute = 14, 35
    else:
        hour, minute = 18, 35

    game_datetime = datetime.strptime(game_date, "%Y-%m-%d").replace(hour=hour, minute=minute)
    offset = random.randint(-40, 20)

    return (game_datetime + timedelta(minutes=offset)).strftime("%Y-%m-%d %H:%M:%S")

def choose_group_event_type(account_type):
    if account_type == "school":
        return weighted_choice([("school_night", 0.60), ("fundraiser", 0.25), ("group_outing", 0.15)])

    if account_type == "church":
        return weighted_choice([("church_night", 0.60), ("community_night", 0.20), ("group_outing", 0.20)])

    if account_type == "youth_sports":
        return weighted_choice([("youth_sports_night", 0.70), ("team_event", 0.20), ("group_outing", 0.10)])

    if account_type == "corporate":
        return weighted_choice([("corporate_night", 0.50), ("group_outing", 0.30), ("team_event", 0.20)])

    return random.choice(event_types)

def update_ticket_summary(orders):
    total_ticket_quantity = sum(int(row["ticket_quantity"]) for row in orders)
    total_net_revenue = sum(float(row["net_ticket_revenue"]) for row in orders)

    ticket_type_counts = Counter(row["ticket_type"] for row in orders)
    ticket_type_quantity = defaultdict(int)

    for row in orders:
        ticket_type_quantity[row["ticket_type"]] += int(row["ticket_quantity"])

    summary_rows = [
        {"metric": "ticket_order_rows", "value": len(orders)},
        {"metric": "ticket_order_item_rows", "value": len(orders)},
        {"metric": "total_ticket_quantity", "value": total_ticket_quantity},
        {"metric": "total_net_ticket_revenue", "value": f"{total_net_revenue:.2f}"},
        {"metric": "average_ticket_quantity_per_order", "value": f"{total_ticket_quantity / len(orders):.2f}"}
    ]

    for ticket_type in sorted(ticket_type_counts):
        summary_rows.append({"metric": f"order_count_{ticket_type}", "value": ticket_type_counts[ticket_type]})
        summary_rows.append({"metric": f"ticket_quantity_{ticket_type}", "value": ticket_type_quantity[ticket_type]})

    write_csv(ticket_summary_path, summary_rows, ["metric", "value"])

def update_scan_summary(scans):
    total_ticket_quantity = sum(int(row["ticket_quantity"]) for row in scans)
    total_scanned_quantity = sum(int(row["scanned_ticket_quantity"]) for row in scans)
    total_no_show_quantity = sum(int(row["no_show_ticket_quantity"]) for row in scans)

    scan_status_counts = Counter(row["scan_status"] for row in scans)

    summary_rows = [
        {"metric": "ticket_scan_rows", "value": len(scans)},
        {"metric": "total_ticket_quantity", "value": total_ticket_quantity},
        {"metric": "total_scanned_ticket_quantity", "value": total_scanned_quantity},
        {"metric": "total_no_show_ticket_quantity", "value": total_no_show_quantity},
        {"metric": "overall_scan_rate", "value": f"{total_scanned_quantity / total_ticket_quantity:.4f}"},
        {"metric": "overall_no_show_rate", "value": f"{total_no_show_quantity / total_ticket_quantity:.4f}"}
    ]

    for status, count in sorted(scan_status_counts.items()):
        summary_rows.append({"metric": f"scan_status_count_{status}", "value": count})

    write_csv(scan_summary_path, summary_rows, ["metric", "value"])

games = read_csv(games_path)
promotions = read_csv(promotions_path)
fans = read_csv(fans_path)
segments = read_csv(segments_path)
orders = read_csv(ticket_orders_path)
items = read_csv(ticket_items_path)
scans = read_csv(ticket_scans_path)

games_by_id = {row["game_id"]: row for row in games}
promo_categories_by_game = {}

for row in promotions:
    promo_categories_by_game.setdefault(row["game_id"], set()).add(row["promo_category"])

fan_segments = defaultdict(set)

for row in segments:
    fan_segments[row["fan_id"]].add(row["segment_name"])

group_candidate_fans = [
    fan for fan in fans
    if "Group Buyer" in fan_segments[fan["fan_id"]]
    or "Corporate Prospect" in fan_segments[fan["fan_id"]]
    or fan["corporate_flag"].lower() == "true"
    or fan["youth_sports_flag"].lower() == "true"
]

if not group_candidate_fans:
    group_candidate_fans = fans

group_accounts = []

for i in range(1, group_account_count + 1):
    account_id = f"ACCT_{i:05d}"
    account_type = weighted_choice(account_types)
    city, zip_code = random.choice(cities)
    industry = random.choice(industries[account_type])
    account_owner = random.choice(account_owners)
    renewal_status = weighted_choice([
        ("new", 0.24),
        ("active", 0.44),
        ("renewal_target", 0.22),
        ("lapsed", 0.10)
    ])

    corporate_prospect_flag = account_type in ["corporate", "local_business", "healthcare"] or random.random() < 0.08

    first_game = random.choice(games)
    last_game = random.choice(games)

    first_purchase_date = min(parse_date(first_game["game_date"]), parse_date(last_game["game_date"]))
    last_purchase_date = max(parse_date(first_game["game_date"]), parse_date(last_game["game_date"]))

    group_accounts.append({
        "account_id": account_id,
        "account_name": f"Synthetic {account_type.replace('_', ' ').title()} Account {i:04d}",
        "account_type": account_type,
        "account_owner": account_owner,
        "industry": industry,
        "city": city,
        "zip_code": zip_code,
        "first_purchase_date": first_purchase_date.isoformat(),
        "last_purchase_date": last_purchase_date.isoformat(),
        "renewal_status": renewal_status,
        "corporate_prospect_flag": corporate_prospect_flag,
        "synthetic_data_flag": True
    })

order_counter = next_numeric_id(orders, "order_id", "ORD_")
item_counter = next_numeric_id(items, "order_item_id", "ITEM_")
scan_counter = next_numeric_id(scans, "scan_id", "SCAN_")

group_sales = []

high_group_fit_games = [
    game for game in games
    if game["day_of_week"] in ["Friday", "Saturday", "Sunday"]
    or "family" in promo_categories_by_game.get(game["game_id"], set())
    or "fireworks" in promo_categories_by_game.get(game["game_id"], set())
    or "weekly_promo" in promo_categories_by_game.get(game["game_id"], set())
]

for i in range(1, group_sale_count + 1):
    account = random.choice(group_accounts)

    if random.random() < 0.70:
        game = random.choice(high_group_fit_games)
    else:
        game = random.choice(games)

    fan = random.choice(group_candidate_fans)
    account_type = account["account_type"]
    game_id = game["game_id"]
    promo_categories = promo_categories_by_game.get(game_id, set())

    ticket_quantity = choose_group_quantity(account_type)
    section_type = weighted_choice(section_types)
    ticket_price = choose_ticket_price(section_type, account_type)

    gross_revenue = round(ticket_quantity * ticket_price, 2)
    discount_rate = random.uniform(0.05, 0.22)
    discount_amount = round(gross_revenue * discount_rate, 2)
    net_revenue = round(gross_revenue - discount_amount, 2)

    game_date = parse_date(game["game_date"])
    order_date = game_date - timedelta(days=random.randint(14, 100))

    order_id = f"ORD_{order_counter:08d}"
    order_item_id = f"ITEM_{item_counter:09d}"
    scan_id = f"SCAN_{scan_counter:09d}"
    group_sale_id = f"GRP_{i:07d}"

    group_scan_rate = scan_rate_for_group(account_type, promo_categories, game["day_of_week"])
    scanned_quantity = sum(1 for _ in range(ticket_quantity) if random.random() < group_scan_rate)
    no_show_quantity = ticket_quantity - scanned_quantity

    scan_status = scan_status_from_quantities(ticket_quantity, scanned_quantity)
    scan_time = ""
    gate = ""

    if scanned_quantity > 0:
        scan_time = scan_time_for_game(game["game_date"], game["day_of_week"], game["start_time"])
        gate = weighted_choice([
            ("Main Gate", 0.40),
            ("Third Base Gate", 0.20),
            ("First Base Gate", 0.18),
            ("Outfield Gate", 0.12),
            ("Suite/Premium Entrance", 0.10)
        ])

    event_type = choose_group_event_type(account_type)

    renewal_flag = account["renewal_status"] in ["active", "renewal_target"] and scanned_quantity / ticket_quantity >= 0.72
    upsell_flag = (
        account_type in ["corporate", "local_business", "healthcare"]
        and ticket_quantity >= 30
        and scanned_quantity / ticket_quantity >= 0.78
    )

    orders.append({
        "order_id": order_id,
        "fan_id": fan["fan_id"],
        "account_id": account["account_id"],
        "game_id": game_id,
        "order_date": order_date.isoformat(),
        "purchase_channel": weighted_choice(purchase_channels),
        "ticket_type": "group",
        "ticket_quantity": ticket_quantity,
        "gross_ticket_revenue": f"{gross_revenue:.2f}",
        "discount_amount": f"{discount_amount:.2f}",
        "net_ticket_revenue": f"{net_revenue:.2f}",
        "group_order_flag": True,
        "premium_flag": section_type in ["premium", "club"],
        "synthetic_data_flag": True
    })

    items.append({
        "order_item_id": order_item_id,
        "order_id": order_id,
        "game_id": game_id,
        "fan_id": fan["fan_id"],
        "ticket_type": "group",
        "section_type": section_type,
        "ticket_quantity": ticket_quantity,
        "ticket_price": f"{ticket_price:.2f}",
        "discount_amount": f"{discount_amount:.2f}",
        "net_ticket_revenue": f"{net_revenue:.2f}",
        "synthetic_data_flag": True
    })

    scans.append({
        "scan_id": scan_id,
        "order_item_id": order_item_id,
        "order_id": order_id,
        "game_id": game_id,
        "fan_id": fan["fan_id"],
        "ticket_quantity": ticket_quantity,
        "scanned_ticket_quantity": scanned_quantity,
        "no_show_ticket_quantity": no_show_quantity,
        "scan_status": scan_status,
        "scan_time": scan_time,
        "gate": gate,
        "no_show_flag": no_show_quantity > 0,
        "scan_match_confidence": random.randint(82, 99),
        "synthetic_data_flag": True
    })

    group_sales.append({
        "group_sale_id": group_sale_id,
        "account_id": account["account_id"],
        "game_id": game_id,
        "order_id": order_id,
        "group_ticket_quantity": ticket_quantity,
        "group_ticket_revenue": f"{net_revenue:.2f}",
        "group_type": account_type,
        "event_type": event_type,
        "renewal_flag": renewal_flag,
        "upsell_flag": upsell_flag,
        "group_scan_rate": f"{scanned_quantity / ticket_quantity:.4f}",
        "synthetic_data_flag": True
    })

    order_counter += 1
    item_counter += 1
    scan_counter += 1

account_fields = [
    "account_id",
    "account_name",
    "account_type",
    "account_owner",
    "industry",
    "city",
    "zip_code",
    "first_purchase_date",
    "last_purchase_date",
    "renewal_status",
    "corporate_prospect_flag",
    "synthetic_data_flag"
]

group_sale_fields = [
    "group_sale_id",
    "account_id",
    "game_id",
    "order_id",
    "group_ticket_quantity",
    "group_ticket_revenue",
    "group_type",
    "event_type",
    "renewal_flag",
    "upsell_flag",
    "group_scan_rate",
    "synthetic_data_flag"
]

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

write_csv(group_accounts_path, group_accounts, account_fields)
write_csv(group_sales_path, group_sales, group_sale_fields)
write_csv(ticket_orders_path, orders, order_fields)
write_csv(ticket_items_path, items, item_fields)
write_csv(ticket_scans_path, scans, scan_fields)

update_ticket_summary(orders)
update_scan_summary(scans)

total_group_tickets = sum(int(row["group_ticket_quantity"]) for row in group_sales)
total_group_revenue = sum(float(row["group_ticket_revenue"]) for row in group_sales)
renewal_count = sum(1 for row in group_sales if str(row["renewal_flag"]).lower() == "true")
upsell_count = sum(1 for row in group_sales if str(row["upsell_flag"]).lower() == "true")

summary_rows = [
    {"metric": "group_account_rows", "value": len(group_accounts)},
    {"metric": "group_sales_rows", "value": len(group_sales)},
    {"metric": "total_group_tickets", "value": total_group_tickets},
    {"metric": "total_group_revenue", "value": f"{total_group_revenue:.2f}"},
    {"metric": "average_group_ticket_quantity", "value": f"{total_group_tickets / len(group_sales):.2f}"},
    {"metric": "renewal_flag_count", "value": renewal_count},
    {"metric": "upsell_flag_count", "value": upsell_count}
]

account_type_counts = Counter(row["account_type"] for row in group_accounts)
group_type_counts = Counter(row["group_type"] for row in group_sales)

for account_type, count in sorted(account_type_counts.items()):
    summary_rows.append({"metric": f"account_type_count_{account_type}", "value": count})

for group_type, count in sorted(group_type_counts.items()):
    summary_rows.append({"metric": f"group_sale_count_{group_type}", "value": count})

write_csv(group_summary_path, summary_rows, ["metric", "value"])

print(f"Wrote {group_accounts_path} with {len(group_accounts)} accounts")
print(f"Wrote {group_sales_path} with {len(group_sales)} group sales")
print(f"Appended {len(group_sales)} group ticket orders/items/scans")
print(f"Total group tickets: {total_group_tickets}")
print(f"Total group revenue: {total_group_revenue:.2f}")
print(f"Wrote {group_summary_path}")