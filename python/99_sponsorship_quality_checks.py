import csv
from pathlib import Path
from collections import Counter

activations_path = Path("data/synthetic/sponsorship_activations.csv")
games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
output_path = Path("data/synthetic/sponsorship_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def add_check(checks, check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

activations = read_csv(activations_path)
games = read_csv(games_path)
promotions = read_csv(promotions_path)

game_ids = {row["game_id"] for row in games}
promo_ids = {row["promo_id"] for row in promotions}

checks = []

add_check(
    checks,
    "sponsorship_activation_rows",
    "Count sponsorship activation rows",
    "> 0",
    str(len(activations)),
    "PASS" if len(activations) > 0 else "FAIL"
)

activation_ids = [row["activation_id"] for row in activations]

duplicate_activation_ids = [
    activation_id for activation_id, count in Counter(activation_ids).items() if count > 1
]

add_check(
    checks,
    "duplicate_activation_ids",
    "Check duplicate activation_id values",
    "0",
    str(len(duplicate_activation_ids)),
    "PASS" if len(duplicate_activation_ids) == 0 else "FAIL"
)

invalid_game_ids = [
    row for row in activations if row["game_id"] not in game_ids
]

add_check(
    checks,
    "invalid_activation_game_ids",
    "Check sponsorship game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_game_ids)),
    "PASS" if len(invalid_game_ids) == 0 else "FAIL"
)

invalid_promo_ids = [
    row for row in activations
    if row["promo_id"].strip() != "" and row["promo_id"] not in promo_ids
]

add_check(
    checks,
    "invalid_activation_promo_ids",
    "Check nonblank sponsorship promo_id values exist in promotions_clean.csv",
    "0",
    str(len(invalid_promo_ids)),
    "PASS" if len(invalid_promo_ids) == 0 else "FAIL"
)

missing_sponsor_ids = [
    row for row in activations if not row["sponsor_id"].strip()
]

add_check(
    checks,
    "missing_sponsor_ids",
    "Check every activation has sponsor_id",
    "0",
    str(len(missing_sponsor_ids)),
    "PASS" if len(missing_sponsor_ids) == 0 else "FAIL"
)

valid_sponsor_categories = {
    "healthcare",
    "auto",
    "restaurant",
    "banking",
    "grocery",
    "insurance",
    "local_business",
    "education",
    "nonprofit",
    "technology"
}

invalid_sponsor_categories = [
    row for row in activations if row["sponsor_category"] not in valid_sponsor_categories
]

add_check(
    checks,
    "invalid_sponsor_categories",
    "Check sponsor_category values",
    "0",
    str(len(invalid_sponsor_categories)),
    "PASS" if len(invalid_sponsor_categories) == 0 else "FAIL"
)

valid_activation_types = {
    "giveaway",
    "theme_night",
    "concourse_table",
    "signage",
    "digital",
    "community",
    "hospitality",
    "on_field_recognition"
}

invalid_activation_types = [
    row for row in activations if row["activation_type"] not in valid_activation_types
]

add_check(
    checks,
    "invalid_activation_types",
    "Check activation_type values",
    "0",
    str(len(invalid_activation_types)),
    "PASS" if len(invalid_activation_types) == 0 else "FAIL"
)

valid_activation_locations = {
    "ballpark",
    "concourse",
    "field",
    "digital",
    "suite_level",
    "pregame"
}

invalid_activation_locations = [
    row for row in activations if row["activation_location"] not in valid_activation_locations
]

add_check(
    checks,
    "invalid_activation_locations",
    "Check activation_location values",
    "0",
    str(len(invalid_activation_locations)),
    "PASS" if len(invalid_activation_locations) == 0 else "FAIL"
)

valid_activation_goals = {
    "awareness",
    "community",
    "lead_capture",
    "hospitality",
    "sales",
    "brand_affinity"
}

invalid_activation_goals = [
    row for row in activations if row["activation_goal"] not in valid_activation_goals
]

add_check(
    checks,
    "invalid_activation_goals",
    "Check activation_goal values",
    "0",
    str(len(invalid_activation_goals)),
    "PASS" if len(invalid_activation_goals) == 0 else "FAIL"
)

valid_boolean_values = {"True", "False", "true", "false", "TRUE", "FALSE"}

bad_boolean_values = []

for row in activations:
    for field in ["sponsor_attached_flag", "synthetic_data_flag"]:
        if row[field] not in valid_boolean_values:
            bad_boolean_values.append((row["activation_id"], field, row[field]))

add_check(
    checks,
    "boolean_field_values",
    "Check boolean-like sponsorship fields use true/false values",
    "0",
    str(len(bad_boolean_values)),
    "PASS" if len(bad_boolean_values) == 0 else "FAIL"
)

games_with_activation = len(set(row["game_id"] for row in activations))
unique_sponsors = len(set(row["sponsor_id"] for row in activations))
promo_linked_activations = sum(1 for row in activations if row["promo_id"].strip())

add_check(
    checks,
    "games_with_sponsor_activation",
    "Report games with sponsorship activation",
    "Review only",
    str(games_with_activation),
    "PASS"
)

add_check(
    checks,
    "unique_sponsors",
    "Report unique sponsor count",
    "Review only",
    str(unique_sponsors),
    "PASS"
)

add_check(
    checks,
    "promo_linked_activations",
    "Report promo-linked sponsorship activations",
    "> 0",
    str(promo_linked_activations),
    "PASS" if promo_linked_activations > 0 else "REVIEW"
)

category_counts = Counter(row["sponsor_category"] for row in activations)
activation_type_counts = Counter(row["activation_type"] for row in activations)
goal_counts = Counter(row["activation_goal"] for row in activations)

for category in sorted(valid_sponsor_categories):
    add_check(
        checks,
        f"sponsor_category_exists_{category}",
        f"Check sponsor category exists: {category}",
        "> 0",
        str(category_counts.get(category, 0)),
        "PASS" if category_counts.get(category, 0) > 0 else "REVIEW"
    )

for activation_type in sorted(valid_activation_types):
    add_check(
        checks,
        f"activation_type_exists_{activation_type}",
        f"Check activation type exists: {activation_type}",
        "> 0",
        str(activation_type_counts.get(activation_type, 0)),
        "PASS" if activation_type_counts.get(activation_type, 0) > 0 else "REVIEW"
    )

for goal in sorted(valid_activation_goals):
    add_check(
        checks,
        f"activation_goal_exists_{goal}",
        f"Check activation goal exists: {goal}",
        "> 0",
        str(goal_counts.get(goal, 0)),
        "PASS" if goal_counts.get(goal, 0) > 0 else "REVIEW"
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