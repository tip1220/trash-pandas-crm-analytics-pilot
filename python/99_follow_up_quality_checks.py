import csv
from pathlib import Path
from collections import Counter
from datetime import datetime

opportunities_path = Path("data/synthetic/follow_up_opportunities.csv")
crm_tasks_path = Path("data/synthetic/crm_follow_ups.csv")
fans_path = Path("data/synthetic/fans.csv")
accounts_path = Path("data/synthetic/group_accounts.csv")
games_path = Path("data/processed/games_clean.csv")
output_path = Path("data/synthetic/follow_up_quality_summary.csv")

output_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def to_int(value):
    return int(float(str(value).strip()))

def to_float(value):
    return float(str(value).strip())

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

def expected_priority_band(score):
    if score >= 80:
        return "High"
    if score >= 60:
        return "Medium"
    if score >= 40:
        return "Monitor"
    return "Low"

def add_check(checks, check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

opportunities = read_csv(opportunities_path)
crm_tasks = read_csv(crm_tasks_path)
fans = read_csv(fans_path)
accounts = read_csv(accounts_path)
games = read_csv(games_path)

fan_ids = {row["fan_id"] for row in fans}
account_ids = {row["account_id"] for row in accounts}
game_ids = {row["game_id"] for row in games}
opportunity_ids = {row["opportunity_id"] for row in opportunities}

opportunities_by_id = {
    row["opportunity_id"]: row
    for row in opportunities
}

checks = []

add_check(
    checks,
    "follow_up_opportunity_rows",
    "Count follow-up opportunity rows",
    "> 0",
    str(len(opportunities)),
    "PASS" if len(opportunities) > 0 else "FAIL"
)

add_check(
    checks,
    "crm_follow_up_task_rows",
    "Count CRM follow-up task rows",
    "> 0 and <= 15000",
    str(len(crm_tasks)),
    "PASS" if 0 < len(crm_tasks) <= 15000 else "FAIL"
)

duplicate_opportunity_ids = [
    opportunity_id for opportunity_id, count in Counter(row["opportunity_id"] for row in opportunities).items() if count > 1
]

duplicate_follow_up_ids = [
    follow_up_id for follow_up_id, count in Counter(row["follow_up_id"] for row in crm_tasks).items() if count > 1
]

add_check(
    checks,
    "duplicate_opportunity_ids",
    "Check duplicate opportunity_id values",
    "0",
    str(len(duplicate_opportunity_ids)),
    "PASS" if len(duplicate_opportunity_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "duplicate_follow_up_ids",
    "Check duplicate follow_up_id values",
    "0",
    str(len(duplicate_follow_up_ids)),
    "PASS" if len(duplicate_follow_up_ids) == 0 else "FAIL"
)

bad_opportunity_entity_logic = []

for row in opportunities:
    fan_id = row["fan_id"].strip()
    account_id = row["account_id"].strip()

    if fan_id == "" and account_id == "":
        bad_opportunity_entity_logic.append(row)

    if fan_id != "" and account_id != "":
        bad_opportunity_entity_logic.append(row)

    if fan_id and fan_id not in fan_ids:
        bad_opportunity_entity_logic.append(row)

    if account_id and account_id not in account_ids:
        bad_opportunity_entity_logic.append(row)

add_check(
    checks,
    "bad_opportunity_entity_logic",
    "Check each opportunity connects to exactly one fan or account",
    "0",
    str(len(bad_opportunity_entity_logic)),
    "PASS" if len(bad_opportunity_entity_logic) == 0 else "FAIL"
)

invalid_opportunity_game_ids = [
    row for row in opportunities
    if row["game_id"].strip() != "" and row["game_id"] not in game_ids
]

invalid_task_game_ids = [
    row for row in crm_tasks
    if row["game_id"].strip() != "" and row["game_id"] not in game_ids
]

add_check(
    checks,
    "invalid_opportunity_game_ids",
    "Check nonblank opportunity game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_opportunity_game_ids)),
    "PASS" if len(invalid_opportunity_game_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "invalid_task_game_ids",
    "Check nonblank CRM task game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_task_game_ids)),
    "PASS" if len(invalid_task_game_ids) == 0 else "FAIL"
)

valid_opportunity_types = {
    "valuable_no_show_recovery",
    "theme_night_repeat_offer",
    "high_in_park_spender",
    "lapsed_fan_winback",
    "premium_upgrade",
    "family_pack_offer",
    "group_renewal",
    "group_upsell"
}

invalid_opportunity_types = [
    row for row in opportunities if row["opportunity_type"] not in valid_opportunity_types
]

add_check(
    checks,
    "invalid_opportunity_types",
    "Check opportunity_type values",
    "0",
    str(len(invalid_opportunity_types)),
    "PASS" if len(invalid_opportunity_types) == 0 else "FAIL"
)

valid_source_signals = {
    "ticket_scan",
    "promotion_engagement",
    "merch_concession",
    "lifecycle",
    "value_engagement",
    "fan_segment",
    "group_sales"
}

invalid_source_signals = [
    row for row in opportunities if row["source_signal"] not in valid_source_signals
]

add_check(
    checks,
    "invalid_source_signals",
    "Check source_signal values",
    "0",
    str(len(invalid_source_signals)),
    "PASS" if len(invalid_source_signals) == 0 else "FAIL"
)

valid_priority_bands = {"High", "Medium", "Monitor", "Low"}

invalid_priority_bands = [
    row for row in opportunities if row["priority_band"] not in valid_priority_bands
]

add_check(
    checks,
    "invalid_priority_bands",
    "Check opportunity priority_band values",
    "0",
    str(len(invalid_priority_bands)),
    "PASS" if len(invalid_priority_bands) == 0 else "FAIL"
)

bad_opportunity_scores = []
bad_priority_band_logic = []
bad_future_revenue_values = []
bad_repeat_likelihood_scores = []
bad_upgrade_potential_scores = []
bad_created_dates = []

for row in opportunities:
    try:
        score = to_int(row["opportunity_score"])

        if score < 1 or score > 100:
            bad_opportunity_scores.append(row)

        if row["priority_band"] != expected_priority_band(score):
            bad_priority_band_logic.append(row)
    except Exception:
        bad_opportunity_scores.append(row)

    try:
        future_revenue = to_float(row["future_revenue_opportunity"])

        if future_revenue < 0:
            bad_future_revenue_values.append(row)
    except Exception:
        bad_future_revenue_values.append(row)

    try:
        repeat_score = to_int(row["repeat_likelihood_score"])

        if repeat_score < 1 or repeat_score > 100:
            bad_repeat_likelihood_scores.append(row)
    except Exception:
        bad_repeat_likelihood_scores.append(row)

    try:
        upgrade_score = to_int(row["upgrade_potential_score"])

        if upgrade_score < 1 or upgrade_score > 100:
            bad_upgrade_potential_scores.append(row)
    except Exception:
        bad_upgrade_potential_scores.append(row)

    try:
        parse_date(row["created_date"])
    except Exception:
        bad_created_dates.append(row)

add_check(
    checks,
    "bad_opportunity_scores",
    "Check opportunity_score is between 1 and 100",
    "0",
    str(len(bad_opportunity_scores)),
    "PASS" if len(bad_opportunity_scores) == 0 else "FAIL"
)

add_check(
    checks,
    "bad_priority_band_logic",
    "Check priority_band matches opportunity_score",
    "0",
    str(len(bad_priority_band_logic)),
    "PASS" if len(bad_priority_band_logic) == 0 else "FAIL"
)

add_check(
    checks,
    "bad_future_revenue_values",
    "Check future_revenue_opportunity is non-negative",
    "0",
    str(len(bad_future_revenue_values)),
    "PASS" if len(bad_future_revenue_values) == 0 else "FAIL"
)

add_check(
    checks,
    "bad_repeat_likelihood_scores",
    "Check repeat_likelihood_score is between 1 and 100",
    "0",
    str(len(bad_repeat_likelihood_scores)),
    "PASS" if len(bad_repeat_likelihood_scores) == 0 else "FAIL"
)

add_check(
    checks,
    "bad_upgrade_potential_scores",
    "Check upgrade_potential_score is between 1 and 100",
    "0",
    str(len(bad_upgrade_potential_scores)),
    "PASS" if len(bad_upgrade_potential_scores) == 0 else "FAIL"
)

add_check(
    checks,
    "bad_created_dates",
    "Check opportunity created_date format",
    "0",
    str(len(bad_created_dates)),
    "PASS" if len(bad_created_dates) == 0 else "FAIL"
)

valid_boolean_values = {"True", "False", "true", "false", "TRUE", "FALSE"}

bad_opportunity_boolean_values = []

for row in opportunities:
    if row["synthetic_data_flag"] not in valid_boolean_values:
        bad_opportunity_boolean_values.append(row)

add_check(
    checks,
    "opportunity_boolean_values",
    "Check opportunity synthetic_data_flag values",
    "0",
    str(len(bad_opportunity_boolean_values)),
    "PASS" if len(bad_opportunity_boolean_values) == 0 else "FAIL"
)

invalid_task_opportunity_ids = [
    row for row in crm_tasks if row["opportunity_id"] not in opportunity_ids
]

add_check(
    checks,
    "invalid_task_opportunity_ids",
    "Check CRM task opportunity_id values exist in follow_up_opportunities.csv",
    "0",
    str(len(invalid_task_opportunity_ids)),
    "PASS" if len(invalid_task_opportunity_ids) == 0 else "FAIL"
)

bad_task_entity_links = []

for row in crm_tasks:
    opportunity = opportunities_by_id.get(row["opportunity_id"])

    if not opportunity:
        continue

    if row["fan_id"] != opportunity["fan_id"]:
        bad_task_entity_links.append(row)

    if row["account_id"] != opportunity["account_id"]:
        bad_task_entity_links.append(row)

    if row["game_id"] != opportunity["game_id"]:
        bad_task_entity_links.append(row)

add_check(
    checks,
    "bad_task_entity_links",
    "Check CRM task entity fields match source opportunity",
    "0",
    str(len(bad_task_entity_links)),
    "PASS" if len(bad_task_entity_links) == 0 else "FAIL"
)

invalid_task_fan_ids = [
    row for row in crm_tasks
    if row["fan_id"].strip() != "" and row["fan_id"] not in fan_ids
]

invalid_task_account_ids = [
    row for row in crm_tasks
    if row["account_id"].strip() != "" and row["account_id"] not in account_ids
]

add_check(
    checks,
    "invalid_task_fan_ids",
    "Check nonblank CRM task fan_id values exist in fans.csv",
    "0",
    str(len(invalid_task_fan_ids)),
    "PASS" if len(invalid_task_fan_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "invalid_task_account_ids",
    "Check nonblank CRM task account_id values exist in group_accounts.csv",
    "0",
    str(len(invalid_task_account_ids)),
    "PASS" if len(invalid_task_account_ids) == 0 else "FAIL"
)

valid_assigned_teams = {"sales", "marketing", "group_sales", "service"}

invalid_assigned_teams = [
    row for row in crm_tasks if row["assigned_team"] not in valid_assigned_teams
]

add_check(
    checks,
    "invalid_assigned_teams",
    "Check assigned_team values",
    "0",
    str(len(invalid_assigned_teams)),
    "PASS" if len(invalid_assigned_teams) == 0 else "FAIL"
)

bad_task_priority_logic = []

for row in crm_tasks:
    opportunity = opportunities_by_id.get(row["opportunity_id"])

    if not opportunity:
        continue

    if row["priority_score"] != opportunity["opportunity_score"]:
        bad_task_priority_logic.append(row)

    if row["priority_band"] != opportunity["priority_band"]:
        bad_task_priority_logic.append(row)

    if row["priority_band"] not in {"High", "Medium"}:
        bad_task_priority_logic.append(row)

add_check(
    checks,
    "bad_task_priority_logic",
    "Check CRM tasks are tied to high or medium opportunity priority",
    "0",
    str(len(bad_task_priority_logic)),
    "PASS" if len(bad_task_priority_logic) == 0 else "FAIL"
)

bad_task_dates = []

for row in crm_tasks:
    opportunity = opportunities_by_id.get(row["opportunity_id"])

    if not opportunity:
        continue

    try:
        created_date = parse_date(opportunity["created_date"])
        due_date = parse_date(row["due_date"])

        if due_date < created_date:
            bad_task_dates.append(row)
    except Exception:
        bad_task_dates.append(row)

add_check(
    checks,
    "bad_task_due_dates",
    "Check CRM task due_date is not before opportunity created_date",
    "0",
    str(len(bad_task_dates)),
    "PASS" if len(bad_task_dates) == 0 else "FAIL"
)

missing_task_actions = [
    row for row in crm_tasks if not row["suggested_action"].strip()
]

missing_task_owners = [
    row for row in crm_tasks if not row["assigned_owner"].strip()
]

add_check(
    checks,
    "missing_task_actions",
    "Check every CRM task has suggested_action",
    "0",
    str(len(missing_task_actions)),
    "PASS" if len(missing_task_actions) == 0 else "FAIL"
)

add_check(
    checks,
    "missing_task_owners",
    "Check every CRM task has assigned_owner",
    "0",
    str(len(missing_task_owners)),
    "PASS" if len(missing_task_owners) == 0 else "FAIL"
)

invalid_task_statuses = [
    row for row in crm_tasks if row["status"] not in {"open", "completed", "deferred", "dismissed"}
]

add_check(
    checks,
    "invalid_task_statuses",
    "Check CRM task status values",
    "0",
    str(len(invalid_task_statuses)),
    "PASS" if len(invalid_task_statuses) == 0 else "FAIL"
)

bad_task_boolean_values = []

for row in crm_tasks:
    if row["synthetic_data_flag"] not in valid_boolean_values:
        bad_task_boolean_values.append(row)

add_check(
    checks,
    "task_boolean_values",
    "Check CRM task synthetic_data_flag values",
    "0",
    str(len(bad_task_boolean_values)),
    "PASS" if len(bad_task_boolean_values) == 0 else "FAIL"
)

opportunity_type_counts = Counter(row["opportunity_type"] for row in opportunities)
priority_counts = Counter(row["priority_band"] for row in opportunities)
team_counts = Counter(row["assigned_team"] for row in crm_tasks)

for opportunity_type in sorted(valid_opportunity_types):
    add_check(
        checks,
        f"opportunity_type_exists_{opportunity_type}",
        f"Check opportunity type exists: {opportunity_type}",
        "> 0",
        str(opportunity_type_counts.get(opportunity_type, 0)),
        "PASS" if opportunity_type_counts.get(opportunity_type, 0) > 0 else "REVIEW"
    )

for band in ["High", "Medium", "Monitor", "Low"]:
    add_check(
        checks,
        f"priority_band_count_{band}",
        f"Report opportunity priority band count: {band}",
        "Review only",
        str(priority_counts.get(band, 0)),
        "PASS"
    )

for team in sorted(valid_assigned_teams):
    add_check(
        checks,
        f"crm_task_team_count_{team}",
        f"Report CRM task team count: {team}",
        "Review only",
        str(team_counts.get(team, 0)),
        "PASS" if team_counts.get(team, 0) > 0 else "REVIEW"
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