import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

fans_path = Path("data/synthetic/fans.csv")
segments_path = Path("data/synthetic/fan_segments.csv")
games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")
merch_path = Path("data/synthetic/merch_transactions.csv")
concessions_path = Path("data/synthetic/concession_transactions.csv")
engagement_path = Path("data/synthetic/fan_engagement.csv")
group_accounts_path = Path("data/synthetic/group_accounts.csv")
group_sales_path = Path("data/synthetic/group_sales.csv")

output_dir = Path("data/synthetic")
output_dir.mkdir(parents=True, exist_ok=True)

opportunities_path = output_dir / "follow_up_opportunities.csv"
crm_tasks_path = output_dir / "crm_follow_ups.csv"
summary_path = output_dir / "follow_up_generation_summary.csv"

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def to_bool(value):
    return str(value).strip().lower() == "true"

def to_int(value):
    if value is None or str(value).strip() == "":
        return 0
    return int(float(str(value).strip()))

def to_float(value):
    if value is None or str(value).strip() == "":
        return 0.0
    return float(str(value).strip())

def parse_date(value):
    if value is None or str(value).strip() == "":
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()

def max_date(*dates):
    clean_dates = [date for date in dates if date is not None]
    if not clean_dates:
        return None
    return max(clean_dates)

def priority_band(score):
    if score >= 80:
        return "High"
    if score >= 60:
        return "Medium"
    if score >= 40:
        return "Monitor"
    return "Low"

def clamp_score(score):
    return max(1, min(int(round(score)), 100))

def source_date_for_fan(stats):
    selected_date = max_date(
        stats["last_attended_date"],
        stats["last_purchase_date"],
        stats["last_engagement_date"]
    )

    if selected_date is None:
        return datetime.strptime("2025-09-15", "%Y-%m-%d").date()

    return selected_date + timedelta(days=1)

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

fans = read_csv(fans_path)
segments = read_csv(segments_path)
games = read_csv(games_path)
promotions = read_csv(promotions_path)
orders = read_csv(orders_path)
scans = read_csv(scans_path)
merch = read_csv(merch_path)
concessions = read_csv(concessions_path)
engagement = read_csv(engagement_path)
group_accounts = read_csv(group_accounts_path)
group_sales = read_csv(group_sales_path)

fans_by_id = {row["fan_id"]: row for row in fans}
games_by_id = {row["game_id"]: row for row in games}
accounts_by_id = {row["account_id"]: row for row in group_accounts}

segments_by_fan = defaultdict(set)
lifecycle_by_fan = {}

for row in segments:
    fan_id = row["fan_id"]
    segment_name = row["segment_name"]
    segments_by_fan[fan_id].add(segment_name)

    if row["segment_type"] == "lifecycle":
        lifecycle_by_fan[fan_id] = segment_name

promo_categories_by_game = defaultdict(set)

for row in promotions:
    promo_categories_by_game[row["game_id"]].add(row["promo_category"])
    promo_categories_by_game[row["game_id"]].add(row["promo_type"])

fan_stats = defaultdict(lambda: {
    "ticket_revenue": 0.0,
    "ticket_quantity": 0,
    "order_count": 0,
    "premium_order_count": 0,
    "group_order_count": 0,
    "games_purchased": set(),
    "games_attended": set(),
    "promo_categories_attended": set(),
    "last_purchase_date": None,
    "last_attended_date": None,
    "no_show_ticket_quantity": 0,
    "last_no_show_game_id": "",
    "merch_spend": 0.0,
    "merch_transactions": 0,
    "concession_spend": 0.0,
    "concession_transactions": 0,
    "engagement_count": 0,
    "engagement_score_total": 0,
    "engagement_types": set(),
    "last_engagement_date": None
})

for order in orders:
    fan_id = order["fan_id"]
    game_id = order["game_id"]

    if fan_id not in fans_by_id:
        continue

    stats = fan_stats[fan_id]
    stats["ticket_revenue"] += to_float(order["net_ticket_revenue"])
    stats["ticket_quantity"] += to_int(order["ticket_quantity"])
    stats["order_count"] += 1
    stats["games_purchased"].add(game_id)

    if to_bool(order["premium_flag"]):
        stats["premium_order_count"] += 1

    if to_bool(order["group_order_flag"]) or order["ticket_type"] == "group":
        stats["group_order_count"] += 1

    order_date = parse_date(order["order_date"])
    stats["last_purchase_date"] = max_date(stats["last_purchase_date"], order_date)

