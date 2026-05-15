from pathlib import Path
import pandas as pd

games_path = Path("data/processed/games_clean.csv")
attendance_path = Path("data/processed/attendance_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")
group_sales_path = Path("data/synthetic/group_sales.csv")
merch_path = Path("data/synthetic/merch_transactions.csv")
concessions_path = Path("data/synthetic/concession_transactions.csv")
sponsorship_path = Path("data/synthetic/sponsorship_activations.csv")
engagement_path = Path("data/synthetic/fan_engagement.csv")
opportunities_path = Path("data/synthetic/follow_up_opportunities.csv")
crm_tasks_path = Path("data/synthetic/crm_follow_ups.csv")

output_dir = Path("data/exports")
output_dir.mkdir(parents=True, exist_ok=True)

homestand_path = output_dir / "homestand_summary.csv"
summary_path = output_dir / "homestand_summary_generation_summary.csv"

def read_csv(path):
    return pd.read_csv(path, dtype=str)

def to_number(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def to_bool(series):
    return series.astype(str).str.lower().eq("true")

def safe_divide(numerator, denominator):
    numerator = to_number(numerator)
    denominator = to_number(denominator)
    return numerator.div(denominator.where(denominator != 0)).fillna(0)

def minmax(series):
    series = to_number(series)
    low = series.min()
    high = series.max()

    if high == low:
        return pd.Series([0.5] * len(series), index=series.index)

    return (series - low) / (high - low)

def join_unique(values):
    clean_values = sorted(
        set(str(value).strip() for value in values if str(value).strip() not in {"", "nan", "None"})
    )
    return " | ".join(clean_values)

games = read_csv(games_path)
attendance = read_csv(attendance_path)
promotions = read_csv(promotions_path)
orders = read_csv(orders_path)
scans = read_csv(scans_path)
group_sales = read_csv(group_sales_path)
merch = read_csv(merch_path)
concessions = read_csv(concessions_path)
sponsorship = read_csv(sponsorship_path)
engagement = read_csv(engagement_path)
opportunities = read_csv(opportunities_path)
crm_tasks = read_csv(crm_tasks_path)

games["season"] = games["season"].astype(str)
games["game_date_dt"] = pd.to_datetime(games["game_date"])

game_lookup = games[[
    "game_id",
    "season",
    "homestand_id",
    "game_date",
    "game_date_dt",
    "day_of_week"
]].copy()

homestand_base = (
    games
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        homestand_start_date=("game_date_dt", "min"),
        homestand_end_date=("game_date_dt", "max"),
        game_count=("game_id", "count"),
        weekend_game_count=("weekend_flag", lambda x: to_bool(x).sum()),
        opponents=("opponent", join_unique)
    )
)

homestand_base["homestand_start_date"] = homestand_base["homestand_start_date"].dt.date.astype(str)
homestand_base["homestand_end_date"] = homestand_base["homestand_end_date"].dt.date.astype(str)

attendance = attendance.merge(
    game_lookup[["game_id", "homestand_id"]],
    on="game_id",
    how="left"
)

attendance["season"] = attendance["season"].astype(str)
attendance["announced_attendance"] = to_number(attendance["announced_attendance"])
attendance["matched_attendance_flag"] = attendance["attendance_match_status"].astype(str).eq("matched")

attendance_rollup = (
    attendance[attendance["matched_attendance_flag"]]
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        public_announced_attendance=("announced_attendance", "sum"),
        matched_attendance_game_count=("game_id", "count")
    )
)

orders = orders.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left"
)

orders["season"] = orders["season"].astype(str)
orders["ticket_quantity"] = to_number(orders["ticket_quantity"])
orders["net_ticket_revenue"] = to_number(orders["net_ticket_revenue"])
orders["premium_flag_bool"] = to_bool(orders["premium_flag"])
orders["group_order_flag_bool"] = to_bool(orders["group_order_flag"])

ticket_rollup = (
    orders
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        ticket_order_count=("order_id", "nunique"),
        tickets_sold=("ticket_quantity", "sum"),
        net_ticket_revenue=("net_ticket_revenue", "sum"),
        premium_order_count=("premium_flag_bool", "sum"),
        group_ticket_order_count=("group_order_flag_bool", "sum"),
        unique_ticket_buyers=("fan_id", "nunique")
    )
)

scans = scans.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left"
)

scans["season"] = scans["season"].astype(str)
scans["ticket_quantity"] = to_number(scans["ticket_quantity"])
scans["scanned_ticket_quantity"] = to_number(scans["scanned_ticket_quantity"])
scans["no_show_ticket_quantity"] = to_number(scans["no_show_ticket_quantity"])

