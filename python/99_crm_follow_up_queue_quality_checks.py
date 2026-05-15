import csv
from pathlib import Path
import pandas as pd

queue_path = Path("data/exports/crm_follow_up_queue.csv")
crm_tasks_path = Path("data/synthetic/crm_follow_ups.csv")
opportunities_path = Path("data/synthetic/follow_up_opportunities.csv")
fans_path = Path("data/synthetic/fans.csv")
accounts_path = Path("data/synthetic/group_accounts.csv")
games_path = Path("data/processed/games_clean.csv")
summary_path = Path("data/exports/crm_follow_up_queue_quality_summary.csv")

summary_path.parent.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)

def to_number(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def has_value(series):
    return series.fillna("").astype(str).str.strip().ne("")

def add_check(checks, check_name, result, expected, actual, status):
    checks.append({
        "check_name": check_name,
        "result": result,
        "expected": expected,
        "actual": actual,
        "status": status
    })

queue = read_csv(queue_path)
crm_tasks = read_csv(crm_tasks_path)
opportunities = read_csv(opportunities_path)
fans = read_csv(fans_path)
accounts = read_csv(accounts_path)
games = read_csv(games_path)

checks = []

required_columns = [
    "priority_rank",
    "follow_up_id",
    "opportunity_id",
    "entity_type",
    "entity_id",
    "entity_display_name",
    "assigned_team",
    "assigned_owner",
    "executive_action_bucket",
    "priority_score",
    "priority_band",
    "opportunity_type",
    "opportunity_reason",
    "source_signal",
    "suggested_action",
    "due_date",
    "status",
    "created_date",
    "future_revenue_opportunity",
    "repeat_likelihood_score",
    "upgrade_potential_score",
    "entity_total_value",
    "entity_ticket_revenue",
    "entity_in_park_revenue",
    "entity_activity_summary",
    "dashboard_filter_label",
    "game_id",
    "season",
    "game_date",
    "opponent",
    "day_of_week",
    "homestand_id",
    "fan_id",
    "account_id",
    "synthetic_data_flag"
]

missing_columns = [
    column for column in required_columns
    if column not in queue.columns
]

add_check(
    checks,
    "missing_required_columns",
    "Check required CRM queue columns exist",
    "0",
    str(len(missing_columns)),
    "PASS" if len(missing_columns) == 0 else "FAIL"
)

add_check(
    checks,
    "crm_follow_up_queue_rows",
    "Count CRM follow-up queue rows",
    str(len(crm_tasks)),
    str(len(queue)),
    "PASS" if len(queue) == len(crm_tasks) else "FAIL"
)

duplicate_follow_up_ids = queue.duplicated(subset=["follow_up_id"]).sum()

add_check(
    checks,
    "duplicate_follow_up_ids",
    "Check duplicate follow_up_id values",
    "0",
    str(int(duplicate_follow_up_ids)),
    "PASS" if duplicate_follow_up_ids == 0 else "FAIL"
)

duplicate_priority_ranks = queue.duplicated(subset=["priority_rank"]).sum()

add_check(
    checks,
    "duplicate_priority_ranks",
    "Check duplicate priority_rank values",
    "0",
    str(int(duplicate_priority_ranks)),
    "PASS" if duplicate_priority_ranks == 0 else "FAIL"
)

priority_ranks = sorted(to_number(queue["priority_rank"]).astype(int).tolist())
expected_priority_ranks = list(range(1, len(queue) + 1))

add_check(
    checks,
    "priority_rank_sequence",
    "Check priority_rank is a complete 1-to-row-count sequence",
    f"1-{len(queue)}",
    "valid" if priority_ranks == expected_priority_ranks else "invalid",
    "PASS" if priority_ranks == expected_priority_ranks else "FAIL"
)

crm_task_ids = set(crm_tasks["follow_up_id"])
queue_task_ids = set(queue["follow_up_id"])

missing_task_ids = crm_task_ids - queue_task_ids
extra_task_ids = queue_task_ids - crm_task_ids

add_check(
    checks,
    "missing_crm_task_ids",
    "Check every CRM task appears in queue export",
    "0",
    str(len(missing_task_ids)),
    "PASS" if len(missing_task_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "extra_queue_task_ids",
    "Check queue has no follow_up_id values outside crm_follow_ups.csv",
    "0",
    str(len(extra_task_ids)),
    "PASS" if len(extra_task_ids) == 0 else "FAIL"
)

opportunity_ids = set(opportunities["opportunity_id"])
fan_ids = set(fans["fan_id"])
account_ids = set(accounts["account_id"])
game_ids = set(games["game_id"])

invalid_opportunity_ids = queue[
    ~queue["opportunity_id"].isin(opportunity_ids)
]

add_check(
    checks,
    "invalid_opportunity_ids",
    "Check opportunity_id values exist in follow_up_opportunities.csv",
    "0",
    str(len(invalid_opportunity_ids)),
    "PASS" if len(invalid_opportunity_ids) == 0 else "FAIL"
)

invalid_fan_ids = queue[
    has_value(queue["fan_id"])
    & ~queue["fan_id"].isin(fan_ids)
]

invalid_account_ids = queue[
    has_value(queue["account_id"])
    & ~queue["account_id"].isin(account_ids)
]

invalid_game_ids = queue[
    has_value(queue["game_id"])
    & ~queue["game_id"].isin(game_ids)
]

add_check(
    checks,
    "invalid_fan_ids",
    "Check nonblank fan_id values exist in fans.csv",
    "0",
    str(len(invalid_fan_ids)),
    "PASS" if len(invalid_fan_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "invalid_account_ids",
    "Check nonblank account_id values exist in group_accounts.csv",
    "0",
    str(len(invalid_account_ids)),
    "PASS" if len(invalid_account_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "invalid_game_ids",
    "Check nonblank game_id values exist in games_clean.csv",
    "0",
    str(len(invalid_game_ids)),
    "PASS" if len(invalid_game_ids) == 0 else "FAIL"
)

valid_entity_types = {"fan", "account"}

invalid_entity_types = queue[
    ~queue["entity_type"].isin(valid_entity_types)
]

add_check(
    checks,
    "invalid_entity_types",
    "Check entity_type values",
    "0",
    str(len(invalid_entity_types)),
    "PASS" if len(invalid_entity_types) == 0 else "FAIL"
)

bad_entity_logic = []

for _, row in queue.iterrows():
    entity_type = row["entity_type"]
    fan_id = str(row["fan_id"]).strip()
    account_id = str(row["account_id"]).strip()
    entity_id = str(row["entity_id"]).strip()

    if entity_type == "fan":
        if fan_id == "" or account_id != "" or entity_id != fan_id:
            bad_entity_logic.append(row)

    elif entity_type == "account":
        if account_id == "" or fan_id != "" or entity_id != account_id:
            bad_entity_logic.append(row)

    else:
        bad_entity_logic.append(row)

add_check(
    checks,
    "bad_entity_logic",
    "Check entity_type, entity_id, fan_id, and account_id alignment",
    "0",
    str(len(bad_entity_logic)),
    "PASS" if len(bad_entity_logic) == 0 else "FAIL"
)

blank_entity_ids = queue[
    ~has_value(queue["entity_id"])
]

blank_entity_display_names = queue[
    ~has_value(queue["entity_display_name"])
]

add_check(
    checks,
    "blank_entity_ids",
    "Check every queue row has entity_id",
    "0",
    str(len(blank_entity_ids)),
    "PASS" if len(blank_entity_ids) == 0 else "FAIL"
)

add_check(
    checks,
    "blank_entity_display_names",
    "Check every queue row has entity_display_name",
    "0",
    str(len(blank_entity_display_names)),
    "PASS" if len(blank_entity_display_names) == 0 else "FAIL"
)

valid_assigned_teams = {"service", "sales", "marketing", "group_sales"}

invalid_assigned_teams = queue[
    ~queue["assigned_team"].isin(valid_assigned_teams)
]

add_check(
    checks,
    "invalid_assigned_teams",
    "Check assigned_team values",
    "0",
    str(len(invalid_assigned_teams)),
    "PASS" if len(invalid_assigned_teams) == 0 else "FAIL"
)

valid_action_buckets = {"Recover", "Upgrade", "Retain", "Renew"}

invalid_action_buckets = queue[
    ~queue["executive_action_bucket"].isin(valid_action_buckets)
]

add_check(
    checks,
    "invalid_executive_action_buckets",
    "Check executive_action_bucket values",
    "0",
    str(len(invalid_action_buckets)),
    "PASS" if len(invalid_action_buckets) == 0 else "FAIL"
)

valid_priority_bands = {"High", "Medium"}

invalid_priority_bands = queue[
    ~queue["priority_band"].isin(valid_priority_bands)
]

add_check(
    checks,
    "invalid_priority_bands",
    "Check CRM queue priority_band values are High or Medium",
    "0",
    str(len(invalid_priority_bands)),
    "PASS" if len(invalid_priority_bands) == 0 else "FAIL"
)

blank_suggested_actions = queue[
    ~has_value(queue["suggested_action"])
]

blank_assigned_owners = queue[
    ~has_value(queue["assigned_owner"])
]

blank_dashboard_filter_labels = queue[
    ~has_value(queue["dashboard_filter_label"])
]

add_check(
    checks,
    "blank_suggested_actions",
    "Check every queue row has suggested_action",
    "0",
    str(len(blank_suggested_actions)),
    "PASS" if len(blank_suggested_actions) == 0 else "FAIL"
)

add_check(
    checks,
    "blank_assigned_owners",
    "Check every queue row has assigned_owner",
    "0",
    str(len(blank_assigned_owners)),
    "PASS" if len(blank_assigned_owners) == 0 else "FAIL"
)

add_check(
    checks,
    "blank_dashboard_filter_labels",
    "Check every queue row has dashboard_filter_label",
    "0",
    str(len(blank_dashboard_filter_labels)),
    "PASS" if len(blank_dashboard_filter_labels) == 0 else "FAIL"
)

bad_date_rows = []

for _, row in queue.iterrows():
    try:
        created_date = pd.to_datetime(row["created_date"])
        due_date = pd.to_datetime(row["due_date"])

        if due_date < created_date:
            bad_date_rows.append(row)
    except Exception:
        bad_date_rows.append(row)

add_check(
    checks,
    "bad_due_date_logic",
    "Check due_date is not before created_date",
    "0",
    str(len(bad_date_rows)),
    "PASS" if len(bad_date_rows) == 0 else "FAIL"
)

numeric_columns = [
    "priority_score",
    "future_revenue_opportunity",
    "repeat_likelihood_score",
    "upgrade_potential_score",
    "entity_total_value",
    "entity_ticket_revenue",
    "entity_in_park_revenue",
    "fan_ticket_revenue",
    "fan_merch_revenue",
    "fan_concession_revenue",
    "fan_in_park_revenue",
    "fan_total_value",
    "account_group_revenue",
    "account_total_value"
]

negative_numeric_columns = []

for column in numeric_columns:
    bad_rows = queue[to_number(queue[column]) < 0]

    if len(bad_rows) > 0:
        negative_numeric_columns.append(column)

add_check(
    checks,
    "negative_numeric_columns",
    "Check key numeric columns are non-negative",
    "0 columns",
    str(len(negative_numeric_columns)),
    "PASS" if len(negative_numeric_columns) == 0 else "FAIL"
)

bad_score_ranges = queue[
    (to_number(queue["priority_score"]) < 1)
    | (to_number(queue["priority_score"]) > 100)
    | (to_number(queue["repeat_likelihood_score"]) < 1)
    | (to_number(queue["repeat_likelihood_score"]) > 100)
    | (to_number(queue["upgrade_potential_score"]) < 1)
    | (to_number(queue["upgrade_potential_score"]) > 100)
]

add_check(
    checks,
    "bad_score_ranges",
    "Check priority, repeat, and upgrade scores are between 1 and 100",
    "0",
    str(len(bad_score_ranges)),
    "PASS" if len(bad_score_ranges) == 0 else "FAIL"
)

bad_rate_ranges = queue[
    (to_number(queue["fan_scan_rate"]) < 0)
    | (to_number(queue["fan_scan_rate"]) > 1)
    | (to_number(queue["fan_no_show_rate"]) < 0)
    | (to_number(queue["fan_no_show_rate"]) > 1)
    | (to_number(queue["account_avg_group_scan_rate"]) < 0)
    | (to_number(queue["account_avg_group_scan_rate"]) > 1)
]

add_check(
    checks,
    "bad_rate_ranges",
    "Check scan-rate fields are between 0 and 1",
    "0",
    str(len(bad_rate_ranges)),
    "PASS" if len(bad_rate_ranges) == 0 else "FAIL"
)

bad_entity_value_logic = []

for _, row in queue.iterrows():
    entity_type = row["entity_type"]

    entity_total_value = float(row["entity_total_value"])
    fan_total_value = float(row["fan_total_value"])
    account_total_value = float(row["account_total_value"])

    if entity_type == "fan":
        if abs(entity_total_value - fan_total_value) > 0.02:
            bad_entity_value_logic.append(row)

    if entity_type == "account":
        if abs(entity_total_value - account_total_value) > 0.02:
            bad_entity_value_logic.append(row)

add_check(
    checks,
    "bad_entity_value_logic",
    "Check entity_total_value matches fan/account value",
    "0",
    str(len(bad_entity_value_logic)),
    "PASS" if len(bad_entity_value_logic) == 0 else "FAIL"
)

null_string_rows = 0

for column in queue.columns:
    null_string_rows += queue[column].astype(str).str.lower().isin(["nan", "none", "null"]).sum()

add_check(
    checks,
    "bad_null_string_values",
    "Check no string null placeholders exist",
    "0",
    str(int(null_string_rows)),
    "PASS" if null_string_rows == 0 else "FAIL"
)

team_counts = queue["assigned_team"].value_counts().to_dict()
bucket_counts = queue["executive_action_bucket"].value_counts().to_dict()
entity_counts = queue["entity_type"].value_counts().to_dict()
priority_counts = queue["priority_band"].value_counts().to_dict()
opportunity_type_counts = queue["opportunity_type"].value_counts().to_dict()

for team in sorted(valid_assigned_teams):
    add_check(
        checks,
        f"assigned_team_count_{team}",
        f"Report assigned team count: {team}",
        "> 0",
        str(team_counts.get(team, 0)),
        "PASS" if team_counts.get(team, 0) > 0 else "FAIL"
    )

for bucket in sorted(valid_action_buckets):
    add_check(
        checks,
        f"executive_action_bucket_count_{bucket}",
        f"Report executive action bucket count: {bucket}",
        "> 0",
        str(bucket_counts.get(bucket, 0)),
        "PASS" if bucket_counts.get(bucket, 0) > 0 else "FAIL"
    )

for entity_type in ["fan", "account"]:
    add_check(
        checks,
        f"entity_type_count_{entity_type}",
        f"Report entity type count: {entity_type}",
        "> 0",
        str(entity_counts.get(entity_type, 0)),
        "PASS" if entity_counts.get(entity_type, 0) > 0 else "FAIL"
    )

for priority_band in ["High", "Medium"]:
    add_check(
        checks,
        f"priority_band_count_{priority_band}",
        f"Report priority band count: {priority_band}",
        "> 0",
        str(priority_counts.get(priority_band, 0)),
        "PASS" if priority_counts.get(priority_band, 0) > 0 else "FAIL"
    )

for opportunity_type, count in sorted(opportunity_type_counts.items()):
    add_check(
        checks,
        f"opportunity_type_count_{opportunity_type}",
        f"Report opportunity type count: {opportunity_type}",
        "Review only",
        str(count),
        "PASS"
    )

add_check(
    checks,
    "total_future_revenue_opportunity",
    "Report total future revenue opportunity",
    "Review only",
    f"{float(to_number(queue['future_revenue_opportunity']).sum()):.2f}",
    "PASS"
)

add_check(
    checks,
    "average_priority_score",
    "Report average priority score",
    "Review only",
    f"{float(to_number(queue['priority_score']).mean()):.2f}",
    "PASS"
)

with summary_path.open("w", newline="") as f:
    fieldnames = ["check_name", "result", "expected", "actual", "status"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(checks)

for check in checks:
    print(f"{check['status']}: {check['check_name']} | expected={check['expected']} | actual={check['actual']}")

fail_count = sum(1 for check in checks if check["status"] == "FAIL")
review_count = sum(1 for check in checks if check["status"] == "REVIEW")

print(f"\nQuality check summary saved to {summary_path}")
print(f"FAIL checks: {fail_count}")
print(f"REVIEW checks: {review_count}")

if fail_count > 0:
    raise SystemExit(1)