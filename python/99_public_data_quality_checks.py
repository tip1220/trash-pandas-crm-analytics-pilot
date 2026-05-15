import csv
from pathlib import Path
from collections import Counter, defaultdict

games_path = Path("data/public/games.csv")
source_log_path = Path("data/public/public_source_log.csv")
output_path = Path("data/processed/public_data_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

games = read_csv(games_path)
sources = read_csv(source_log_path)

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

total_rows = len(games)
add_check(
    "total_game_rows",
    "Count total game rows",
    "207",
    str(total_rows),
    "PASS" if total_rows == 207 else "FAIL"
)

season_counts = Counter(row["season"] for row in games)
for season in ["2023", "2024", "2025"]:
    actual = season_counts.get(season, 0)
    add_check(
        f"{season}_home_game_count",
        f"Count home games for {season}",
        "69",
        str(actual),
        "PASS" if actual == 69 else "FAIL"
    )

game_ids = [row["game_id"] for row in games]
duplicate_game_ids = [game_id for game_id, count in Counter(game_ids).items() if count > 1]
add_check(
    "duplicate_game_ids",
    "Check duplicate game_id values",
    "0",
    str(len(duplicate_game_ids)),
    "PASS" if len(duplicate_game_ids) == 0 else "FAIL"
)

game_keys = [
    (row["season"], row["game_date"], row["opponent"])
    for row in games
]
duplicate_game_keys = [key for key, count in Counter(game_keys).items() if count > 1]
add_check(
    "duplicate_season_date_opponent",
    "Check duplicate season/game_date/opponent values",
    "0",
    str(len(duplicate_game_keys)),
    "PASS" if len(duplicate_game_keys) == 0 else "FAIL"
)

non_home_games = [row for row in games if row["home_away"] != "Home"]
add_check(
    "home_games_only",
    "Check all games are home games",
    "0 non-home rows",
    str(len(non_home_games)),
    "PASS" if len(non_home_games) == 0 else "FAIL"
)

missing_homestand = [row for row in games if not row["homestand_id"]]
add_check(
    "missing_homestand_id",
    "Check all games have homestand_id",
    "0",
    str(len(missing_homestand)),
    "PASS" if len(missing_homestand) == 0 else "FAIL"
)

missing_source_id = [row for row in games if not row["source_id"]]
add_check(
    "missing_source_id",
    "Check all games have source_id",
    "0",
    str(len(missing_source_id)),
    "PASS" if len(missing_source_id) == 0 else "FAIL"
)

invalid_source_id = [row for row in games if row["source_id"] not in source_ids]
add_check(
    "invalid_source_id",
    "Check all game source_id values exist in public_source_log",
    "0",
    str(len(invalid_source_id)),
    "PASS" if len(invalid_source_id) == 0 else "FAIL"
)

missing_dates = [row for row in games if not row["game_date"]]
add_check(
    "missing_game_date",
    "Check all games have game_date",
    "0",
    str(len(missing_dates)),
    "PASS" if len(missing_dates) == 0 else "FAIL"
)

missing_opponents = [row for row in games if not row["opponent"]]
add_check(
    "missing_opponent",
    "Check all games have opponent",
    "0",
    str(len(missing_opponents)),
    "PASS" if len(missing_opponents) == 0 else "FAIL"
)

homestand_counts = defaultdict(int)
for row in games:
    homestand_counts[row["homestand_id"]] += 1

bad_homestand_counts = {
    homestand_id: count
    for homestand_id, count in homestand_counts.items()
    if count < 3 or count > 12
}

add_check(
    "homestand_size_range",
    "Check homestand sizes are reasonable",
    "3-12 games",
    str(dict(sorted(bad_homestand_counts.items()))),
    "PASS" if len(bad_homestand_counts) == 0 else "REVIEW"
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