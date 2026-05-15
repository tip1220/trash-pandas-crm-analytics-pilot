import csv
from pathlib import Path
from collections import Counter
from datetime import datetime

engagement_path = Path("data/synthetic/fan_engagement.csv")
fans_path = Path("data/synthetic/fans.csv")
games_path = Path("data/processed/games_clean.csv")
output_path = Path("data/synthetic/fan_engagement_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def to_int(value):
    return int(float(str(value).strip()))

def add_check(checks, check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

engagement = read_csv(engagement_path)
fans = read_csv(fans_path)
games = read_csv(games_path)

fan_ids = {row["fan_id"] for row in fans}
game_ids = {row["game_id"] for row in games}

checks = []

add_check(
    checks,
    "fan_engagement_rows",
    "Count fan engagement rows",
    "> 0",
    str(len(engagement)),
    "PASS" if len(engagement) > 0 else "FAIL"
)

engagement_ids = [row["engagement_id"] for row in engagement]

duplicate_engagement_ids = [
    engagement_id for engagement_id, count in Counter(engagement_ids).items() if count > 1
]

add_check(
    checks,
    "duplicate_engagement_ids",
    "Check duplicate engagement_id values",
    "0",
    str(len(duplicate_engagement_ids)),
    "PASS" if len(duplicate_engagement_ids) == 0 else "FAIL"
)

invalid_fan_ids = [
    row for row in engagement if row["fan_id"] not in fan_ids
]

add_check(
    checks,
    "invalid_engagement_fan_ids",
    "Check engagement fan_id values exist in fans.csv",
    "0",
    str(len(invalid_fan_ids)),
    "PASS" if len(invalid_fan_ids) == 0 else "FAIL"
)

invalid_game_ids = [
    row for row in engagement
    if row["game_id"].strip() != "" and row["game_id"] not in game_ids
]

add_check(
    checks,
    "invalid_engagement_game_ids",
    "Check nonblank engagement game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_game_ids)),
    "PASS" if len(invalid_game_ids) == 0 else "FAIL"
)

missing_campaign_ids = [
    row for row in engagement if not row["campaign_id"].strip()
]

add_check(
    checks,
    "missing_campaign_ids",
    "Check every engagement row has campaign_id",
    "0",
    str(len(missing_campaign_ids)),
    "PASS" if len(missing_campaign_ids) == 0 else "FAIL"
)

missing_campaign_names = [
    row for row in engagement if not row["campaign_name"].strip()
]

add_check(
    checks,
    "missing_campaign_names",
    "Check every engagement row has campaign_name",
    "0",
    str(len(missing_campaign_names)),
    "PASS" if len(missing_campaign_names) == 0 else "FAIL"
)

valid_engagement_types = {
    "email_open",
    "email_click",
    "sms_click",
    "offer_response",
    "survey_response",
    "qr_scan",
    "app_interaction",
    "social_interaction",
    "merch_offer_click",
    "concession_offer_click",
    "group_interest_form",
    "premium_interest_form"
}

invalid_engagement_types = [
    row for row in engagement if row["engagement_type"] not in valid_engagement_types
]

add_check(
    checks,
    "invalid_engagement_types",
    "Check engagement_type values",
    "0",
    str(len(invalid_engagement_types)),
    "PASS" if len(invalid_engagement_types) == 0 else "FAIL"
)

valid_channels = {
    "email",
    "sms",
    "web",
    "app",
    "social",
    "in_park"
}

invalid_channels = [
    row for row in engagement if row["engagement_channel"] not in valid_channels
]

add_check(
    checks,
    "invalid_engagement_channels",
    "Check engagement_channel values",
    "0",
    str(len(invalid_channels)),
    "PASS" if len(invalid_channels) == 0 else "FAIL"
)

bad_scores = []

for row in engagement:
    try:
        score = to_int(row["engagement_score"])

        if score < 1 or score > 100:
            bad_scores.append(row)
    except Exception:
        bad_scores.append(row)

add_check(
    checks,
    "bad_engagement_scores",
    "Check engagement_score is between 1 and 100",
    "0",
    str(len(bad_scores)),
    "PASS" if len(bad_scores) == 0 else "FAIL"
)

bad_dates = []

for row in engagement:
    try:
        datetime.strptime(row["engagement_date"], "%Y-%m-%d")
    except Exception:
        bad_dates.append(row)

add_check(
    checks,
    "bad_engagement_dates",
    "Check engagement_date format",
    "0",
    str(len(bad_dates)),
    "PASS" if len(bad_dates) == 0 else "FAIL"
)

valid_boolean_values = {"True", "False", "true", "false", "TRUE", "FALSE"}

bad_boolean_values = []

for row in engagement:
    for field in ["promo_related_flag", "synthetic_data_flag"]:
        if row[field] not in valid_boolean_values:
            bad_boolean_values.append((row["engagement_id"], field, row[field]))

add_check(
    checks,
    "boolean_field_values",
    "Check boolean-like engagement fields use true/false values",
    "0",
    str(len(bad_boolean_values)),
    "PASS" if len(bad_boolean_values) == 0 else "FAIL"
)

unique_engaged_fans = len(set(row["fan_id"] for row in engagement))
game_linked_rows = sum(1 for row in engagement if row["game_id"].strip())
non_game_campaign_rows = sum(1 for row in engagement if not row["game_id"].strip())
average_engagement_score = sum(to_int(row["engagement_score"]) for row in engagement) / len(engagement)

add_check(
    checks,
    "unique_engaged_fans",
    "Report unique engaged fans",
    "> 0",
    str(unique_engaged_fans),
    "PASS" if unique_engaged_fans > 0 else "FAIL"
)

add_check(
    checks,
    "game_linked_engagement_rows",
    "Report game-linked engagement rows",
    "> 0",
    str(game_linked_rows),
    "PASS" if game_linked_rows > 0 else "FAIL"
)

add_check(
    checks,
    "non_game_campaign_engagement_rows",
    "Report non-game campaign engagement rows",
    "> 0",
    str(non_game_campaign_rows),
    "PASS" if non_game_campaign_rows > 0 else "REVIEW"
)

add_check(
    checks,
    "average_engagement_score",
    "Report average engagement score",
    "5-70",
    f"{average_engagement_score:.2f}",
    "PASS" if 5 <= average_engagement_score <= 70 else "REVIEW"
)

type_counts = Counter(row["engagement_type"] for row in engagement)
channel_counts = Counter(row["engagement_channel"] for row in engagement)

for engagement_type in sorted(valid_engagement_types):
    add_check(
        checks,
        f"engagement_type_exists_{engagement_type}",
        f"Check engagement type exists: {engagement_type}",
        "> 0",
        str(type_counts.get(engagement_type, 0)),
        "PASS" if type_counts.get(engagement_type, 0) > 0 else "REVIEW"
    )

for channel in sorted(valid_channels):
    add_check(
        checks,
        f"engagement_channel_exists_{channel}",
        f"Check engagement channel exists: {channel}",
        "> 0",
        str(channel_counts.get(channel, 0)),
        "PASS" if channel_counts.get(channel, 0) > 0 else "REVIEW"
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