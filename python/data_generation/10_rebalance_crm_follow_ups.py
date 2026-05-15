import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

opportunities_path = Path("data/synthetic/follow_up_opportunities.csv")
crm_tasks_path = Path("data/synthetic/crm_follow_ups.csv")
summary_path = Path("data/synthetic/follow_up_generation_summary.csv")

max_tasks = 15000

team_quotas = {
    "service": 4500,
    "sales": 4000,
    "marketing": 4000,
    "group_sales": 2500
}

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()

def assigned_team(opportunity_type):
    if opportunity_type in {"group_renewal", "group_upsell"}:
        return "group_sales"

    if opportunity_type == "premium_upgrade":
        return "sales"

    if opportunity_type in {"valuable_no_show_recovery", "lapsed_fan_winback"}:
        return "service"

    return "marketing"

def assigned_owner(team, index):
    owners = {
        "group_sales": ["Group Sales Rep A", "Group Sales Rep B"],
        "sales": ["Sales Rep A", "Sales Rep B", "Business Development Rep"],
        "service": ["Service Rep A", "Service Rep B"],
        "marketing": ["Marketing Coordinator", "CRM Coordinator"]
    }

    choices = owners.get(team, ["CRM Coordinator"])
    return choices[index % len(choices)]

def suggested_action(opportunity_type):
    actions = {
        "valuable_no_show_recovery": "Send service-focused recovery message with next-game offer",
        "theme_night_repeat_offer": "Send related theme-night pre-sale or reminder",
        "high_in_park_spender": "Send merch or concessions bundle offer",
        "lapsed_fan_winback": "Send win-back campaign tied to strong upcoming promo",
        "premium_upgrade": "Route to sales for premium or mini-plan upgrade conversation",
        "family_pack_offer": "Send family pack offer for weekend or Sunday game",
        "group_renewal": "Route to group sales for renewal outreach",
        "group_upsell": "Route to group sales for larger outing or premium area offer"
    }

    return actions.get(opportunity_type, "Review connected fan/account behavior and assign next action")

opportunities = read_csv(opportunities_path)

task_candidates = [
    row for row in opportunities
    if row["priority_band"] in {"High", "Medium"}
]

task_candidates = sorted(
    task_candidates,
    key=lambda row: (
        int(row["opportunity_score"]),
        float(row["future_revenue_opportunity"])
    ),
    reverse=True
)

candidates_by_team = defaultdict(list)

for row in task_candidates:
    candidates_by_team[assigned_team(row["opportunity_type"])].append(row)

selected = []
selected_ids = set()

for team, quota in team_quotas.items():
    for row in candidates_by_team.get(team, [])[:quota]:
        selected.append(row)
        selected_ids.add(row["opportunity_id"])

if len(selected) < max_tasks:
    for row in task_candidates:
        if row["opportunity_id"] in selected_ids:
            continue

        selected.append(row)
        selected_ids.add(row["opportunity_id"])

        if len(selected) >= max_tasks:
            break

selected = sorted(
    selected[:max_tasks],
    key=lambda row: (
        int(row["opportunity_score"]),
        float(row["future_revenue_opportunity"])
    ),
    reverse=True
)

crm_tasks = []

for index, opportunity in enumerate(selected, start=1):
    score = int(opportunity["opportunity_score"])
    created_date = parse_date(opportunity["created_date"])
    team = assigned_team(opportunity["opportunity_type"])

    if score >= 80:
        due_date = created_date + timedelta(days=2)
    else:
        due_date = created_date + timedelta(days=5)

    crm_tasks.append({
        "follow_up_id": f"FUP_{index:08d}",
        "opportunity_id": opportunity["opportunity_id"],
        "fan_id": opportunity["fan_id"],
        "account_id": opportunity["account_id"],
        "game_id": opportunity["game_id"],
        "assigned_team": team,
        "assigned_owner": assigned_owner(team, index),
        "suggested_action": suggested_action(opportunity["opportunity_type"]),
        "priority_score": score,
        "priority_band": opportunity["priority_band"],
        "due_date": due_date.isoformat(),
        "status": "open",
        "outcome": "",
        "synthetic_data_flag": True
    })

task_fields = [
    "follow_up_id",
    "opportunity_id",
    "fan_id",
    "account_id",
    "game_id",
    "assigned_team",
    "assigned_owner",
    "suggested_action",
    "priority_score",
    "priority_band",
    "due_date",
    "status",
    "outcome",
    "synthetic_data_flag"
]

write_csv(crm_tasks_path, crm_tasks, task_fields)

opportunity_type_counts = defaultdict(int)
priority_counts = defaultdict(int)
task_team_counts = defaultdict(int)

for row in opportunities:
    opportunity_type_counts[row["opportunity_type"]] += 1
    priority_counts[row["priority_band"]] += 1

for row in crm_tasks:
    task_team_counts[row["assigned_team"]] += 1

summary_rows = [
    {"metric": "follow_up_opportunity_rows", "value": len(opportunities)},
    {"metric": "crm_follow_up_task_rows", "value": len(crm_tasks)},
    {"metric": "fan_opportunity_rows", "value": sum(1 for row in opportunities if row["fan_id"])},
    {"metric": "account_opportunity_rows", "value": sum(1 for row in opportunities if row["account_id"])},
    {"metric": "high_priority_opportunities", "value": priority_counts.get("High", 0)},
    {"metric": "medium_priority_opportunities", "value": priority_counts.get("Medium", 0)},
    {"metric": "monitor_priority_opportunities", "value": priority_counts.get("Monitor", 0)},
    {"metric": "low_priority_opportunities", "value": priority_counts.get("Low", 0)}
]

for opportunity_type, count in sorted(opportunity_type_counts.items()):
    summary_rows.append({"metric": f"opportunity_type_count_{opportunity_type}", "value": count})

for team, count in sorted(task_team_counts.items()):
    summary_rows.append({"metric": f"crm_task_team_count_{team}", "value": count})

write_csv(summary_path, summary_rows, ["metric", "value"])

print(f"Wrote {crm_tasks_path} with {len(crm_tasks)} balanced CRM follow-up tasks")
print(f"Wrote {summary_path}")

for team in ["service", "sales", "marketing", "group_sales"]:
    print(f"{team}: {task_team_counts.get(team, 0)}")