scan_rollup = (
    scans
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        scan_ticket_quantity=("ticket_quantity", "sum"),
        scanned_attendance=("scanned_ticket_quantity", "sum"),
        no_show_ticket_quantity=("no_show_ticket_quantity", "sum")
    )
)

promotions = promotions.merge(
    game_lookup[["game_id", "homestand_id"]],
    on="game_id",
    how="left"
)

promotions["season"] = promotions["season"].astype(str)
promotions["primary_promo_flag_bool"] = to_bool(promotions["primary_promo_flag"])
promotions["giveaway_flag_bool"] = to_bool(promotions["giveaway_flag"])
promotions["fireworks_flag_bool"] = to_bool(promotions["fireworks_flag"])
promotions["theme_night_flag_bool"] = to_bool(promotions["theme_night_flag"])
promotions["family_flag_bool"] = to_bool(promotions["family_flag"])

promotion_rollup = (
    promotions
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        promotion_count=("promo_id", "count"),
        primary_promo_count=("primary_promo_flag_bool", "sum"),
        giveaway_count=("giveaway_flag_bool", "sum"),
        fireworks_count=("fireworks_flag_bool", "sum"),
        theme_night_count=("theme_night_flag_bool", "sum"),
        family_promo_count=("family_flag_bool", "sum"),
        promo_categories=("promo_category", join_unique)
    )
)

group_sales = group_sales.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left"
)

group_sales["season"] = group_sales["season"].astype(str)
group_sales["group_ticket_quantity"] = to_number(group_sales["group_ticket_quantity"])
group_sales["group_ticket_revenue"] = to_number(group_sales["group_ticket_revenue"])
group_sales["renewal_flag_bool"] = to_bool(group_sales["renewal_flag"])
group_sales["upsell_flag_bool"] = to_bool(group_sales["upsell_flag"])

group_rollup = (
    group_sales
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        group_sale_count=("group_sale_id", "count"),
        group_ticket_quantity=("group_ticket_quantity", "sum"),
        group_ticket_revenue=("group_ticket_revenue", "sum"),
        group_renewal_opportunity_count=("renewal_flag_bool", "sum"),
        group_upsell_opportunity_count=("upsell_flag_bool", "sum"),
        group_types=("group_type", join_unique)
    )
)

merch = merch.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left"
)

merch["season"] = merch["season"].astype(str)
merch["net_sales"] = to_number(merch["net_sales"])
merch["fan_match_flag_bool"] = to_bool(merch["fan_match_flag"])

merch_rollup = (
    merch
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        merch_transaction_count=("merch_transaction_id", "count"),
        merch_net_sales=("net_sales", "sum"),
        fan_matched_merch_transactions=("fan_match_flag_bool", "sum")
    )
)

concessions = concessions.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left"
)

concessions["season"] = concessions["season"].astype(str)
concessions["net_sales"] = to_number(concessions["net_sales"])
concessions["fan_match_flag_bool"] = to_bool(concessions["fan_match_flag"])

concession_rollup = (
    concessions
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        concession_transaction_count=("concession_transaction_id", "count"),
        concession_net_sales=("net_sales", "sum"),
        fan_matched_concession_transactions=("fan_match_flag_bool", "sum")
    )
)

sponsorship = sponsorship.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left"
)

sponsorship["season"] = sponsorship["season"].astype(str)

sponsorship_rollup = (
    sponsorship
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        sponsorship_activation_count=("activation_id", "count"),
        unique_sponsor_count=("sponsor_id", "nunique"),
        sponsorship_goals=("activation_goal", join_unique)
    )
)

engagement = engagement[engagement["game_id"].astype(str).str.strip() != ""].copy()

engagement = engagement.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left"
)

engagement["season"] = engagement["season"].astype(str)
engagement["engagement_score"] = to_number(engagement["engagement_score"])

engagement_rollup = (
    engagement
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        fan_engagement_count=("engagement_id", "count"),
        unique_engaged_fans=("fan_id", "nunique"),
        avg_engagement_score=("engagement_score", "mean")
    )
)

opportunities = opportunities[opportunities["game_id"].astype(str).str.strip() != ""].copy()

opportunities = opportunities.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left",
    suffixes=("", "_lookup")
)

if "homestand_id_lookup" in opportunities.columns:
    opportunities["homestand_id"] = opportunities["homestand_id_lookup"].fillna(opportunities["homestand_id"])
    opportunities = opportunities.drop(columns=["homestand_id_lookup"])

opportunities["season"] = opportunities["season"].astype(str)
opportunities["opportunity_score"] = to_number(opportunities["opportunity_score"])
opportunities["future_revenue_opportunity"] = to_number(opportunities["future_revenue_opportunity"])