for scan in scans:
    fan_id = scan["fan_id"]
    game_id = scan["game_id"]

    if fan_id not in fans_by_id:
        continue

    stats = fan_stats[fan_id]
    scanned_qty = to_int(scan["scanned_ticket_quantity"])
    no_show_qty = to_int(scan["no_show_ticket_quantity"])

    if scanned_qty > 0:
        stats["games_attended"].add(game_id)

        game = games_by_id.get(game_id)
        if game:
            attended_date = parse_date(game["game_date"])
            stats["last_attended_date"] = max_date(stats["last_attended_date"], attended_date)

        for category in promo_categories_by_game.get(game_id, set()):
            stats["promo_categories_attended"].add(category)

    if no_show_qty > 0:
        stats["no_show_ticket_quantity"] += no_show_qty
        stats["last_no_show_game_id"] = game_id

for row in merch:
    fan_id = row["fan_id"].strip()

    if fan_id in fans_by_id:
        fan_stats[fan_id]["merch_spend"] += to_float(row["net_sales"])
        fan_stats[fan_id]["merch_transactions"] += 1

for row in concessions:
    fan_id = row["fan_id"].strip()

    if fan_id in fans_by_id:
        fan_stats[fan_id]["concession_spend"] += to_float(row["net_sales"])
        fan_stats[fan_id]["concession_transactions"] += 1

for row in engagement:
    fan_id = row["fan_id"]

    if fan_id in fans_by_id:
        stats = fan_stats[fan_id]
        stats["engagement_count"] += 1
        stats["engagement_score_total"] += to_int(row["engagement_score"])
        stats["engagement_types"].add(row["engagement_type"])
        stats["last_engagement_date"] = max_date(stats["last_engagement_date"], parse_date(row["engagement_date"]))

account_stats = defaultdict(lambda: {
    "group_sales_count": 0,
    "group_ticket_quantity": 0,
    "group_revenue": 0.0,
    "renewal_count": 0,
    "upsell_count": 0,
    "scan_rate_total": 0.0,
    "latest_game_id": "",
    "latest_game_date": None
})

for row in group_sales:
    account_id = row["account_id"]
    game_id = row["game_id"]

    stats = account_stats[account_id]
    stats["group_sales_count"] += 1
    stats["group_ticket_quantity"] += to_int(row["group_ticket_quantity"])
    stats["group_revenue"] += to_float(row["group_ticket_revenue"])
    stats["scan_rate_total"] += to_float(row["group_scan_rate"])

    if to_bool(row["renewal_flag"]):
        stats["renewal_count"] += 1

    if to_bool(row["upsell_flag"]):
        stats["upsell_count"] += 1

    game = games_by_id.get(game_id)

    if game:
        game_date = parse_date(game["game_date"])

        if stats["latest_game_date"] is None or game_date > stats["latest_game_date"]:
            stats["latest_game_date"] = game_date
            stats["latest_game_id"] = game_id

opportunities = []
opportunity_counter = 1

def add_opportunity(fan_id, account_id, game_id, opportunity_type, opportunity_reason, score, source_signal, created_date, future_revenue_opportunity, repeat_likelihood_score, upgrade_potential_score):
    global opportunity_counter

    homestand_id = ""

    if game_id in games_by_id:
        homestand_id = games_by_id[game_id]["homestand_id"]

    final_score = clamp_score(score)

    opportunities.append({
        "opportunity_id": f"OPP_{opportunity_counter:08d}",
        "fan_id": fan_id,
        "account_id": account_id,
        "game_id": game_id,
        "homestand_id": homestand_id,
        "opportunity_type": opportunity_type,
        "opportunity_reason": opportunity_reason,
        "opportunity_score": final_score,
        "priority_band": priority_band(final_score),
        "source_signal": source_signal,
        "created_date": created_date.isoformat(),
        "future_revenue_opportunity": f"{future_revenue_opportunity:.2f}",
        "repeat_likelihood_score": repeat_likelihood_score,
        "upgrade_potential_score": upgrade_potential_score,
        "synthetic_data_flag": True
    })

    opportunity_counter += 1

