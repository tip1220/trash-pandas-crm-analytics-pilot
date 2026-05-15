import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)

games_path = Path("data/processed/games_clean.csv")
output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

fans_path = output_dir / "fans.csv"
segments_path = output_dir / "fan_segments.csv"
summary_path = output_dir / "fan_generation_summary.csv"

fan_count = 45000

local_zips = [
    "35801", "35802", "35803", "35805", "35806", "35810", "35811", "35816",
    "35758", "35757", "35756", "35749", "35763", "35613", "35611", "35649"
]

regional_zips = [
    "35203", "35205", "35209", "35242", "36104", "36109", "37402", "37405",
    "37203", "37209", "37027", "37130", "35630", "35055", "35901", "35903"
]

out_of_market_zips = [
    "30303", "30318", "38103", "38117", "40202", "40207", "60601", "60614",
    "75001", "75201", "32801", "32803", "28202", "28205", "20001", "10001"
]

fan_created_sources = [
    "online_ticket_purchase",
    "box_office_purchase",
    "group_sale",
    "promotion_signup",
    "team_store_purchase",
    "email_signup",
    "community_event",
    "sponsor_activation"
]

lifecycle_segments = [
    ("One-Time Buyer", 0.36, 55, 85),
    ("Occasional Fan", 0.28, 50, 80),
    ("Repeat Single-Game Buyer", 0.14, 55, 90),
    ("Mini Plan Buyer", 0.07, 65, 95),
    ("Season Ticket Holder", 0.035, 75, 100),
    ("Group Buyer", 0.035, 60, 95),
    ("Lapsed Fan", 0.08, 45, 85)
]

additional_segments = [
    ("Theme Night Buyer", "behavioral", 0.18, 50, 90),
    ("Family Buyer", "behavioral", 0.22, 55, 95),
    ("Corporate Prospect", "sales", 0.07, 50, 90),
    ("High In-Park Spender", "value", 0.12, 65, 100)
]

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def weighted_choice(options):
    random_value = random.random()
    cumulative = 0

    for value, weight, low_score, high_score in options:
        cumulative += weight
        if random_value <= cumulative:
            return value, random.randint(low_score, high_score)

    value, weight, low_score, high_score = options[-1]
    return value, random.randint(low_score, high_score)

def random_date(start_date, end_date):
    days = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, max(days, 0)))

def choose_market():
    roll = random.random()

    if roll < 0.70:
        return "local", random.choice(local_zips)

    if roll < 0.90:
        return "regional", random.choice(regional_zips)

    return "out_of_market", random.choice(out_of_market_zips)

games = read_csv(games_path)
game_dates = sorted(datetime.strptime(row["game_date"], "%Y-%m-%d").date() for row in games)

min_game_date = game_dates[0]
max_game_date = game_dates[-1]

fans = []
fan_segments = []
segment_id_counter = 1

