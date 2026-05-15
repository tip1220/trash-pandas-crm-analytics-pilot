import csv
import random
from pathlib import Path
from collections import Counter

random.seed(48)

games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")

output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

activations_path = output_dir / "sponsorship_activations.csv"
summary_path = output_dir / "sponsorship_activation_generation_summary.csv"

sponsor_categories = [
    ("healthcare", 0.16),
    ("auto", 0.14),
    ("restaurant", 0.14),
    ("banking", 0.10),
    ("grocery", 0.09),
    ("insurance", 0.08),
    ("local_business", 0.14),
    ("education", 0.07),
    ("nonprofit", 0.05),
    ("technology", 0.03)
]

activation_types = [
    ("giveaway", 0.18),
    ("theme_night", 0.18),
    ("concourse_table", 0.15),
    ("signage", 0.14),
    ("digital", 0.12),
    ("community", 0.10),
    ("hospitality", 0.08),
    ("on_field_recognition", 0.05)
]

activation_locations = [
    ("ballpark", 0.34),
    ("concourse", 0.26),
    ("field", 0.12),
    ("digital", 0.14),
    ("suite_level", 0.08),
    ("pregame", 0.06)
]

activation_goals = [
    ("awareness", 0.34),
    ("community", 0.20),
    ("lead_capture", 0.14),
    ("hospitality", 0.12),
    ("sales", 0.10),
    ("brand_affinity", 0.10)
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

def activation_probability(game, promo):
    probability = 0.18

    promo_category = promo["promo_category"] if promo else ""
    promo_type = promo["promo_type"] if promo else ""

    if game["day_of_week"] in ["Friday", "Saturday"]:
        probability += 0.10

    if promo_category in ["fireworks", "family", "bobblehead_giveaway", "jersey_giveaway"]:
        probability += 0.18

    if promo_type in ["dog_day", "kids_run_bases", "military_recognition", "ladies_night"]:
        probability += 0.10

    if promo and promo["sponsor_attached_flag"].strip().lower() == "true":
        probability += 0.35

    return min(probability, 0.85)

def choose_activation_type(promo):
    if promo:
        if promo["giveaway_flag"].strip().lower() == "true":
            return weighted_choice([("giveaway", 0.55), ("concourse_table", 0.15), ("digital", 0.15), ("signage", 0.15)])

        if promo["theme_night_flag"].strip().lower() == "true":
            return weighted_choice([("theme_night", 0.45), ("concourse_table", 0.20), ("digital", 0.20), ("signage", 0.15)])

        if promo["family_flag"].strip().lower() == "true":
            return weighted_choice([("community", 0.30), ("concourse_table", 0.25), ("theme_night", 0.20), ("digital", 0.15), ("signage", 0.10)])

        if promo["fireworks_flag"].strip().lower() == "true":
            return weighted_choice([("signage", 0.30), ("digital", 0.25), ("hospitality", 0.20), ("on_field_recognition", 0.15), ("concourse_table", 0.10)])

    return weighted_choice(activation_types)

games = read_csv(games_path)
promotions = read_csv(promotions_path)

promotions_by_game = {}

for promo in promotions:
    promotions_by_game.setdefault(promo["game_id"], []).append(promo)

activation_rows = []
activation_counter = 1

for game in games:
    game_promos = promotions_by_game.get(game["game_id"], [])

    if not game_promos:
        if random.random() < 0.08:
            game_promos = [None]
        else:
            continue

    for promo in game_promos:
        probability = activation_probability(game, promo)

        if random.random() > probability:
            continue

        sponsor_category = weighted_choice(sponsor_categories)
        sponsor_id = f"SPONSOR_{random.randint(1, 85):03d}"
        activation_type = choose_activation_type(promo)

        if activation_type == "digital":
            activation_location = "digital"
        elif activation_type == "hospitality":
            activation_location = weighted_choice([("suite_level", 0.55), ("ballpark", 0.25), ("pregame", 0.20)])
        elif activation_type == "concourse_table":
            activation_location = "concourse"
        elif activation_type == "on_field_recognition":
            activation_location = "field"
        else:
            activation_location = weighted_choice(activation_locations)

        if sponsor_category in ["healthcare", "education", "nonprofit"]:
            activation_goal = weighted_choice([("community", 0.42), ("awareness", 0.28), ("lead_capture", 0.15), ("brand_affinity", 0.15)])
        elif sponsor_category in ["auto", "banking", "insurance", "technology"]:
            activation_goal = weighted_choice([("lead_capture", 0.30), ("awareness", 0.25), ("sales", 0.20), ("hospitality", 0.15), ("brand_affinity", 0.10)])
        else:
            activation_goal = weighted_choice(activation_goals)

        activation_rows.append({
            "activation_id": f"ACT_{activation_counter:06d}",
            "game_id": game["game_id"],
            "promo_id": "" if promo is None else promo["promo_id"],
            "sponsor_id": sponsor_id,
            "sponsor_category": sponsor_category,
            "activation_type": activation_type,
            "activation_location": activation_location,
            "activation_goal": activation_goal,
            "sponsor_attached_flag": True,
            "synthetic_data_flag": True,
            "notes": "Synthetic sponsorship context only; not used for sponsorship ROI analysis"
        })

        activation_counter += 1

fields = [
    "activation_id",
    "game_id",
    "promo_id",
    "sponsor_id",
    "sponsor_category",
    "activation_type",
    "activation_location",
    "activation_goal",
    "sponsor_attached_flag",
    "synthetic_data_flag",
    "notes"
]

write_csv(activations_path, activation_rows, fields)

category_counts = Counter(row["sponsor_category"] for row in activation_rows)
activation_type_counts = Counter(row["activation_type"] for row in activation_rows)
goal_counts = Counter(row["activation_goal"] for row in activation_rows)

summary_rows = [
    {"metric": "sponsorship_activation_rows", "value": len(activation_rows)},
    {"metric": "unique_sponsors", "value": len(set(row["sponsor_id"] for row in activation_rows))},
    {"metric": "games_with_sponsor_activation", "value": len(set(row["game_id"] for row in activation_rows))},
    {"metric": "promo_linked_activations", "value": sum(1 for row in activation_rows if row["promo_id"])}
]

for category, count in sorted(category_counts.items()):
    summary_rows.append({"metric": f"sponsor_category_count_{category}", "value": count})

for activation_type, count in sorted(activation_type_counts.items()):
    summary_rows.append({"metric": f"activation_type_count_{activation_type}", "value": count})

for goal, count in sorted(goal_counts.items()):
    summary_rows.append({"metric": f"activation_goal_count_{goal}", "value": count})

write_csv(summary_path, summary_rows, ["metric", "value"])

print(f"Wrote {activations_path} with {len(activation_rows)} activations")
print(f"Wrote {summary_path}")