opportunity_rollup = (
    opportunities
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        follow_up_opportunity_count=("opportunity_id", "count"),
        high_priority_opportunity_count=("priority_band", lambda x: (x == "High").sum()),
        medium_priority_opportunity_count=("priority_band", lambda x: (x == "Medium").sum()),
        future_revenue_opportunity=("future_revenue_opportunity", "sum"),
        avg_opportunity_score=("opportunity_score", "mean")
    )
)

crm_tasks = crm_tasks[crm_tasks["game_id"].astype(str).str.strip() != ""].copy()

crm_tasks = crm_tasks.merge(
    game_lookup[["game_id", "season", "homestand_id"]],
    on="game_id",
    how="left"
)

crm_tasks["season"] = crm_tasks["season"].astype(str)

crm_rollup = (
    crm_tasks
    .groupby(["season", "homestand_id"], as_index=False)
    .agg(
        crm_follow_up_task_count=("follow_up_id", "count"),
        sales_task_count=("assigned_team", lambda x: (x == "sales").sum()),
        marketing_task_count=("assigned_team", lambda x: (x == "marketing").sum()),
        service_task_count=("assigned_team", lambda x: (x == "service").sum()),
        group_sales_task_count=("assigned_team", lambda x: (x == "group_sales").sum())
    )
)

summary = homestand_base.copy()

rollups = [
    attendance_rollup,
    ticket_rollup,
    scan_rollup,
    promotion_rollup,
    group_rollup,
    merch_rollup,
    concession_rollup,
    sponsorship_rollup,
    engagement_rollup,
    opportunity_rollup,
    crm_rollup
]

for rollup in rollups:
    summary = summary.merge(rollup, on=["season", "homestand_id"], how="left")

numeric_columns = [
    "game_count",
    "weekend_game_count",
    "public_announced_attendance",
    "matched_attendance_game_count",
    "ticket_order_count",
    "tickets_sold",
    "net_ticket_revenue",
    "premium_order_count",
    "group_ticket_order_count",
    "unique_ticket_buyers",
    "scan_ticket_quantity",
    "scanned_attendance",
    "no_show_ticket_quantity",
    "promotion_count",
    "primary_promo_count",
    "giveaway_count",
    "fireworks_count",
    "theme_night_count",
    "family_promo_count",
    "group_sale_count",
    "group_ticket_quantity",
    "group_ticket_revenue",
    "group_renewal_opportunity_count",
    "group_upsell_opportunity_count",
    "merch_transaction_count",
    "merch_net_sales",
    "fan_matched_merch_transactions",
    "concession_transaction_count",
    "concession_net_sales",
    "fan_matched_concession_transactions",
    "sponsorship_activation_count",
    "unique_sponsor_count",
    "fan_engagement_count",
    "unique_engaged_fans",
    "avg_engagement_score",
    "follow_up_opportunity_count",
    "high_priority_opportunity_count",
    "medium_priority_opportunity_count",
    "future_revenue_opportunity",
    "avg_opportunity_score",
    "crm_follow_up_task_count",
    "sales_task_count",
    "marketing_task_count",
    "service_task_count",
    "group_sales_task_count"
]

for column in numeric_columns:
    if column not in summary.columns:
        summary[column] = 0
    summary[column] = to_number(summary[column])

text_columns = [
    "promo_categories",
    "group_types",
    "sponsorship_goals"
]

for column in text_columns:
    if column not in summary.columns:
        summary[column] = ""
    summary[column] = summary[column].fillna("")

summary["scan_rate"] = safe_divide(summary["scanned_attendance"], summary["scan_ticket_quantity"])
summary["no_show_rate"] = safe_divide(summary["no_show_ticket_quantity"], summary["scan_ticket_quantity"])
summary["revenue_per_scanned_fan"] = safe_divide(summary["net_ticket_revenue"], summary["scanned_attendance"])
summary["merch_per_scanned_fan"] = safe_divide(summary["merch_net_sales"], summary["scanned_attendance"])
summary["concession_per_scanned_fan"] = safe_divide(summary["concession_net_sales"], summary["scanned_attendance"])
summary["in_park_spend_per_scanned_fan"] = safe_divide(
    summary["merch_net_sales"] + summary["concession_net_sales"],
    summary["scanned_attendance"]
)
summary["total_revenue_indicator"] = (
    summary["net_ticket_revenue"]
    + summary["merch_net_sales"]
    + summary["concession_net_sales"]
)

summary["homestand_total_value_index"] = (
    minmax(summary["total_revenue_indicator"]) * 40
    + minmax(summary["scan_rate"]) * 15
    + minmax(summary["in_park_spend_per_scanned_fan"]) * 15
    + minmax(summary["group_ticket_quantity"]) * 10
    + minmax(summary["follow_up_opportunity_count"]) * 10
    + minmax(summary["fan_engagement_count"]) * 10
).round(1)

