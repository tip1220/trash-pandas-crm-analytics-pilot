import csv
import random
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path

random.seed(1220)

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
QC_DIR = Path("outputs/qc")

ATTENDANCE_FILE = PROCESSED_DIR / "game_attendance_reconciled_2023_2025.csv"
FANS_OUT = PROCESSED_DIR / "synthetic_fans.csv"
ORDERS_OUT = PROCESSED_DIR / "synthetic_ticket_orders.csv"
QC_OUT = QC_DIR / "synthetic_crm_generation_summary.txt"

SEGMENTS = {
    "season_ticket_holder": {
        "base_weight": 0.18,
        "qty_range": (1, 4),
        "existing_prob": 0.95,
        "price": 16.00,
        "ticket_type": "season_ticket",
        "group_order": 0,
        "lead_days": (60, 180),
    },
    "mini_plan_buyer": {
        "base_weight": 0.12,
        "qty_range": (2, 6),
        "existing_prob": 0.75,
        "price": 18.00,
        "ticket_type": "mini_plan",
        "group_order": 0,
        "lead_days": (20, 90),
    },
    "family_buyer": {
        "base_weight": 0.22,
        "qty_range": (3, 6),
        "existing_prob": 0.45,
        "price": 17.00,
        "ticket_type": "single_game",
        "group_order": 0,
        "lead_days": (3, 45),
    },
    "casual_single_game": {
        "base_weight": 0.20,
        "qty_range": (1, 4),
        "existing_prob": 0.20,
        "price": 19.00,
        "ticket_type": "single_game",
        "group_order": 0,
        "lead_days": (0, 21),
    },
    "promo_chaser": {
        "base_weight": 0.13,
        "qty_range": (2, 5),
        "existing_prob": 0.35,
        "price": 18.50,
        "ticket_type": "promo_single_game",
        "group_order": 0,
        "lead_days": (1, 30),
    },
    "group_buyer": {
        "base_weight": 0.035,
        "qty_range": (8, 35),
        "existing_prob": 0.45,
        "price": 14.00,
        "ticket_type": "group",
        "group_order": 1,
        "lead_days": (14, 120),
    },
    "corporate_group": {
        "base_weight": 0.012,
        "qty_range": (15, 60),
        "existing_prob": 0.60,
        "price": 20.00,
        "ticket_type": "corporate_group",
        "group_order": 1,
        "lead_days": (30, 150),
    },
    "out_of_town_visitor": {
        "base_weight": 0.03,
        "qty_range": (1, 4),
        "existing_prob": 0.10,
        "price": 20.00,
        "ticket_type": "single_game",
        "group_order": 0,
        "lead_days": (0, 14),
    },
}

CITIES = [
    ("Madison", "AL", 0.30),
    ("Huntsville", "AL", 0.34),
    ("Athens", "AL", 0.08),
    ("Decatur", "AL", 0.07),
    ("Harvest", "AL", 0.06),
    ("Meridianville", "AL", 0.04),
    ("Birmingham", "AL", 0.03),
    ("Florence", "AL", 0.02),
    ("Nashville", "TN", 0.03),
    ("Chattanooga", "TN", 0.03),
]

CHANNELS = {
    "season_ticket_holder": ["ticket_rep", "renewal_campaign", "website"],
    "mini_plan_buyer": ["email_campaign", "website", "ticket_rep"],
    "family_buyer": ["organic_social", "email_campaign", "website", "referral"],
    "casual_single_game": ["website", "walk_up", "paid_social", "organic_social"],
    "promo_chaser": ["email_campaign", "organic_social", "paid_social"],
    "group_buyer": ["group_sales_rep", "community_event", "website"],
    "corporate_group": ["ticket_rep", "group_sales_rep", "sponsorship_relationship"],
    "out_of_town_visitor": ["website", "walk_up", "referral"],
}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def weighted_choice(items):
    total = sum(weight for _, weight in items)

    if total <= 0:
        return items[0][0]

    r = random.uniform(0, total)
    upto = 0

    for item, weight in items:
        upto += weight
        if upto >= r:
            return item

    return items[-1][0]


