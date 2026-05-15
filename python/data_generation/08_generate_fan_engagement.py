import csv
import random
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta

random.seed(49)

fans_path = Path("data/synthetic/fans.csv")
segments_path = Path("data/synthetic/fan_segments.csv")
games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")
merch_path = Path("data/synthetic/merch_transactions.csv")
concessions_path = Path("data/synthetic/concession_transactions.csv")

output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

engagement_path = output_dir / "fan_engagement.csv"
summary_path = output_dir / "fan_engagement_generation_summary.csv"

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

def to_int(value):
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

def engagement_score(engagement_type, fan_segments):
    base_scores = {
        "email_open": (8, 18),
        "email_click": (22, 38),
        "sms_click": (28, 45),
        "offer_response": (35, 55),
        "survey_response": (32, 50),
        "qr_scan": (25, 42),
        "app_interaction": (18, 35),
        "social_interaction": (12, 28),
        "merch_offer_click": (30, 48),
        "concession_offer_click": (22, 40),
        "group_interest_form": (55, 80),
        "premium_interest_form": (58, 85)
    }

    low, high = base_scores.get(engagement_type, (10, 30))
    score = random.randint(low, high)

    if "High In-Park Spender" in fan_segments:
        score += random.randint(3, 8)

    if "Season Ticket Holder" in fan_segments:
        score += random.randint(2, 6)

    if "Corporate Prospect" in fan_segments:
        score += random.randint(3, 10)

    if "Lapsed Fan" in fan_segments:
        score -= random.randint(2, 8)

    return max(1, min(score, 100))

def campaign_for_order(game, promo_categories, fan_segments):
    if "fireworks" in promo_categories:
        return "CAMPAIGN_FIREWORKS_GAME", "Fireworks Game Reminder"

    if "family" in promo_categories:
        return "CAMPAIGN_FAMILY_DAY", "Family Day Reminder"

    if "Theme Night Buyer" in fan_segments:
        return "CAMPAIGN_THEME_NIGHT", "Theme Night Follow-Up"

    if "Corporate Prospect" in fan_segments:
        return "CAMPAIGN_GROUP_PREMIUM", "Group and Premium Interest"

    if game["day_of_week"] in ["Friday", "Saturday"]:
        return "CAMPAIGN_WEEKEND_SERIES", "Weekend Series Reminder"

    return "CAMPAIGN_GAME_REMINDER", "Game Reminder"

def add_engagement(rows, counter, fan_id, game_id, campaign_id, campaign_name, engagement_date, engagement_type, engagement_channel, fan_segments, promo_related_flag):
    rows.append({
        "engagement_id": f"ENG_{counter:09d}",
        "fan_id": fan_id,
        "game_id": game_id,
        "campaign_id": campaign_id,
        "engagement_date": engagement_date.isoformat(),
        "engagement_type": engagement_type,
        "engagement_channel": engagement_channel,
        "engagement_score": engagement_score(engagement_type, fan_segments),
        "campaign_name": campaign_name,
        "promo_related_flag": promo_related_flag,
        "synthetic_data_flag": True
    })

    return counter + 1

fans = read_csv(fans_path)
segments = read_csv(segments_path)
games = read_csv(games_path)
promotions = read_csv(promotions_path)
orders = read_csv(orders_path)
scans = read_csv(scans_path)
merch = read_csv(merch_path)
concessions = read_csv(concessions_path)

fans_by_id = {row["fan_id"]: row for row in fans}
games_by_id = {row["game_id"]: row for row in games}

segments_by_fan = defaultdict(set)

for row in segments:
    segments_by_fan[row["fan_id"]].add(row["segment_name"])

promo_categories_by_game = defaultdict(set)

for row in promotions:
    promo_categories_by_game[row["game_id"]].add(row["promo_category"])

scanned_by_order = {}

for row in scans:
    scanned_by_order[row["order_id"]] = to_int(row["scanned_ticket_quantity"])

merch_spend_by_fan = defaultdict(float)

for row in merch:
    fan_id = row["fan_id"].strip()

    if fan_id:
        merch_spend_by_fan[fan_id] += float(row["net_sales"])

concession_spend_by_fan = defaultdict(float)

for row in concessions:
    fan_id = row["fan_id"].strip()

    if fan_id:
        concession_spend_by_fan[fan_id] += float(row["net_sales"])

engagement_rows = []
engagement_counter = 1

