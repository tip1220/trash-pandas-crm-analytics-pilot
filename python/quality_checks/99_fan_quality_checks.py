import csv
from pathlib import Path
from collections import Counter
from datetime import datetime

fans_path = Path("data/synthetic/fans.csv")
segments_path = Path("data/synthetic/fan_segments.csv")
output_path = Path("data/synthetic/fan_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

fans = read_csv(fans_path)
segments = read_csv(segments_path)

checks = []

def add_check(check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

fan_count = len(fans)

add_check(
    "fan_count",
    "Count synthetic fan records",
    "45000",
    str(fan_count),
    "PASS" if fan_count == 45000 else "FAIL"
)

fan_ids = [row["fan_id"] for row in fans]
unique_fan_ids = set(fan_ids)
duplicate_fan_ids = [fan_id for fan_id, count in Counter(fan_ids).items() if count > 1]

add_check(
    "duplicate_fan_ids",
    "Check duplicate fan_id values",
    "0",
    str(len(duplicate_fan_ids)),
    "PASS" if len(duplicate_fan_ids) == 0 else "FAIL"
)

missing_fan_ids = [row for row in fans if not row["fan_id"]]

add_check(
    "missing_fan_ids",
    "Check missing fan_id values",
    "0",
    str(len(missing_fan_ids)),
    "PASS" if len(missing_fan_ids) == 0 else "FAIL"
)

segment_count = len(segments)

add_check(
    "fan_segment_rows",
    "Count fan segment assignment records",
    "> fan count",
    str(segment_count),
    "PASS" if segment_count > fan_count else "FAIL"
)

segment_ids = [row["fan_segment_id"] for row in segments]
duplicate_segment_ids = [
    segment_id for segment_id, count in Counter(segment_ids).items() if count > 1
]

add_check(
    "duplicate_fan_segment_ids",
    "Check duplicate fan_segment_id values",
    "0",
    str(len(duplicate_segment_ids)),
    "PASS" if len(duplicate_segment_ids) == 0 else "FAIL"
)

invalid_segment_fan_ids = [
    row for row in segments if row["fan_id"] not in unique_fan_ids
]

add_check(
    "invalid_segment_fan_ids",
    "Check all fan segment fan_id values exist in fans.csv",
    "0",
    str(len(invalid_segment_fan_ids)),
    "PASS" if len(invalid_segment_fan_ids) == 0 else "FAIL"
)

segment_names = Counter(row["segment_name"] for row in segments)

required_segments = [
    "One-Time Buyer",
    "Occasional Fan",
    "Repeat Single-Game Buyer",
    "Mini Plan Buyer",
    "Season Ticket Holder",
    "Group Buyer",
    "Theme Night Buyer",
    "Family Buyer",
    "Corporate Prospect",
    "High In-Park Spender",
    "Lapsed Fan"
]

for segment_name in required_segments:
    actual = segment_names.get(segment_name, 0)
    add_check(
        f"segment_exists_{segment_name}",
        f"Check segment exists: {segment_name}",
        "> 0",
        str(actual),
        "PASS" if actual > 0 else "FAIL"
    )

lifecycle_counts = Counter(
    row["fan_id"] for row in segments if row["segment_type"] == "lifecycle"
)

fans_without_lifecycle = [
    fan_id for fan_id in unique_fan_ids if lifecycle_counts.get(fan_id, 0) == 0
]

fans_with_multiple_lifecycle = [
    fan_id for fan_id, count in lifecycle_counts.items() if count > 1
]

add_check(
    "fans_without_lifecycle_segment",
    "Check every fan has one lifecycle segment",
    "0",
    str(len(fans_without_lifecycle)),
    "PASS" if len(fans_without_lifecycle) == 0 else "FAIL"
)

add_check(
    "fans_with_multiple_lifecycle_segments",
    "Check fans do not have multiple lifecycle segments",
    "0",
    str(len(fans_with_multiple_lifecycle)),
    "PASS" if len(fans_with_multiple_lifecycle) == 0 else "FAIL"
)

valid_boolean_values = {"True", "False", "true", "false", "TRUE", "FALSE"}

fan_boolean_fields = [
    "email_opt_in_flag",
    "sms_opt_in_flag",
    "family_flag",
    "corporate_flag",
    "youth_sports_flag",
    "synthetic_data_flag"
]

bad_fan_boolean_values = []

for row in fans:
    for field in fan_boolean_fields:
        if row[field] not in valid_boolean_values:
            bad_fan_boolean_values.append((row["fan_id"], field, row[field]))

add_check(
    "fan_boolean_values",
    "Check fan boolean fields use true/false values",
    "0 invalid values",
    str(len(bad_fan_boolean_values)),
    "PASS" if len(bad_fan_boolean_values) == 0 else "FAIL"
)

segment_boolean_fields = [
    "active_flag",
    "synthetic_data_flag"
]

bad_segment_boolean_values = []

for row in segments:
    for field in segment_boolean_fields:
        if row[field] not in valid_boolean_values:
            bad_segment_boolean_values.append((row["fan_segment_id"], field, row[field]))

add_check(
    "segment_boolean_values",
    "Check segment boolean fields use true/false values",
    "0 invalid values",
    str(len(bad_segment_boolean_values)),
    "PASS" if len(bad_segment_boolean_values) == 0 else "FAIL"
)

bad_segment_scores = []

for row in segments:
    try:
        score = int(row["segment_score"])
        if score < 0 or score > 100:
            bad_segment_scores.append(row)
    except ValueError:
        bad_segment_scores.append(row)

add_check(
    "segment_score_range",
    "Check segment scores are between 0 and 100",
    "0 invalid scores",
    str(len(bad_segment_scores)),
    "PASS" if len(bad_segment_scores) == 0 else "FAIL"
)

bad_seen_dates = []

for row in fans:
    try:
        first_seen = datetime.strptime(row["first_seen_date"], "%Y-%m-%d").date()
        last_seen = datetime.strptime(row["last_seen_date"], "%Y-%m-%d").date()
        if last_seen < first_seen:
            bad_seen_dates.append(row)
    except ValueError:
        bad_seen_dates.append(row)

add_check(
    "fan_seen_date_order",
    "Check last_seen_date is not before first_seen_date",
    "0 invalid date rows",
    str(len(bad_seen_dates)),
    "PASS" if len(bad_seen_dates) == 0 else "FAIL"
)

market_counts = Counter(row["market_distance_band"] for row in fans)

for market_band in ["local", "regional", "out_of_market"]:
    actual = market_counts.get(market_band, 0)
    add_check(
        f"market_band_exists_{market_band}",
        f"Check market band exists: {market_band}",
        "> 0",
        str(actual),
        "PASS" if actual > 0 else "FAIL"
    )

synthetic_fan_flags = [row for row in fans if row["synthetic_data_flag"] not in valid_boolean_values]
synthetic_segment_flags = [row for row in segments if row["synthetic_data_flag"] not in valid_boolean_values]

add_check(
    "synthetic_flag_present_fans",
    "Check fans have synthetic data flag",
    "0 invalid values",
    str(len(synthetic_fan_flags)),
    "PASS" if len(synthetic_fan_flags) == 0 else "FAIL"
)

add_check(
    "synthetic_flag_present_segments",
    "Check segments have synthetic data flag",
    "0 invalid values",
    str(len(synthetic_segment_flags)),
    "PASS" if len(synthetic_segment_flags) == 0 else "FAIL"
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