def choose_city():
    city_state_options = [
        ((city, state), weight)
        for city, state, weight in CITIES
    ]

    city, state = weighted_choice(city_state_options)
    return city, state


def load_promo_summary():
    promo_map = defaultdict(lambda: {
        "has_fireworks": 0,
        "has_giveaway": 0,
        "has_theme_night": 0,
        "has_weekly_promo": 0,
        "has_group_sales": 0,
        "has_community": 0,
        "has_appearance": 0,
        "has_jersey_auction": 0,
        "promo_categories": set(),
    })

    for year in [2023, 2024, 2025]:
        path = RAW_DIR / f"promotions_{year}.csv"
        rows = read_csv(path)

        for row in rows:
            key = (row["season"], row["game_date"])

            promo_map[key]["has_fireworks"] = max(
                promo_map[key]["has_fireworks"],
                int(row["is_fireworks"])
            )
            promo_map[key]["has_giveaway"] = max(
                promo_map[key]["has_giveaway"],
                int(row["is_giveaway"])
            )
            promo_map[key]["has_theme_night"] = max(
                promo_map[key]["has_theme_night"],
                int(row["is_theme_night"])
            )
            promo_map[key]["has_weekly_promo"] = max(
                promo_map[key]["has_weekly_promo"],
                int(row["is_weekly_promo"])
            )
            promo_map[key]["has_group_sales"] = max(
                promo_map[key]["has_group_sales"],
                int(row["is_group_sales"])
            )
            promo_map[key]["has_community"] = max(
                promo_map[key]["has_community"],
                int(row["is_community"])
            )
            promo_map[key]["has_appearance"] = max(
                promo_map[key]["has_appearance"],
                int(row["is_appearance"])
            )
            promo_map[key]["has_jersey_auction"] = max(
                promo_map[key]["has_jersey_auction"],
                int(row["is_jersey_auction"])
            )

            promo_map[key]["promo_categories"].add(row["promo_category"])

    return promo_map


def adjusted_segment_weights(game_row, promo_info):
    weights = {}

    for segment, config in SEGMENTS.items():
        weights[segment] = config["base_weight"]

    day = game_row["planned_day_of_week"]

    if day in {"Friday", "Saturday", "Sunday"}:
        weights["family_buyer"] *= 1.25
        weights["promo_chaser"] *= 1.20
        weights["casual_single_game"] *= 1.10

    if day in {"Tuesday", "Wednesday", "Thursday"}:
        weights["mini_plan_buyer"] *= 1.15
        weights["casual_single_game"] *= 1.10

    if promo_info["has_fireworks"]:
        weights["family_buyer"] *= 1.35
        weights["promo_chaser"] *= 1.25

    if promo_info["has_giveaway"]:
        weights["promo_chaser"] *= 1.40
        weights["family_buyer"] *= 1.15

    if promo_info["has_theme_night"]:
        weights["promo_chaser"] *= 1.25
        weights["casual_single_game"] *= 1.10

    if promo_info["has_group_sales"]:
        weights["group_buyer"] *= 1.35
        weights["corporate_group"] *= 1.20

    if promo_info["has_community"]:
        weights["family_buyer"] *= 1.15
        weights["group_buyer"] *= 1.20

    return list(weights.items())


def favorite_promo_for_segment(segment):
    mapping = {
        "season_ticket_holder": "team_affinity",
        "mini_plan_buyer": "weekend_games",
        "family_buyer": "fireworks",
        "casual_single_game": "theme_night",
        "promo_chaser": "giveaway",
        "group_buyer": "group_sales",
        "corporate_group": "corporate_group",
        "out_of_town_visitor": "special_event",
    }
    return mapping.get(segment, "general")