for fan_id, fan in fans_by_id.items():
    stats = fan_stats[fan_id]
    fan_segments = segments_by_fan.get(fan_id, set())
    lifecycle = lifecycle_by_fan.get(fan_id, "")
    ticket_revenue = stats["ticket_revenue"]
    in_park_spend = stats["merch_spend"] + stats["concession_spend"]
    total_value = ticket_revenue + in_park_spend
    attended_games = len(stats["games_attended"])
    purchased_games = len(stats["games_purchased"])
    engagement_count = stats["engagement_count"]
    engagement_score_total = stats["engagement_score_total"]

    repeat_likelihood_score = clamp_score(
        18
        + attended_games * 4
        + purchased_games * 3
        + engagement_count * 0.4
        + (12 if "Repeat Single-Game Buyer" in fan_segments else 0)
        + (16 if "Mini Plan Buyer" in fan_segments else 0)
        + (20 if "Season Ticket Holder" in fan_segments else 0)
        - (10 if "Lapsed Fan" in fan_segments else 0)
    )

    upgrade_potential_score = clamp_score(
        15
        + (stats["premium_order_count"] * 8)
        + (stats["group_order_count"] * 10)
        + (20 if "Corporate Prospect" in fan_segments else 0)
        + (15 if "High In-Park Spender" in fan_segments else 0)
        + min(total_value / 35, 25)
        + (20 if "premium_interest_form" in stats["engagement_types"] else 0)
        + (18 if "group_interest_form" in stats["engagement_types"] else 0)
    )

    future_revenue_opportunity = (
        ticket_revenue * 0.22
        + in_park_spend * 0.28
        + engagement_score_total * 0.35
        + upgrade_potential_score * 1.50
    ) * (repeat_likelihood_score / 100)

    one_time_low_value = (
        lifecycle == "One-Time Buyer"
        and total_value < 150
        and stats["premium_order_count"] == 0
        and stats["group_order_count"] == 0
    )

    created_date = source_date_for_fan(stats)

    if stats["no_show_ticket_quantity"] > 0 and not one_time_low_value:
        no_show_score = (
            45
            + min(total_value / 25, 25)
            + min(stats["no_show_ticket_quantity"] * 2, 12)
            + (10 if engagement_count > 0 else 0)
            + (8 if stats["premium_order_count"] > 0 else 0)
            + (8 if stats["group_order_count"] > 0 else 0)
        )

        add_opportunity(
            fan_id,
            "",
            stats["last_no_show_game_id"],
            "valuable_no_show_recovery",
            "Fan or account purchased tickets but did not fully scan; prior value supports recovery outreach",
            no_show_score,
            "ticket_scan",
            created_date,
            future_revenue_opportunity,
            repeat_likelihood_score,
            upgrade_potential_score
        )

    if "Theme Night Buyer" in fan_segments and attended_games > 0 and not one_time_low_value:
        theme_score = (
            42
            + min(engagement_count * 1.5, 18)
            + min(total_value / 40, 18)
            + (10 if repeat_likelihood_score >= 65 else 0)
        )

        add_opportunity(
            fan_id,
            "",
            "",
            "theme_night_repeat_offer",
            "Fan has theme-night behavior and enough connected activity to support repeat promotion targeting",
            theme_score,
            "promotion_engagement",
            created_date,
            future_revenue_opportunity,
            repeat_likelihood_score,
            upgrade_potential_score
        )

    if in_park_spend >= 125 and ticket_revenue < 300:
        spender_score = (
            50
            + min(in_park_spend / 20, 25)
            + min(engagement_count, 15)
            + (8 if "High In-Park Spender" in fan_segments else 0)
        )

        add_opportunity(
            fan_id,
            "",
            "",
            "high_in_park_spender",
            "Fan shows hidden value through merch and concession spend beyond ticket revenue",
            spender_score,
            "merch_concession",
            created_date,
            future_revenue_opportunity,
            repeat_likelihood_score,
            upgrade_potential_score
        )

    if "Lapsed Fan" in fan_segments and total_value >= 125:
        lapsed_score = (
            40
            + min(total_value / 30, 25)
            + min(engagement_count * 1.2, 15)
            + (8 if stats["no_show_ticket_quantity"] == 0 else 0)
        )

        add_opportunity(
            fan_id,
            "",
            "",
            "lapsed_fan_winback",
            "Fan has prior value but is currently classified as lapsed",
            lapsed_score,
            "lifecycle",
            created_date,
            future_revenue_opportunity,
            repeat_likelihood_score,
            upgrade_potential_score
        )

    if upgrade_potential_score >= 65 and not one_time_low_value:
        upgrade_score = (
            45
            + min(upgrade_potential_score * 0.35, 35)
            + min(total_value / 60, 15)
            + (10 if "premium_interest_form" in stats["engagement_types"] else 0)
        )

        add_opportunity(
            fan_id,
            "",
            "",
            "premium_upgrade",
            "Fan shows premium, corporate, or high-value behavior that supports upgrade outreach",
            upgrade_score,
            "value_engagement",
            created_date,
            future_revenue_opportunity,
            repeat_likelihood_score,
            upgrade_potential_score
        )

    if "Family Buyer" in fan_segments and attended_games >= 1 and not one_time_low_value:
        family_score = (
            38
            + min(repeat_likelihood_score * 0.30, 25)
            + min(in_park_spend / 25, 18)
            + (10 if "family" in stats["promo_categories_attended"] else 0)
        )

        add_opportunity(
            fan_id,
            "",
            "",
            "family_pack_offer",
            "Fan shows family-oriented attendance or spend behavior",
            family_score,
            "fan_segment",
            created_date,
            future_revenue_opportunity,
            repeat_likelihood_score,
            upgrade_potential_score
        )