for i in range(1, fan_count + 1):
    fan_id = f"FAN_{i:06d}"
    household_id = f"HH_{random.randint(1, int(fan_count * 0.72)):06d}"

    lifecycle_segment, lifecycle_score = weighted_choice(lifecycle_segments)
    market_distance_band, zip_code = choose_market()

    first_seen_date = random_date(min_game_date, max_game_date)

    if lifecycle_segment == "Lapsed Fan":
        max_lapsed_date = min(max_game_date, first_seen_date + timedelta(days=250))
        last_seen_date = random_date(first_seen_date, max_lapsed_date)
    elif lifecycle_segment == "One-Time Buyer":
        last_seen_date = first_seen_date
    elif lifecycle_segment in ["Occasional Fan", "Repeat Single-Game Buyer", "Mini Plan Buyer", "Group Buyer"]:
        last_seen_date = random_date(first_seen_date, max_game_date)
    elif lifecycle_segment == "Season Ticket Holder":
        season_ticket_start = max(first_seen_date, max_game_date - timedelta(days=180))
        last_seen_date = random_date(season_ticket_start, max_game_date)
    else:
        last_seen_date = random_date(first_seen_date, max_game_date)

    family_flag = random.random() < 0.24
    corporate_flag = random.random() < 0.07
    youth_sports_flag = random.random() < 0.09

    if lifecycle_segment == "Group Buyer":
        corporate_flag = corporate_flag or random.random() < 0.35
        youth_sports_flag = youth_sports_flag or random.random() < 0.25

    if lifecycle_segment == "Season Ticket Holder":
        email_opt_in_probability = 0.88
        sms_opt_in_probability = 0.38
    elif lifecycle_segment == "Mini Plan Buyer":
        email_opt_in_probability = 0.82
        sms_opt_in_probability = 0.32
    elif lifecycle_segment == "Repeat Single-Game Buyer":
        email_opt_in_probability = 0.76
        sms_opt_in_probability = 0.28
    elif lifecycle_segment == "One-Time Buyer":
        email_opt_in_probability = 0.56
        sms_opt_in_probability = 0.16
    elif lifecycle_segment == "Lapsed Fan":
        email_opt_in_probability = 0.50
        sms_opt_in_probability = 0.14
    else:
        email_opt_in_probability = 0.65
        sms_opt_in_probability = 0.22

    email_opt_in_flag = random.random() < email_opt_in_probability
    sms_opt_in_flag = random.random() < sms_opt_in_probability

    fan_created_source = random.choice(fan_created_sources)

    fans.append({
        "fan_id": fan_id,
        "household_id": household_id,
        "first_seen_date": first_seen_date.isoformat(),
        "last_seen_date": last_seen_date.isoformat(),
        "zip_code": zip_code,
        "market_distance_band": market_distance_band,
        "email_opt_in_flag": email_opt_in_flag,
        "sms_opt_in_flag": sms_opt_in_flag,
        "family_flag": family_flag,
        "corporate_flag": corporate_flag,
        "youth_sports_flag": youth_sports_flag,
        "fan_created_source": fan_created_source,
        "synthetic_data_flag": True
    })

    fan_segments.append({
        "fan_segment_id": f"FSEG_{segment_id_counter:07d}",
        "fan_id": fan_id,
        "segment_name": lifecycle_segment,
        "segment_type": "lifecycle",
        "assigned_date": first_seen_date.isoformat(),
        "active_flag": lifecycle_segment != "Lapsed Fan",
        "segment_score": lifecycle_score,
        "synthetic_data_flag": True
    })
    segment_id_counter += 1

    for segment_name, segment_type, probability, low_score, high_score in additional_segments:
        add_segment = random.random() < probability

        if segment_name == "Family Buyer" and family_flag:
            add_segment = random.random() < 0.72

        if segment_name == "Corporate Prospect" and corporate_flag:
            add_segment = random.random() < 0.80

        if segment_name == "High In-Park Spender" and lifecycle_segment in ["Season Ticket Holder", "Mini Plan Buyer", "Repeat Single-Game Buyer"]:
            add_segment = add_segment or random.random() < 0.18

        if segment_name == "Theme Night Buyer" and lifecycle_segment in ["One-Time Buyer", "Occasional Fan", "Repeat Single-Game Buyer"]:
            add_segment = add_segment or random.random() < 0.10

        if add_segment:
            fan_segments.append({
                "fan_segment_id": f"FSEG_{segment_id_counter:07d}",
                "fan_id": fan_id,
                "segment_name": segment_name,
                "segment_type": segment_type,
                "assigned_date": first_seen_date.isoformat(),
                "active_flag": True,
                "segment_score": random.randint(low_score, high_score),
                "synthetic_data_flag": True
            })
            segment_id_counter += 1

fan_fields = [
    "fan_id",
    "household_id",
    "first_seen_date",
    "last_seen_date",
    "zip_code",
    "market_distance_band",
    "email_opt_in_flag",
    "sms_opt_in_flag",
    "family_flag",
    "corporate_flag",
    "youth_sports_flag",
    "fan_created_source",
    "synthetic_data_flag"
]

segment_fields = [
    "fan_segment_id",
    "fan_id",
    "segment_name",
    "segment_type",
    "assigned_date",
    "active_flag",
    "segment_score",
    "synthetic_data_flag"
]

with fans_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fan_fields)
    writer.writeheader()
    writer.writerows(fans)

with segments_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=segment_fields)
    writer.writeheader()
    writer.writerows(fan_segments)

segment_counts = {}

for row in fan_segments:
    segment_counts[row["segment_name"]] = segment_counts.get(row["segment_name"], 0) + 1

summary_rows = [
    {"metric": "fan_count", "value": len(fans)},
    {"metric": "fan_segment_rows", "value": len(fan_segments)},
    {"metric": "household_count", "value": len(set(row["household_id"] for row in fans))}
]

for segment_name, count in sorted(segment_counts.items()):
    summary_rows.append({"metric": f"segment_count_{segment_name}", "value": count})

with summary_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["metric", "value"])
    writer.writeheader()
    writer.writerows(summary_rows)

print(f"Wrote {fans_path} with {len(fans)} fans")
print(f"Wrote {segments_path} with {len(fan_segments)} segment rows")
print(f"Wrote {summary_path}")