def make_fan(fan_number, segment, first_seen_date):
    city, state = choose_city()
    fan_id = f"FAN{fan_number:07d}"
    household_id = f"HH{fan_number:07d}"

    return {
        "fan_id": fan_id,
        "household_id": household_id,
        "fan_segment": segment,
        "city": city,
        "state": state,
        "acquisition_channel": random.choice(CHANNELS[segment]),
        "first_seen_date": first_seen_date,
        "email_opt_in": 1 if random.random() < 0.82 else 0,
        "sms_opt_in": 1 if random.random() < 0.38 else 0,
        "favorite_promo_category": favorite_promo_for_segment(segment),
        "synthetic_model_version": "crm_v1_attendance_calibrated",
    }


def choose_or_create_fan(segment, planned_game_date, fans, segment_pools, fan_order_counts):
    use_existing = (
        segment_pools[segment]
        and random.random() < SEGMENTS[segment]["existing_prob"]
    )

    if use_existing:
        fan_id = random.choice(segment_pools[segment])
        return fan_id

    fan_number = len(fans) + 1
    fan = make_fan(fan_number, segment, planned_game_date)
    fans[fan["fan_id"]] = fan
    segment_pools[segment].append(fan["fan_id"])
    fan_order_counts[fan["fan_id"]] = 0

    return fan["fan_id"]


def get_order_quantity(segment, remaining):
    low, high = SEGMENTS[segment]["qty_range"]

    if remaining <= low:
        return remaining

    high = min(high, remaining)
    return random.randint(low, high)


def get_order_date(planned_game_date, segment):
    start_days, end_days = SEGMENTS[segment]["lead_days"]
    days_before = random.randint(start_days, end_days)
    game_date = datetime.strptime(planned_game_date, "%Y-%m-%d")
    order_date = game_date - timedelta(days=days_before)
    return order_date.strftime("%Y-%m-%d")