for account_id, account in accounts_by_id.items():
    stats = account_stats[account_id]

    if stats["group_sales_count"] == 0:
        continue

    average_scan_rate = stats["scan_rate_total"] / stats["group_sales_count"]
    account_value = stats["group_revenue"]

    repeat_likelihood_score = clamp_score(
        25
        + stats["group_sales_count"] * 8
        + average_scan_rate * 35
        + (12 if account["renewal_status"] in {"active", "renewal_target"} else 0)
    )

    upgrade_potential_score = clamp_score(
        20
        + min(stats["group_ticket_quantity"] / 12, 30)
        + min(account_value / 2500, 25)
        + (18 if to_bool(account["corporate_prospect_flag"]) else 0)
        + stats["upsell_count"] * 4
    )

    future_revenue_opportunity = (
        account_value * 0.32
        + stats["group_ticket_quantity"] * 2.50
        + upgrade_potential_score * 3.00
    ) * (repeat_likelihood_score / 100)

    created_date = stats["latest_game_date"] + timedelta(days=1) if stats["latest_game_date"] else datetime.strptime("2025-09-15", "%Y-%m-%d").date()

    if stats["renewal_count"] > 0:
        score = (
            50
            + min(account_value / 1500, 25)
            + average_scan_rate * 15
            + (10 if account["renewal_status"] == "renewal_target" else 0)
        )

        add_opportunity(
            "",
            account_id,
            stats["latest_game_id"],
            "group_renewal",
            "Group account has renewal signal based on connected ticket volume and scan performance",
            score,
            "group_sales",
            created_date,
            future_revenue_opportunity,
            repeat_likelihood_score,
            upgrade_potential_score
        )

    if stats["upsell_count"] > 0:
        score = (
            52
            + min(account_value / 1800, 22)
            + min(stats["group_ticket_quantity"] / 20, 18)
            + (10 if to_bool(account["corporate_prospect_flag"]) else 0)
        )

        add_opportunity(
            "",
            account_id,
            stats["latest_game_id"],
            "group_upsell",
            "Group account shows volume, scan, or corporate signals that support upsell outreach",
            score,
            "group_sales",
            created_date,
            future_revenue_opportunity,
            repeat_likelihood_score,
            upgrade_potential_score
        )

opportunity_fields = [
    "opportunity_id",
    "fan_id",
    "account_id",
    "game_id",
    "homestand_id",
    "opportunity_type",
    "opportunity_reason",
    "opportunity_score",
    "priority_band",
    "source_signal",
    "created_date",
    "future_revenue_opportunity",
    "repeat_likelihood_score",
    "upgrade_potential_score",
    "synthetic_data_flag"
]

write_csv(opportunities_path, opportunities, opportunity_fields)

crm_tasks = []
task_counter = 1

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

max_tasks = min(len(task_candidates), 15000)

for index, opportunity in enumerate(task_candidates[:max_tasks], start=1):
    score = int(opportunity["opportunity_score"])
    created_date = parse_date(opportunity["created_date"])
    team = assigned_team(opportunity["opportunity_type"])

    if score >= 80:
        due_date = created_date + timedelta(days=2)
    else:
        due_date = created_date + timedelta(days=5)

    crm_tasks.append({
        "follow_up_id": f"FUP_{task_counter:08d}",
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

    task_counter += 1

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

print(f"Wrote {opportunities_path} with {len(opportunities)} opportunities")
print(f"Wrote {crm_tasks_path} with {len(crm_tasks)} CRM follow-up tasks")
print(f"Wrote {summary_path}")