def recommended_focus(row):
    if row["no_show_rate"] >= 0.13 and row["high_priority_opportunity_count"] >= 100:
        return "No-show recovery"

    if row["group_ticket_quantity"] >= summary["group_ticket_quantity"].quantile(0.75):
        return "Group sales renewal"

    if row["in_park_spend_per_scanned_fan"] >= summary["in_park_spend_per_scanned_fan"].quantile(0.75):
        return "In-park spend growth"

    if row["fan_engagement_count"] >= summary["fan_engagement_count"].quantile(0.75):
        return "Engagement follow-up"

    if row["homestand_total_value_index"] >= summary["homestand_total_value_index"].quantile(0.75):
        return "Repeat what worked"

    return "Baseline review"

summary["recommended_focus"] = summary.apply(recommended_focus, axis=1)

ordered_columns = [
    "season",
    "homestand_id",
    "homestand_start_date",
    "homestand_end_date",
    "game_count",
    "weekend_game_count",
    "opponents",
    "public_announced_attendance",
    "matched_attendance_game_count",
    "tickets_sold",
    "scanned_attendance",
    "scan_rate",
    "no_show_ticket_quantity",
    "no_show_rate",
    "ticket_order_count",
    "unique_ticket_buyers",
    "net_ticket_revenue",
    "group_ticket_quantity",
    "group_ticket_revenue",
    "group_sale_count",
    "group_renewal_opportunity_count",
    "group_upsell_opportunity_count",
    "merch_transaction_count",
    "merch_net_sales",
    "fan_matched_merch_transactions",
    "concession_transaction_count",
    "concession_net_sales",
    "fan_matched_concession_transactions",
    "revenue_per_scanned_fan",
    "merch_per_scanned_fan",
    "concession_per_scanned_fan",
    "in_park_spend_per_scanned_fan",
    "total_revenue_indicator",
    "promotion_count",
    "primary_promo_count",
    "giveaway_count",
    "fireworks_count",
    "theme_night_count",
    "family_promo_count",
    "promo_categories",
    "sponsorship_activation_count",
    "unique_sponsor_count",
    "sponsorship_goals",
    "fan_engagement_count",
    "unique_engaged_fans",
    "avg_engagement_score",
    "follow_up_opportunity_count",
    "high_priority_opportunity_count",
    "medium_priority_opportunity_count",
    "crm_follow_up_task_count",
    "sales_task_count",
    "marketing_task_count",
    "service_task_count",
    "group_sales_task_count",
    "future_revenue_opportunity",
    "avg_opportunity_score",
    "homestand_total_value_index",
    "recommended_focus"
]

summary = summary[ordered_columns]
summary = summary.sort_values(["season", "homestand_start_date"])

money_columns = [
    "net_ticket_revenue",
    "group_ticket_revenue",
    "merch_net_sales",
    "concession_net_sales",
    "revenue_per_scanned_fan",
    "merch_per_scanned_fan",
    "concession_per_scanned_fan",
    "in_park_spend_per_scanned_fan",
    "total_revenue_indicator",
    "future_revenue_opportunity"
]

rate_columns = [
    "scan_rate",
    "no_show_rate",
    "avg_engagement_score",
    "avg_opportunity_score",
    "homestand_total_value_index"
]

for column in money_columns:
    summary[column] = summary[column].round(2)

for column in rate_columns:
    summary[column] = summary[column].round(4)

summary.to_csv(homestand_path, index=False)

generation_summary = pd.DataFrame([
    {"metric": "homestand_rows", "value": len(summary)},
    {"metric": "total_games", "value": int(summary["game_count"].sum())},
    {"metric": "total_tickets_sold", "value": int(summary["tickets_sold"].sum())},
    {"metric": "total_scanned_attendance", "value": int(summary["scanned_attendance"].sum())},
    {"metric": "total_revenue_indicator", "value": round(float(summary["total_revenue_indicator"].sum()), 2)},
    {"metric": "total_follow_up_opportunities", "value": int(summary["follow_up_opportunity_count"].sum())},
    {"metric": "total_crm_follow_up_tasks", "value": int(summary["crm_follow_up_task_count"].sum())}
])

generation_summary.to_csv(summary_path, index=False)

print(f"Wrote {homestand_path} with {len(summary)} homestand rows")
print(f"Wrote {summary_path}")
print(
    summary[
        [
            "season",
            "homestand_id",
            "game_count",
            "tickets_sold",
            "scanned_attendance",
            "total_revenue_indicator",
            "homestand_total_value_index",
            "recommended_focus"
        ]
    ].head(10).to_string(index=False)
)