def main():
    attendance_rows = read_csv(ATTENDANCE_FILE)
    promo_map = load_promo_summary()

    attendance_rows.sort(
        key=lambda row: (int(row["season"]), row["planned_game_date"], row["game_id"])
    )

    fans = {}
    segment_pools = defaultdict(list)
    fan_order_counts = defaultdict(int)

    orders = []
    order_number = 1

    for game in attendance_rows:
        control_attendance = int(game["attendance"])
        remaining = control_attendance

        promo_info = promo_map[(game["season"], game["planned_game_date"])]
        segment_weights = adjusted_segment_weights(game, promo_info)

        while remaining > 0:
            segment = weighted_choice(segment_weights)
            qty = get_order_quantity(segment, remaining)

            fan_id = choose_or_create_fan(
                segment,
                game["planned_game_date"],
                fans,
                segment_pools,
                fan_order_counts
            )

            buyer_game_number = fan_order_counts[fan_id] + 1
            is_repeat_buyer = 1 if buyer_game_number > 1 else 0

            base_price = SEGMENTS[segment]["price"]
            price_multiplier = random.uniform(0.90, 1.12)
            estimated_revenue = round(qty * base_price * price_multiplier, 2)

            order = {
                "order_id": f"ORD{order_number:09d}",
                "fan_id": fan_id,
                "game_id": game["game_id"],
                "season": game["season"],
                "planned_game_date": game["planned_game_date"],
                "actual_game_date": game["actual_game_date"],
                "order_date": get_order_date(game["planned_game_date"], segment),
                "ticket_quantity": qty,
                "ticket_type": SEGMENTS[segment]["ticket_type"],
                "sales_channel": random.choice(CHANNELS[segment]),
                "estimated_ticket_revenue": f"{estimated_revenue:.2f}",
                "is_group_order": SEGMENTS[segment]["group_order"],
                "is_repeat_buyer": is_repeat_buyer,
                "buyer_game_number": buyer_game_number,
                "buyer_segment_at_purchase": segment,
                "attendance_control_total": control_attendance,
                "synthetic_model_version": "crm_v1_attendance_calibrated",
            }

            orders.append(order)

            fan_order_counts[fan_id] += 1
            order_number += 1
            remaining -= qty

    fan_rows = list(fans.values())

    fan_fieldnames = [
        "fan_id",
        "household_id",
        "fan_segment",
        "city",
        "state",
        "acquisition_channel",
        "first_seen_date",
        "email_opt_in",
        "sms_opt_in",
        "favorite_promo_category",
        "synthetic_model_version",
    ]

    order_fieldnames = [
        "order_id",
        "fan_id",
        "game_id",
        "season",
        "planned_game_date",
        "actual_game_date",
        "order_date",
        "ticket_quantity",
        "ticket_type",
        "sales_channel",
        "estimated_ticket_revenue",
        "is_group_order",
        "is_repeat_buyer",
        "buyer_game_number",
        "buyer_segment_at_purchase",
        "attendance_control_total",
        "synthetic_model_version",
    ]

    write_csv(FANS_OUT, fan_rows, fan_fieldnames)
    write_csv(ORDERS_OUT, orders, order_fieldnames)

    ticket_qty_by_game = defaultdict(int)
    control_by_game = {}

    for row in attendance_rows:
        control_by_game[row["game_id"]] = int(row["attendance"])

    for order in orders:
        ticket_qty_by_game[order["game_id"]] += int(order["ticket_quantity"])

    mismatches = []
    for game_id, control_total in control_by_game.items():
        synthetic_total = ticket_qty_by_game.get(game_id, 0)
        if synthetic_total != control_total:
            mismatches.append((game_id, control_total, synthetic_total))

    total_control = sum(control_by_game.values())
    total_synthetic = sum(int(order["ticket_quantity"]) for order in orders)

    summary_lines = []
    summary_lines.append("SYNTHETIC CRM GENERATION SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append(f"Fans created: {len(fan_rows):,}")
    summary_lines.append(f"Ticket orders created: {len(orders):,}")
    summary_lines.append(f"Control attendance total: {total_control:,}")
    summary_lines.append(f"Synthetic ticket quantity total: {total_synthetic:,}")
    summary_lines.append(f"Game-level attendance mismatches: {len(mismatches):,}")

    summary_lines.append("")
    summary_lines.append("ORDERS BY SEASON")
    summary_lines.append("=" * 60)

    orders_by_season = Counter(order["season"] for order in orders)
    ticket_qty_by_season = defaultdict(int)

    for order in orders:
        ticket_qty_by_season[order["season"]] += int(order["ticket_quantity"])

    for season in sorted(orders_by_season):
        summary_lines.append(
            f"{season}: orders={orders_by_season[season]:,}, tickets={ticket_qty_by_season[season]:,}"
        )

    summary_lines.append("")
    summary_lines.append("FANS BY SEGMENT")
    summary_lines.append("=" * 60)

    fans_by_segment = Counter(fan["fan_segment"] for fan in fan_rows)
    for segment, count in fans_by_segment.most_common():
        summary_lines.append(f"{segment}: {count:,}")

    summary_lines.append("")
    summary_lines.append("ORDERS BY SEGMENT")
    summary_lines.append("=" * 60)

    orders_by_segment = Counter(order["buyer_segment_at_purchase"] for order in orders)
    for segment, count in orders_by_segment.most_common():
        summary_lines.append(f"{segment}: {count:,}")

    if mismatches:
        summary_lines.append("")
        summary_lines.append("MISMATCHES")
        summary_lines.append("=" * 60)
        for game_id, control, synthetic in mismatches[:25]:
            summary_lines.append(f"{game_id}: control={control}, synthetic={synthetic}")

    QC_DIR.mkdir(parents=True, exist_ok=True)
    QC_OUT.write_text("\n".join(summary_lines), encoding="utf-8")

    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
