from pathlib import Path
import pandas as pd

crm_tasks_path = Path("data/synthetic/crm_follow_ups.csv")
opportunities_path = Path("data/synthetic/follow_up_opportunities.csv")
fans_path = Path("data/synthetic/fans.csv")
segments_path = Path("data/synthetic/fan_segments.csv")
accounts_path = Path("data/synthetic/group_accounts.csv")
games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")
merch_path = Path("data/synthetic/merch_transactions.csv")
concessions_path = Path("data/synthetic/concession_transactions.csv")
engagement_path = Path("data/synthetic/fan_engagement.csv")
group_sales_path = Path("data/synthetic/group_sales.csv")

output_dir = Path("data/exports")
output_dir.mkdir(parents=True, exist_ok=True)

queue_path = output_dir / "crm_follow_up_queue.csv"
summary_path = output_dir / "crm_follow_up_queue_generation_summary.csv"

def read_csv(path):
    return pd.read_csv(path, dtype=str)

def to_number(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def to_bool(series):
    return series.astype(str).str.lower().eq("true")

def join_unique(values):
    clean_values = sorted(
        set(str(value).strip() for value in values if str(value).strip() not in {"", "nan", "None"})
    )
    return " | ".join(clean_values)

def safe_divide(numerator, denominator):
    numerator = to_number(numerator)
    denominator = to_number(denominator)
    return numerator.div(denominator.where(denominator != 0)).fillna(0)

crm_tasks = read_csv(crm_tasks_path)
opportunities = read_csv(opportunities_path)
fans = read_csv(fans_path)
segments = read_csv(segments_path)
accounts = read_csv(accounts_path)
games = read_csv(games_path)
promotions = read_csv(promotions_path)
orders = read_csv(orders_path)
scans = read_csv(scans_path)
merch = read_csv(merch_path)
concessions = read_csv(concessions_path)
engagement = read_csv(engagement_path)
group_sales = read_csv(group_sales_path)

games["game_date_dt"] = pd.to_datetime(games["game_date"])

game_context = games[[
    "game_id",
    "season",
    "game_date",
    "opponent",
    "day_of_week",
    "homestand_id",
    "weekend_flag"
]].copy()

promo_context = (
    promotions
    .groupby("game_id", as_index=False)
    .agg(
        promo_names=("promo_name", join_unique),
        promo_categories=("promo_category", join_unique),
        promo_types=("promo_type", join_unique)
    )
)

game_context = game_context.merge(promo_context, on="game_id", how="left")

for column in ["promo_names", "promo_categories", "promo_types"]:
    game_context[column] = game_context[column].fillna("")

segment_context = (
    segments
    .groupby("fan_id", as_index=False)
    .agg(
        fan_segments=("segment_name", join_unique),
        segment_types=("segment_type", join_unique),
        max_segment_score=("segment_score", lambda x: to_number(x).max())
    )
)

orders["ticket_quantity"] = to_number(orders["ticket_quantity"])
orders["net_ticket_revenue"] = to_number(orders["net_ticket_revenue"])
orders["premium_flag_bool"] = to_bool(orders["premium_flag"])
orders["group_order_flag_bool"] = to_bool(orders["group_order_flag"])
orders["order_date_dt"] = pd.to_datetime(orders["order_date"])

fan_ticket_summary = (
    orders
    .groupby("fan_id", as_index=False)
    .agg(
        fan_ticket_order_count=("order_id", "nunique"),
        fan_ticket_quantity=("ticket_quantity", "sum"),
        fan_ticket_revenue=("net_ticket_revenue", "sum"),
        fan_games_purchased=("game_id", "nunique"),
        fan_premium_order_count=("premium_flag_bool", "sum"),
        fan_group_order_count=("group_order_flag_bool", "sum"),
        fan_last_purchase_date=("order_date_dt", "max")
    )
)

fan_ticket_summary["fan_last_purchase_date"] = fan_ticket_summary["fan_last_purchase_date"].dt.date.astype(str)

scans = scans.merge(
    games[["game_id", "game_date_dt"]],
    on="game_id",
    how="left"
)

scans["ticket_quantity"] = to_number(scans["ticket_quantity"])
scans["scanned_ticket_quantity"] = to_number(scans["scanned_ticket_quantity"])
scans["no_show_ticket_quantity"] = to_number(scans["no_show_ticket_quantity"])
scans["attended_flag"] = scans["scanned_ticket_quantity"] > 0

fan_scan_summary = (
    scans
    .groupby("fan_id", as_index=False)
    .agg(
        fan_scan_ticket_quantity=("ticket_quantity", "sum"),
        fan_scanned_ticket_quantity=("scanned_ticket_quantity", "sum"),
        fan_no_show_ticket_quantity=("no_show_ticket_quantity", "sum"),
        fan_games_attended=("game_id", lambda x: x[scans.loc[x.index, "attended_flag"]].nunique()),
        fan_last_attended_date=("game_date_dt", "max")
    )
)

fan_scan_summary["fan_scan_rate"] = safe_divide(
    fan_scan_summary["fan_scanned_ticket_quantity"],
    fan_scan_summary["fan_scan_ticket_quantity"]
)

fan_scan_summary["fan_no_show_rate"] = safe_divide(
    fan_scan_summary["fan_no_show_ticket_quantity"],
    fan_scan_summary["fan_scan_ticket_quantity"]
)

fan_scan_summary["fan_last_attended_date"] = fan_scan_summary["fan_last_attended_date"].dt.date.astype(str)

merch = merch[merch["fan_id"].astype(str).str.strip() != ""].copy()
merch["net_sales"] = to_number(merch["net_sales"])

fan_merch_summary = (
    merch
    .groupby("fan_id", as_index=False)
    .agg(
        fan_merch_transaction_count=("merch_transaction_id", "count"),
        fan_merch_revenue=("net_sales", "sum")
    )
)

concessions = concessions[concessions["fan_id"].astype(str).str.strip() != ""].copy()
concessions["net_sales"] = to_number(concessions["net_sales"])

fan_concession_summary = (
    concessions
    .groupby("fan_id", as_index=False)
    .agg(
        fan_concession_transaction_count=("concession_transaction_id", "count"),
        fan_concession_revenue=("net_sales", "sum")
    )
)

engagement["engagement_score"] = to_number(engagement["engagement_score"])
engagement["engagement_date_dt"] = pd.to_datetime(engagement["engagement_date"])

fan_engagement_summary = (
    engagement
    .groupby("fan_id", as_index=False)
    .agg(
        fan_engagement_count=("engagement_id", "count"),
        fan_avg_engagement_score=("engagement_score", "mean"),
        fan_last_engagement_date=("engagement_date_dt", "max"),
        fan_engagement_types=("engagement_type", join_unique),
        fan_engagement_channels=("engagement_channel", join_unique)
    )
)

fan_engagement_summary["fan_last_engagement_date"] = fan_engagement_summary["fan_last_engagement_date"].dt.date.astype(str)

fan_summary = fans.copy()

fan_rollups = [
    segment_context,
    fan_ticket_summary,
    fan_scan_summary,
    fan_merch_summary,
    fan_concession_summary,
    fan_engagement_summary
]

for rollup in fan_rollups:
    fan_summary = fan_summary.merge(rollup, on="fan_id", how="left")

fan_numeric_columns = [
    "max_segment_score",
    "fan_ticket_order_count",
    "fan_ticket_quantity",
    "fan_ticket_revenue",
    "fan_games_purchased",
    "fan_premium_order_count",
    "fan_group_order_count",
    "fan_scan_ticket_quantity",
    "fan_scanned_ticket_quantity",
    "fan_no_show_ticket_quantity",
    "fan_games_attended",
    "fan_scan_rate",
    "fan_no_show_rate",
    "fan_merch_transaction_count",
    "fan_merch_revenue",
    "fan_concession_transaction_count",
    "fan_concession_revenue",
    "fan_engagement_count",
    "fan_avg_engagement_score"
]

for column in fan_numeric_columns:
    if column not in fan_summary.columns:
        fan_summary[column] = 0
    fan_summary[column] = to_number(fan_summary[column])

fan_text_columns = [
    "fan_segments",
    "segment_types",
    "fan_last_purchase_date",
    "fan_last_attended_date",
    "fan_last_engagement_date",
    "fan_engagement_types",
    "fan_engagement_channels"
]

for column in fan_text_columns:
    if column not in fan_summary.columns:
        fan_summary[column] = ""
    fan_summary[column] = fan_summary[column].fillna("")

fan_summary["fan_in_park_revenue"] = (
    fan_summary["fan_merch_revenue"]
    + fan_summary["fan_concession_revenue"]
)

fan_summary["fan_total_value"] = (
    fan_summary["fan_ticket_revenue"]
    + fan_summary["fan_merch_revenue"]
    + fan_summary["fan_concession_revenue"]
)

fan_summary["fan_hidden_value_flag"] = (
    (fan_summary["fan_in_park_revenue"] >= 125)
    & (fan_summary["fan_ticket_revenue"] < 300)
)

fan_summary["fan_display_name"] = fan_summary["fan_id"]

group_sales["group_ticket_quantity"] = to_number(group_sales["group_ticket_quantity"])
group_sales["group_ticket_revenue"] = to_number(group_sales["group_ticket_revenue"])
group_sales["group_scan_rate"] = to_number(group_sales["group_scan_rate"])
group_sales["renewal_flag_bool"] = to_bool(group_sales["renewal_flag"])
group_sales["upsell_flag_bool"] = to_bool(group_sales["upsell_flag"])

account_sales_summary = (
    group_sales
    .groupby("account_id", as_index=False)
    .agg(
        account_group_sale_count=("group_sale_id", "count"),
        account_group_ticket_quantity=("group_ticket_quantity", "sum"),
        account_group_revenue=("group_ticket_revenue", "sum"),
        account_avg_group_scan_rate=("group_scan_rate", "mean"),
        account_renewal_opportunity_count=("renewal_flag_bool", "sum"),
        account_upsell_opportunity_count=("upsell_flag_bool", "sum"),
        account_group_types=("group_type", join_unique),
        account_event_types=("event_type", join_unique)
    )
)

account_summary = accounts.merge(account_sales_summary, on="account_id", how="left")

account_numeric_columns = [
    "account_group_sale_count",
    "account_group_ticket_quantity",
    "account_group_revenue",
    "account_avg_group_scan_rate",
    "account_renewal_opportunity_count",
    "account_upsell_opportunity_count"
]

for column in account_numeric_columns:
    if column not in account_summary.columns:
        account_summary[column] = 0
    account_summary[column] = to_number(account_summary[column])

for column in ["account_group_types", "account_event_types"]:
    if column not in account_summary.columns:
        account_summary[column] = ""
    account_summary[column] = account_summary[column].fillna("")

account_summary["account_total_value"] = account_summary["account_group_revenue"]
account_summary["account_display_name"] = account_summary["account_name"]

queue = crm_tasks.merge(
    opportunities,
    on="opportunity_id",
    how="left",
    suffixes=("", "_opportunity")
)

for column in ["fan_id", "account_id", "game_id"]:
    opportunity_column = f"{column}_opportunity"
    if opportunity_column in queue.columns:
        queue[column] = queue[column].fillna(queue[opportunity_column])
        queue = queue.drop(columns=[opportunity_column])

queue = queue.merge(
    game_context,
    on="game_id",
    how="left"
)

queue = queue.merge(
    fan_summary,
    on="fan_id",
    how="left"
)

queue = queue.merge(
    account_summary,
    on="account_id",
    how="left"
)

queue["entity_type"] = "fan"
queue.loc[queue["account_id"].astype(str).str.strip() != "", "entity_type"] = "account"

queue["entity_id"] = queue["fan_id"]
queue.loc[queue["entity_type"] == "account", "entity_id"] = queue["account_id"]

queue["entity_display_name"] = queue["fan_display_name"]
queue.loc[queue["entity_type"] == "account", "entity_display_name"] = queue["account_display_name"]

queue["entity_total_value"] = to_number(queue["fan_total_value"])
queue.loc[queue["entity_type"] == "account", "entity_total_value"] = to_number(queue["account_total_value"])

queue["entity_ticket_revenue"] = to_number(queue["fan_ticket_revenue"])
queue["entity_in_park_revenue"] = to_number(queue["fan_in_park_revenue"])

queue["entity_activity_summary"] = ""
queue.loc[queue["entity_type"] == "fan", "entity_activity_summary"] = (
    "Games attended: "
    + to_number(queue["fan_games_attended"]).astype(int).astype(str)
    + " | Total value: $"
    + to_number(queue["fan_total_value"]).round(0).astype(int).astype(str)
    + " | Segments: "
    + queue["fan_segments"].fillna("")
)

queue.loc[queue["entity_type"] == "account", "entity_activity_summary"] = (
    "Group outings: "
    + to_number(queue["account_group_sale_count"]).astype(int).astype(str)
    + " | Group tickets: "
    + to_number(queue["account_group_ticket_quantity"]).astype(int).astype(str)
    + " | Group revenue: $"
    + to_number(queue["account_group_revenue"]).round(0).astype(int).astype(str)
)

queue["priority_rank"] = (
    to_number(queue["priority_score"]) * 1000000
    + to_number(queue["future_revenue_opportunity"]) * 10
).rank(method="first", ascending=False).astype(int)

queue["executive_action_bucket"] = queue["assigned_team"].map({
    "service": "Recover",
    "sales": "Upgrade",
    "marketing": "Retain",
    "group_sales": "Renew"
}).fillna("Review")

queue["dashboard_filter_label"] = (
    queue["priority_band"].astype(str)
    + " | "
    + queue["assigned_team"].astype(str)
    + " | "
    + queue["opportunity_type"].astype(str)
)

numeric_columns = [
    "priority_score",
    "opportunity_score",
    "future_revenue_opportunity",
    "repeat_likelihood_score",
    "upgrade_potential_score",
    "entity_total_value",
    "entity_ticket_revenue",
    "entity_in_park_revenue",
    "fan_ticket_order_count",
    "fan_ticket_quantity",
    "fan_ticket_revenue",
    "fan_games_purchased",
    "fan_premium_order_count",
    "fan_group_order_count",
    "fan_scan_ticket_quantity",
    "fan_scanned_ticket_quantity",
    "fan_no_show_ticket_quantity",
    "fan_games_attended",
    "fan_scan_rate",
    "fan_no_show_rate",
    "fan_merch_transaction_count",
    "fan_merch_revenue",
    "fan_concession_transaction_count",
    "fan_concession_revenue",
    "fan_engagement_count",
    "fan_avg_engagement_score",
    "fan_in_park_revenue",
    "fan_total_value",
    "account_group_sale_count",
    "account_group_ticket_quantity",
    "account_group_revenue",
    "account_avg_group_scan_rate",
    "account_renewal_opportunity_count",
    "account_upsell_opportunity_count",
    "account_total_value"
]

for column in numeric_columns:
    if column not in queue.columns:
        queue[column] = 0
    queue[column] = to_number(queue[column])

text_columns = [
    "season",
    "game_date",
    "opponent",
    "day_of_week",
    "homestand_id",
    "weekend_flag",
    "promo_names",
    "promo_categories",
    "promo_types",
    "fan_segments",
    "segment_types",
    "market_distance_band",
    "fan_last_purchase_date",
    "fan_last_attended_date",
    "fan_last_engagement_date",
    "fan_engagement_types",
    "fan_engagement_channels",
    "account_name",
    "account_type",
    "account_owner",
    "industry",
    "city",
    "zip_code",
    "renewal_status",
    "account_group_types",
    "account_event_types"
]

for column in text_columns:
    if column not in queue.columns:
        queue[column] = ""
    queue[column] = queue[column].fillna("")

ordered_columns = [
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
    "promo_names",
    "promo_categories",
    "promo_types",
    "fan_id",
    "fan_segments",
    "market_distance_band",
    "email_opt_in_flag",
    "sms_opt_in_flag",
    "family_flag",
    "corporate_flag",
    "youth_sports_flag",
    "fan_ticket_order_count",
    "fan_ticket_quantity",
    "fan_ticket_revenue",
    "fan_games_purchased",
    "fan_games_attended",
    "fan_scan_rate",
    "fan_no_show_rate",
    "fan_merch_revenue",
    "fan_concession_revenue",
    "fan_in_park_revenue",
    "fan_total_value",
    "fan_hidden_value_flag",
    "fan_engagement_count",
    "fan_avg_engagement_score",
    "fan_last_purchase_date",
    "fan_last_attended_date",
    "fan_last_engagement_date",
    "account_id",
    "account_name",
    "account_type",
    "account_owner",
    "industry",
    "city",
    "zip_code",
    "renewal_status",
    "account_group_sale_count",
    "account_group_ticket_quantity",
    "account_group_revenue",
    "account_avg_group_scan_rate",
    "account_renewal_opportunity_count",
    "account_upsell_opportunity_count",
    "account_total_value",
    "synthetic_data_flag"
]

for column in ordered_columns:
    if column not in queue.columns:
        queue[column] = ""

queue = queue[ordered_columns]
queue = queue.sort_values(["priority_rank"])

money_columns = [
    "future_revenue_opportunity",
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

rate_columns = [
    "fan_scan_rate",
    "fan_no_show_rate",
    "fan_avg_engagement_score",
    "account_avg_group_scan_rate"
]

for column in money_columns:
    queue[column] = to_number(queue[column]).round(2)

for column in rate_columns:
    queue[column] = to_number(queue[column]).round(4)

queue.to_csv(queue_path, index=False)

summary_rows = [
    {"metric": "crm_follow_up_queue_rows", "value": len(queue)},
    {"metric": "fan_task_rows", "value": int((queue["entity_type"] == "fan").sum())},
    {"metric": "account_task_rows", "value": int((queue["entity_type"] == "account").sum())},
    {"metric": "high_priority_rows", "value": int((queue["priority_band"] == "High").sum())},
    {"metric": "medium_priority_rows", "value": int((queue["priority_band"] == "Medium").sum())},
    {"metric": "total_future_revenue_opportunity", "value": round(float(to_number(queue["future_revenue_opportunity"]).sum()), 2)},
    {"metric": "average_priority_score", "value": round(float(to_number(queue["priority_score"]).mean()), 2)}
]

for team, count in queue["assigned_team"].value_counts().sort_index().items():
    summary_rows.append({"metric": f"assigned_team_count_{team}", "value": int(count)})

for bucket, count in queue["executive_action_bucket"].value_counts().sort_index().items():
    summary_rows.append({"metric": f"executive_action_bucket_count_{bucket}", "value": int(count)})

for opportunity_type, count in queue["opportunity_type"].value_counts().sort_index().items():
    summary_rows.append({"metric": f"opportunity_type_count_{opportunity_type}", "value": int(count)})

summary = pd.DataFrame(summary_rows)
summary.to_csv(summary_path, index=False)

print(f"Wrote {queue_path} with {len(queue)} CRM queue rows")
print(f"Wrote {summary_path}")
print(
    queue[
        [
            "priority_rank",
            "assigned_team",
            "priority_band",
            "opportunity_type",
            "entity_type",
            "entity_id",
            "future_revenue_opportunity",
            "suggested_action"
        ]
    ].head(10).to_string(index=False)
)