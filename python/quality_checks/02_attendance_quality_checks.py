import csv
from pathlib import Path
from collections import Counter

games_path = Path("data/public/games.csv")
attendance_path = Path("data/public/attendance.csv")
source_log_path = Path("data/public/public_source_log.csv")
output_path = Path("data/processed/attendance_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

games = read_csv(games_path)
attendance = read_csv(attendance_path)
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

total_rows = len(attendance)

add_check(
    "total_attendance_rows",
    "Count total attendance rows",
    "207",
    str(total_rows),
    "PASS" if total_rows == 207 else "FAIL"
)

season_counts = Counter(row["season"] for row in attendance)

for season in ["2023", "2024", "2025"]:
    actual = season_counts.get(season, 0)
    add_check(
        f"{season}_attendance_rows",
        f"Count attendance rows for {season}",
        "69",
        str(actual),
        "PASS" if actual == 69 else "FAIL"
    )

attendance_ids = [row["attendance_id"] for row in attendance]
duplicate_attendance_ids = [
    attendance_id for attendance_id, count in Counter(attendance_ids).items() if count > 1
]

add_check(
    "duplicate_attendance_ids",
    "Check duplicate attendance_id values",
    "0",
    str(len(duplicate_attendance_ids)),
    "PASS" if len(duplicate_attendance_ids) == 0 else "FAIL"
)

missing_game_id = [row for row in attendance if not row["game_id"]]

add_check(
    "missing_game_id",
    "Check all attendance rows have game_id",
    "0",
    str(len(missing_game_id)),
    "PASS" if len(missing_game_id) == 0 else "FAIL"
)

invalid_game_id = [row for row in attendance if row["game_id"] not in game_ids]

add_check(
    "invalid_game_id",
    "Check all attendance game_id values exist in games.csv",
    "0",
    str(len(invalid_game_id)),
    "PASS" if len(invalid_game_id) == 0 else "FAIL"
)

matched_rows = [row for row in attendance if row["attendance_match_status"] == "matched"]
unmatched_rows = [row for row in attendance if row["attendance_match_status"] == "unmatched"]

add_check(
    "matched_attendance_rows",
    "Count matched attendance rows",
    "Review only",
    str(len(matched_rows)),
    "PASS" if len(matched_rows) > 0 else "FAIL"
)

add_check(
    "unmatched_attendance_rows",
    "Count unmatched attendance rows",
    "Allowed but should be documented",
    str(len(unmatched_rows)),
    "REVIEW" if len(unmatched_rows) > 0 else "PASS"
)

missing_attendance_on_matched = [
    row for row in matched_rows if not row["announced_attendance"]
]

add_check(
    "missing_attendance_on_matched_rows",
    "Check matched rows have announced_attendance",
    "0",
    str(len(missing_attendance_on_matched)),
    "PASS" if len(missing_attendance_on_matched) == 0 else "FAIL"
)

attendance_on_unmatched = [
    row for row in unmatched_rows if row["announced_attendance"]
]

add_check(
    "attendance_present_on_unmatched_rows",
    "Check unmatched rows do not have announced_attendance",
    "0",
    str(len(attendance_on_unmatched)),
    "PASS" if len(attendance_on_unmatched) == 0 else "FAIL"
)

invalid_attendance_sources = [
    row for row in matched_rows
    if row["attendance_source"] and row["attendance_source"] not in source_ids
]

add_check(
    "invalid_attendance_source",
    "Check attendance_source values exist in public_source_log.csv",
    "0",
    str(len(invalid_attendance_sources)),
    "PASS" if len(invalid_attendance_sources) == 0 else "FAIL"
)

bad_attendance_values = []

for row in matched_rows:
    try:
        value = int(float(row["announced_attendance"]))
        if value <= 0:
            bad_attendance_values.append(row)
    except ValueError:
        bad_attendance_values.append(row)

add_check(
    "bad_attendance_values",
    "Check matched announced_attendance values are positive numbers",
    "0",
    str(len(bad_attendance_values)),
    "PASS" if len(bad_attendance_values) == 0 else "FAIL"
)

season_totals = {}

for season in ["2023", "2024", "2025"]:
    total = 0
    for row in matched_rows:
        if row["season"] == season and row["announced_attendance"]:
            total += int(float(row["announced_attendance"]))
    season_totals[season] = total

expected_public_totals = {
    "2023": 314306,
    "2024": 319417,
    "2025": 275423
}

for season, expected_total in expected_public_totals.items():
    actual_total = season_totals.get(season, 0)
    difference = actual_total - expected_total
    status = "PASS" if difference == 0 else "REVIEW"
    add_check(
        f"{season}_attendance_total_reconciliation",
        f"Compare matched attendance total to public season attendance total for {season}",
        str(expected_total),
        f"{actual_total} | difference={difference}",
        status
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