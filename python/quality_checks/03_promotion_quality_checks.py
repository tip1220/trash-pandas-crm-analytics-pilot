import csv
from pathlib import Path
from collections import Counter

games_path = Path("data/public/games.csv")
promotions_path = Path("data/public/promotions.csv")
source_log_path = Path("data/public/public_source_log.csv")
output_path = Path("data/processed/promotion_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

games = read_csv(games_path)
promotions = read_csv(promotions_path)
sources = read_csv(source_log_path)

game_ids = {row["game_id"] for row in games}
source_ids = {row["source_id"] for row in sources}

checks = []

def add_check(check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

total_rows = len(promotions)

add_check(
    "total_promotion_rows",
    "Count total promotion rows",
    "> 0",
    str(total_rows),
    "PASS" if total_rows > 0 else "FAIL"
)

promo_ids = [row["promo_id"] for row in promotions]
duplicate_promo_ids = [promo_id for promo_id, count in Counter(promo_ids).items() if count > 1]

add_check(
    "duplicate_promo_ids",
    "Check duplicate promo_id values",
    "0",
    str(len(duplicate_promo_ids)),
    "PASS" if len(duplicate_promo_ids) == 0 else "FAIL"
)

missing_game_id = [row for row in promotions if not row["game_id"]]

add_check(
    "missing_game_id",
    "Check all promotion rows have game_id",
    "0",
    str(len(missing_game_id)),
    "PASS" if len(missing_game_id) == 0 else "FAIL"
)

invalid_game_id = [row for row in promotions if row["game_id"] not in game_ids]

add_check(
    "invalid_game_id",
    "Check all promotion game_id values exist in games.csv",
    "0",
    str(len(invalid_game_id)),
    "PASS" if len(invalid_game_id) == 0 else "FAIL"
)

missing_source_id = [row for row in promotions if not row["source_id"]]

add_check(
    "missing_source_id",
    "Check all promotion rows have source_id",
    "0",
    str(len(missing_source_id)),
    "PASS" if len(missing_source_id) == 0 else "FAIL"
)

invalid_source_id = [row for row in promotions if row["source_id"] not in source_ids]

add_check(
    "invalid_source_id",
    "Check all promotion source_id values exist in public_source_log.csv",
    "0",
    str(len(invalid_source_id)),
    "PASS" if len(invalid_source_id) == 0 else "FAIL"
)

missing_promo_name = [row for row in promotions if not row["promo_name"]]

add_check(
    "missing_promo_name",
    "Check all promotion rows have promo_name",
    "0",
    str(len(missing_promo_name)),
    "PASS" if len(missing_promo_name) == 0 else "FAIL"
)

missing_promo_category = [row for row in promotions if not row["promo_category"]]

add_check(
    "missing_promo_category",
    "Check all promotion rows have promo_category",
    "0",
    str(len(missing_promo_category)),
    "PASS" if len(missing_promo_category) == 0 else "FAIL"
)

season_counts = Counter(row["season"] for row in promotions)

for season in ["2023", "2024", "2025"]:
    actual = season_counts.get(season, 0)
    add_check(
        f"{season}_promotion_rows",
        f"Check promotion rows exist for {season}",
        "> 0",
        str(actual),
        "PASS" if actual > 0 else "FAIL"
    )

promo_categories = Counter(row["promo_category"] for row in promotions)

for category in ["weekly_promo", "fireworks", "family"]:
    actual = promo_categories.get(category, 0)
    add_check(
        f"{category}_category_rows",
        f"Check {category} promotion rows exist",
        "> 0",
        str(actual),
        "PASS" if actual > 0 else "REVIEW"
    )

boolean_fields = [
    "primary_promo_flag",
    "sponsor_attached_flag",
    "giveaway_flag",
    "fireworks_flag",
    "theme_night_flag",
    "family_flag",
    "dog_day_flag",
    "jersey_auction_flag",
    "public_data_flag"
]

bad_boolean_values = []

for row in promotions:
    for field in boolean_fields:
        if row[field] not in ["True", "False", "true", "false", "TRUE", "FALSE"]:
            bad_boolean_values.append((row["promo_id"], field, row[field]))

add_check(
    "boolean_field_values",
    "Check boolean-like fields use true/false values",
    "0 invalid values",
    str(len(bad_boolean_values)),
    "PASS" if len(bad_boolean_values) == 0 else "FAIL"
)

game_promo_counts = Counter(row["game_id"] for row in promotions)
games_with_promotions = len(game_promo_counts)

add_check(
    "games_with_promotions",
    "Count games with at least one promotion row",
    "> 0",
    str(games_with_promotions),
    "PASS" if games_with_promotions > 0 else "FAIL"
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