for order in orders:
    fan_id = order["fan_id"]
    game_id = order["game_id"]

    if fan_id not in fans_by_id or game_id not in games_by_id:
        continue

    fan = fans_by_id[fan_id]
    game = games_by_id[game_id]
    fan_segments = segments_by_fan.get(fan_id, set())
    promo_categories = promo_categories_by_game.get(game_id, set())

    game_date = parse_date(game["game_date"])
    campaign_id, campaign_name = campaign_for_order(game, promo_categories, fan_segments)
    promo_related_flag = len(promo_categories) > 0

    email_opt_in = to_bool(fan["email_opt_in_flag"])
    sms_opt_in = to_bool(fan["sms_opt_in_flag"])

    open_probability = 0.26

    if email_opt_in:
        if "Season Ticket Holder" in fan_segments:
            open_probability += 0.08

        if "Mini Plan Buyer" in fan_segments:
            open_probability += 0.06

        if "Repeat Single-Game Buyer" in fan_segments:
            open_probability += 0.05

        if "Lapsed Fan" in fan_segments:
            open_probability -= 0.06

        if "fireworks" in promo_categories or "family" in promo_categories:
            open_probability += 0.04

        if random.random() < open_probability:
            engagement_counter = add_engagement(
                engagement_rows,
                engagement_counter,
                fan_id,
                game_id,
                campaign_id,
                campaign_name,
                game_date - timedelta(days=random.randint(2, 7)),
                "email_open",
                "email",
                fan_segments,
                promo_related_flag
            )

            click_probability = 0.18

            if "High In-Park Spender" in fan_segments:
                click_probability += 0.04

            if "Corporate Prospect" in fan_segments:
                click_probability += 0.05

            if random.random() < click_probability:
                engagement_counter = add_engagement(
                    engagement_rows,
                    engagement_counter,
                    fan_id,
                    game_id,
                    campaign_id,
                    campaign_name,
                    game_date - timedelta(days=random.randint(1, 5)),
                    "email_click",
                    "email",
                    fan_segments,
                    promo_related_flag
                )

    if sms_opt_in:
        sms_probability = 0.07

        if "Season Ticket Holder" in fan_segments or "Mini Plan Buyer" in fan_segments:
            sms_probability += 0.03

        if game["day_of_week"] in ["Friday", "Saturday", "Sunday"]:
            sms_probability += 0.02

        if random.random() < sms_probability:
            engagement_counter = add_engagement(
                engagement_rows,
                engagement_counter,
                fan_id,
                game_id,
                campaign_id,
                campaign_name,
                game_date - timedelta(days=random.randint(0, 2)),
                "sms_click",
                "sms",
                fan_segments,
                promo_related_flag
            )

    scanned_quantity = scanned_by_order.get(order["order_id"], 0)

    if scanned_quantity > 0:
        if random.random() < 0.035:
            engagement_counter = add_engagement(
                engagement_rows,
                engagement_counter,
                fan_id,
                game_id,
                "CAMPAIGN_POSTGAME_SURVEY",
                "Postgame Survey",
                game_date + timedelta(days=random.randint(1, 3)),
                "survey_response",
                "email",
                fan_segments,
                False
            )

        if random.random() < 0.045:
            engagement_counter = add_engagement(
                engagement_rows,
                engagement_counter,
                fan_id,
                game_id,
                "CAMPAIGN_IN_PARK_QR",
                "In-Park QR Engagement",
                game_date,
                "qr_scan",
                "in_park",
                fan_segments,
                promo_related_flag
            )

    if order["ticket_type"] == "group" and random.random() < 0.08:
        engagement_counter = add_engagement(
            engagement_rows,
            engagement_counter,
            fan_id,
            game_id,
            "CAMPAIGN_GROUP_RENEWAL",
            "Group Renewal Interest",
            game_date + timedelta(days=random.randint(2, 10)),
            "group_interest_form",
            "web",
            fan_segments,
            False
        )

    if order["premium_flag"].strip().lower() == "true" and random.random() < 0.06:
        engagement_counter = add_engagement(
            engagement_rows,
            engagement_counter,
            fan_id,
            game_id,
            "CAMPAIGN_PREMIUM_UPGRADE",
            "Premium Upgrade Interest",
            game_date + timedelta(days=random.randint(2, 12)),
            "premium_interest_form",
            "web",
            fan_segments,
            False
        )

for fan_id, spend in merch_spend_by_fan.items():
    fan_segments = segments_by_fan.get(fan_id, set())

    if spend >= 75 and random.random() < 0.18:
        engagement_counter = add_engagement(
            engagement_rows,
            engagement_counter,
            fan_id,
            "",
            "CAMPAIGN_MERCH_OFFER",
            "Merch Offer Click",
            parse_date(fans_by_id[fan_id]["last_seen_date"]) + timedelta(days=random.randint(3, 21)),
            "merch_offer_click",
            "email",
            fan_segments,
            False
        )

for fan_id, spend in concession_spend_by_fan.items():
    fan_segments = segments_by_fan.get(fan_id, set())

    if spend >= 45 and random.random() < 0.10:
        engagement_counter = add_engagement(
            engagement_rows,
            engagement_counter,
            fan_id,
            "",
            "CAMPAIGN_CONCESSION_OFFER",
            "Concession Offer Click",
            parse_date(fans_by_id[fan_id]["last_seen_date"]) + timedelta(days=random.randint(3, 21)),
            "concession_offer_click",
            "email",
            fan_segments,
            False
        )

fields = [
    "engagement_id",
    "fan_id",
    "game_id",
    "campaign_id",
    "engagement_date",
    "engagement_type",
    "engagement_channel",
    "engagement_score",
    "campaign_name",
    "promo_related_flag",
    "synthetic_data_flag"
]

write_csv(engagement_path, engagement_rows, fields)

type_counts = Counter(row["engagement_type"] for row in engagement_rows)
channel_counts = Counter(row["engagement_channel"] for row in engagement_rows)

summary_rows = [
    {"metric": "fan_engagement_rows", "value": len(engagement_rows)},
    {"metric": "unique_engaged_fans", "value": len(set(row["fan_id"] for row in engagement_rows))},
    {"metric": "game_linked_engagement_rows", "value": sum(1 for row in engagement_rows if row["game_id"])},
    {"metric": "non_game_campaign_engagement_rows", "value": sum(1 for row in engagement_rows if not row["game_id"])},
    {"metric": "average_engagement_score", "value": f"{sum(int(row['engagement_score']) for row in engagement_rows) / len(engagement_rows):.2f}"}
]

for engagement_type, count in sorted(type_counts.items()):
    summary_rows.append({"metric": f"engagement_type_count_{engagement_type}", "value": count})

for channel, count in sorted(channel_counts.items()):
    summary_rows.append({"metric": f"engagement_channel_count_{channel}", "value": count})

write_csv(summary_path, summary_rows, ["metric", "value"])

print(f"Wrote {engagement_path} with {len(engagement_rows)} engagement rows")
print(f"Unique engaged fans: {len(set(row['fan_id'] for row in engagement_rows))}")
print(f"Wrote {summary_path}")