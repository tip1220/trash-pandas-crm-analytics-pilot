from pathlib import Path
import pandas as pd

games_path = Path("data/processed/games_clean.csv")
promotions_path = Path("data/processed/promotions_clean.csv")
attendance_path = Path("data/processed/attendance_clean.csv")
orders_path = Path("data/synthetic/ticket_orders.csv")
scans_path = Path("data/synthetic/ticket_scans.csv")
group_sales_path = Path("data/synthetic/group_sales.csv")
merch_path = Path("data/synthetic/merch_transactions.csv")
concessions_path = Path("data/synthetic/concession_transactions.csv")
engagement_path = Path("data/synthetic/fan_engagement.csv")
opportunities_path = Path("data/synthetic/follow_up_opportunities.csv")
crm_tasks_path = Path("data/synthetic/crm_follow_ups.csv")

output_dir = Path("data/exports")
output_dir.mkdir(parents=True, exist_ok=True)

scorecard_path = output_dir / "promotion_scorecard.csv"
summary_path = output_dir / "promotion_scorecard_generation_summary.csv"

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

games = read_csv(games_path)
promotions = read_csv(promotions_path)
attendance = read_csv(attendance_path)
orders = read_csv(orders_path)
scans = read_csv(scans_path)
group_sales = read_csv(group_sales_path)
merch = read_csv(merch_path)
concessions = read_csv(concessions_path)
engagement = read_csv(engagement_path)
opportunities = read_csv(opportunities_path)
crm_tasks = read_csv(crm_tasks_path)

games["season"] = games["season"].astype(str)
games["game_date_dt"] = pd.to_datetime(games["game_date"])

game_lookup = games[[
    "game_id",
    "season",
    "game_date",
    "game_date_dt",
    "opponent",
    "day_of_week",
    "homestand_id",
    "weekend_flag"
]].copy()

attendance = attendance.merge(
    game_lookup[["game_id", "season", "day_of_week"]],
    on="game_id",
    how="left",
    suffixes=("", "_game")
)

attendance["announced_attendance"] = to_number(attendance["announced_attendance"])
attendance["matched_attendance_flag"] = attendance["attendance_match_status"].astype(str).eq("matched")

attendance_game = (
    attendance[attendance["matched_attendance_flag"]]
    .groupby("game_id", as_index=False)
    .agg(
        public_announced_attendance=("announced_attendance", "sum")
    )
)

orders = orders.merge(
    game_lookup[["game_id", "season", "game_date_dt", "day_of_week"]],
    on="game_id",
    how="left"
)

orders["ticket_quantity"] = to_number(orders["ticket_quantity"])
orders["net_ticket_revenue"] = to_number(orders["net_ticket_revenue"])

ticket_game = (
    orders
    .groupby("game_id", as_index=False)
    .agg(
        ticket_order_count=("order_id", "nunique"),
        tickets_sold=("ticket_quantity", "sum"),
        net_ticket_revenue=("net_ticket_revenue", "sum"),
        unique_ticket_buyers=("fan_id", "nunique")
    )
)

fan_game_dates = (
    orders[["fan_id", "game_id", "game_date_dt"]]
    .drop_duplicates()
    .sort_values(["fan_id", "game_date_dt"])
)

fan_prior_games = {}

for fan_id, group in fan_game_dates.groupby("fan_id"):
    prior_dates = []
    for _, row in group.iterrows():
        fan_prior_games[(fan_id, row["game_id"])] = len(prior_dates) > 0
        prior_dates.append(row["game_date_dt"])

repeat_rows = []

for game_id, group in orders.groupby("game_id"):
    buyers = group["fan_id"].dropna().unique()
    repeat_buyers = sum(1 for fan_id in buyers if fan_prior_games.get((fan_id, game_id), False))
    repeat_rows.append({
        "game_id": game_id,
        "repeat_buyer_count": repeat_buyers,
        "buyer_count_for_repeat_rate": len(buyers)
    })

repeat_game = pd.DataFrame(repeat_rows)

scans = scans.merge(
    game_lookup[["game_id", "season", "day_of_week"]],
    on="game_id",
    how="left"
)

scans["ticket_quantity"] = to_number(scans["ticket_quantity"])
scans["scanned_ticket_quantity"] = to_number(scans["scanned_ticket_quantity"])
scans["no_show_ticket_quantity"] = to_number(scans["no_show_ticket_quantity"])

scan_game = (
    scans
    .groupby("game_id", as_index=False)
    .agg(
        scan_ticket_quantity=("ticket_quantity", "sum"),
        scanned_attendance=("scanned_ticket_quantity", "sum"),
        no_show_ticket_quantity=("no_show_ticket_quantity", "sum")
    )
)

group_sales = group_sales.merge(
    game_lookup[["game_id", "season", "day_of_week"]],
    on="game_id",
    how="left"
)

group_sales["group_ticket_quantity"] = to_number(group_sales["group_ticket_quantity"])
group_sales["group_ticket_revenue"] = to_number(group_sales["group_ticket_revenue"])

group_game = (
    group_sales
    .groupby("game_id", as_index=False)
    .agg(
        group_sale_count=("group_sale_id", "count"),
        group_tickets=("group_ticket_quantity", "sum"),
        group_revenue=("group_ticket_revenue", "sum")
    )
)

merch = merch.merge(
    game_lookup[["game_id", "season", "day_of_week"]],
    on="game_id",
    how="left"
)

merch["net_sales"] = to_number(merch["net_sales"])
merch["promo_related_flag_bool"] = to_bool(merch["promo_related_flag"])

merch_game = (
    merch
    .groupby("game_id", as_index=False)
    .agg(
        merch_transaction_count=("merch_transaction_id", "count"),
        merch_net_sales=("net_sales", "sum"),
        promo_related_merch_transactions=("promo_related_flag_bool", "sum")
    )
)

concessions = concessions.merge(
    game_lookup[["game_id", "season", "day_of_week"]],
    on="game_id",
    how="left"
)

concessions["net_sales"] = to_number(concessions["net_sales"])

concession_game = (
    concessions
    .groupby("game_id", as_index=False)
    .agg(
        concession_transaction_count=("concession_transaction_id", "count"),
        concession_net_sales=("net_sales", "sum")
    )
)

engagement = engagement[engagement["game_id"].astype(str).str.strip() != ""].copy()

engagement = engagement.merge(
    game_lookup[["game_id", "season", "day_of_week"]],
    on="game_id",
    how="left"
)

engagement["engagement_score"] = to_number(engagement["engagement_score"])

engagement_game = (
    engagement
    .groupby("game_id", as_index=False)
    .agg(
        fan_engagement_count=("engagement_id", "count"),
        unique_engaged_fans=("fan_id", "nunique"),
        avg_engagement_score=("engagement_score", "mean")
    )
)

opportunities = opportunities[opportunities["game_id"].astype(str).str.strip() != ""].copy()

opportunities = opportunities.merge(
    game_lookup[["game_id", "season", "day_of_week"]],
    on="game_id",
    how="left",
    suffixes=("", "_game")
)

opportunities["opportunity_score"] = to_number(opportunities["opportunity_score"])
opportunities["future_revenue_opportunity"] = to_number(opportunities["future_revenue_opportunity"])

opportunity_game = (
    opportunities
    .groupby("game_id", as_index=False)
    .agg(
        follow_up_opportunity_count=("opportunity_id", "count"),
        high_priority_opportunity_count=("priority_band", lambda x: (x == "High").sum()),
        future_revenue_opportunity=("future_revenue_opportunity", "sum"),
        avg_opportunity_score=("opportunity_score", "mean")
    )
)

crm_tasks = crm_tasks[crm_tasks["game_id"].astype(str).str.strip() != ""].copy()

crm_task_game = (
    crm_tasks
    .groupby("game_id", as_index=False)
    .agg(
        crm_follow_up_task_count=("follow_up_id", "count")
    )
)

game_summary = game_lookup.copy()

game_rollups = [
    attendance_game,
    ticket_game,
    repeat_game,
    scan_game,
    group_game,
    merch_game,
    concession_game,
    engagement_game,
    opportunity_game,
    crm_task_game
]

for rollup in game_rollups:
    game_summary = game_summary.merge(rollup, on="game_id", how="left")

numeric_columns = [
    "public_announced_attendance",
    "ticket_order_count",
    "tickets_sold",
    "net_ticket_revenue",
    "unique_ticket_buyers",
    "repeat_buyer_count",
    "buyer_count_for_repeat_rate",
    "scan_ticket_quantity",
    "scanned_attendance",
    "no_show_ticket_quantity",
    "group_sale_count",
    "group_tickets",
    "group_revenue",
    "merch_transaction_count",
    "merch_net_sales",
    "promo_related_merch_transactions",
    "concession_transaction_count",
    "concession_net_sales",
    "fan_engagement_count",
    "unique_engaged_fans",
    "avg_engagement_score",
    "follow_up_opportunity_count",
    "high_priority_opportunity_count",
    "future_revenue_opportunity",
    "avg_opportunity_score",
    "crm_follow_up_task_count"
]

for column in numeric_columns:
    if column not in game_summary.columns:
        game_summary[column] = 0
    game_summary[column] = to_number(game_summary[column])

game_summary["scan_rate"] = safe_divide(game_summary["scanned_attendance"], game_summary["scan_ticket_quantity"])
game_summary["no_show_rate"] = safe_divide(game_summary["no_show_ticket_quantity"], game_summary["scan_ticket_quantity"])
game_summary["revenue_per_scanned_fan"] = safe_divide(game_summary["net_ticket_revenue"], game_summary["scanned_attendance"])
game_summary["merch_per_scanned_fan"] = safe_divide(game_summary["merch_net_sales"], game_summary["scanned_attendance"])
game_summary["concession_per_scanned_fan"] = safe_divide(game_summary["concession_net_sales"], game_summary["scanned_attendance"])
game_summary["in_park_spend_per_scanned_fan"] = safe_divide(
    game_summary["merch_net_sales"] + game_summary["concession_net_sales"],
    game_summary["scanned_attendance"]
)
game_summary["repeat_buyer_rate"] = safe_divide(
    game_summary["repeat_buyer_count"],
    game_summary["buyer_count_for_repeat_rate"]
)
game_summary["total_revenue_indicator"] = (
    game_summary["net_ticket_revenue"]
    + game_summary["merch_net_sales"]
    + game_summary["concession_net_sales"]
)

baseline = (
    game_summary
    .groupby(["season", "day_of_week"], as_index=False)
    .agg(
        baseline_scanned_attendance=("scanned_attendance", "mean"),
        baseline_merch_per_scanned_fan=("merch_per_scanned_fan", "mean"),
        baseline_concession_per_scanned_fan=("concession_per_scanned_fan", "mean"),
        baseline_revenue_per_scanned_fan=("revenue_per_scanned_fan", "mean"),
        baseline_total_revenue_indicator=("total_revenue_indicator", "mean"),
        baseline_repeat_buyer_rate=("repeat_buyer_rate", "mean")
    )
)

game_summary = game_summary.merge(
    baseline,
    on=["season", "day_of_week"],
    how="left"
)

game_summary["scanned_attendance_lift_vs_slot"] = (
    game_summary["scanned_attendance"]
    - game_summary["baseline_scanned_attendance"]
)

game_summary["merch_lift_per_scanned_fan"] = (
    game_summary["merch_per_scanned_fan"]
    - game_summary["baseline_merch_per_scanned_fan"]
)

game_summary["concession_lift_per_scanned_fan"] = (
    game_summary["concession_per_scanned_fan"]
    - game_summary["baseline_concession_per_scanned_fan"]
)

game_summary["revenue_lift_per_scanned_fan"] = (
    game_summary["revenue_per_scanned_fan"]
    - game_summary["baseline_revenue_per_scanned_fan"]
)

game_summary["repeat_buyer_rate_lift_vs_slot"] = (
    game_summary["repeat_buyer_rate"]
    - game_summary["baseline_repeat_buyer_rate"]
)

promotions = promotions.merge(
    game_lookup[[
        "game_id",
        "season",
        "game_date",
        "opponent",
        "day_of_week",
        "homestand_id",
        "weekend_flag"
    ]],
    on="game_id",
    how="left",
    suffixes=("", "_game")
)

if "season_game" in promotions.columns:
    promotions["season"] = promotions["season"].fillna(promotions["season_game"])
    promotions = promotions.drop(columns=["season_game"])

promo_scorecard = promotions.merge(
    game_summary.drop(columns=["season", "game_date", "opponent", "day_of_week", "homestand_id", "weekend_flag"]),
    on="game_id",
    how="left"
)

for column in numeric_columns + [
    "scan_rate",
    "no_show_rate",
    "revenue_per_scanned_fan",
    "merch_per_scanned_fan",
    "concession_per_scanned_fan",
    "in_park_spend_per_scanned_fan",
    "repeat_buyer_rate",
    "total_revenue_indicator",
    "scanned_attendance_lift_vs_slot",
    "merch_lift_per_scanned_fan",
    "concession_lift_per_scanned_fan",
    "revenue_lift_per_scanned_fan",
    "repeat_buyer_rate_lift_vs_slot"
]:
    if column not in promo_scorecard.columns:
        promo_scorecard[column] = 0
    promo_scorecard[column] = to_number(promo_scorecard[column])

promo_scorecard["total_value_index"] = (
    minmax(promo_scorecard["total_revenue_indicator"]) * 35
    + minmax(promo_scorecard["scanned_attendance_lift_vs_slot"]) * 20
    + minmax(promo_scorecard["scan_rate"]) * 10
    + minmax(promo_scorecard["in_park_spend_per_scanned_fan"]) * 15
    + minmax(promo_scorecard["group_tickets"]) * 10
    + minmax(promo_scorecard["follow_up_opportunity_count"]) * 10
).round(1)

def recommendation(row):
    total_value_index = row["total_value_index"]
    scanned_lift = row["scanned_attendance_lift_vs_slot"]
    revenue_lift = row["revenue_lift_per_scanned_fan"]
    repeat_lift = row["repeat_buyer_rate_lift_vs_slot"]
    no_show_rate = row["no_show_rate"]

    if total_value_index >= 70 and scanned_lift > 0 and revenue_lift >= 0:
        return "return"

    if total_value_index >= 55 and (scanned_lift > 0 or revenue_lift > 0 or repeat_lift > 0):
        return "rework"

    if total_value_index < 35 and scanned_lift < 0 and revenue_lift < 0 and repeat_lift <= 0:
        return "retire"

    if no_show_rate >= 0.15 and scanned_lift < 0:
        return "review"

    return "review"

promo_scorecard["recommendation"] = promo_scorecard.apply(recommendation, axis=1)

def recommendation_reason(row):
    if row["recommendation"] == "return":
        return "Strong total value with positive attendance and revenue lift"
    if row["recommendation"] == "rework":
        return "Shows value, but one or more connected metrics need improvement"
    if row["recommendation"] == "retire":
        return "Weak total value with negative attendance, revenue, and repeat buyer signals"
    return "Mixed performance; needs review before committing future promo inventory"

promo_scorecard["recommendation_reason"] = promo_scorecard.apply(recommendation_reason, axis=1)

ordered_columns = [
    "promo_id",
    "game_id",
    "season",
    "game_date",
    "homestand_id",
    "opponent",
    "day_of_week",
    "weekend_flag",
    "promo_name",
    "promo_category",
    "promo_type",
    "primary_promo_flag",
    "sponsor_attached_flag",
    "giveaway_flag",
    "fireworks_flag",
    "theme_night_flag",
    "family_flag",
    "dog_day_flag",
    "jersey_auction_flag",
    "expected_fan_segment",
    "public_announced_attendance",
    "tickets_sold",
    "scanned_attendance",
    "scan_rate",
    "no_show_ticket_quantity",
    "no_show_rate",
    "ticket_order_count",
    "unique_ticket_buyers",
    "repeat_buyer_count",
    "repeat_buyer_rate",
    "group_tickets",
    "group_revenue",
    "merch_net_sales",
    "concession_net_sales",
    "revenue_per_scanned_fan",
    "merch_per_scanned_fan",
    "concession_per_scanned_fan",
    "in_park_spend_per_scanned_fan",
    "total_revenue_indicator",
    "fan_engagement_count",
    "unique_engaged_fans",
    "avg_engagement_score",
    "follow_up_opportunity_count",
    "high_priority_opportunity_count",
    "crm_follow_up_task_count",
    "future_revenue_opportunity",
    "baseline_scanned_attendance",
    "baseline_merch_per_scanned_fan",
    "baseline_concession_per_scanned_fan",
    "baseline_revenue_per_scanned_fan",
    "baseline_repeat_buyer_rate",
    "scanned_attendance_lift_vs_slot",
    "merch_lift_per_scanned_fan",
    "concession_lift_per_scanned_fan",
    "revenue_lift_per_scanned_fan",
    "repeat_buyer_rate_lift_vs_slot",
    "total_value_index",
    "recommendation",
    "recommendation_reason"
]

for column in ordered_columns:
    if column not in promo_scorecard.columns:
        promo_scorecard[column] = ""

promo_scorecard = promo_scorecard[ordered_columns]
promo_scorecard = promo_scorecard.sort_values(["season", "game_date", "promo_id"])

money_columns = [
    "group_revenue",
    "merch_net_sales",
    "concession_net_sales",
    "revenue_per_scanned_fan",
    "merch_per_scanned_fan",
    "concession_per_scanned_fan",
    "in_park_spend_per_scanned_fan",
    "total_revenue_indicator",
    "future_revenue_opportunity",
    "baseline_merch_per_scanned_fan",
    "baseline_concession_per_scanned_fan",
    "baseline_revenue_per_scanned_fan",
    "merch_lift_per_scanned_fan",
    "concession_lift_per_scanned_fan",
    "revenue_lift_per_scanned_fan"
]

rate_columns = [
    "scan_rate",
    "no_show_rate",
    "repeat_buyer_rate",
    "avg_engagement_score",
    "baseline_repeat_buyer_rate",
    "repeat_buyer_rate_lift_vs_slot",
    "total_value_index"
]

count_columns = [
    "public_announced_attendance",
    "tickets_sold",
    "scanned_attendance",
    "no_show_ticket_quantity",
    "ticket_order_count",
    "unique_ticket_buyers",
    "repeat_buyer_count",
    "group_tickets",
    "fan_engagement_count",
    "unique_engaged_fans",
    "follow_up_opportunity_count",
    "high_priority_opportunity_count",
    "crm_follow_up_task_count",
    "baseline_scanned_attendance",
    "scanned_attendance_lift_vs_slot"
]

for column in money_columns:
    promo_scorecard[column] = to_number(promo_scorecard[column]).round(2)

for column in rate_columns:
    promo_scorecard[column] = to_number(promo_scorecard[column]).round(4)

for column in count_columns:
    promo_scorecard[column] = to_number(promo_scorecard[column]).round(0).astype(int)

promo_scorecard.to_csv(scorecard_path, index=False)

recommendation_counts = promo_scorecard["recommendation"].value_counts().to_dict()

generation_summary = pd.DataFrame([
    {"metric": "promotion_scorecard_rows", "value": len(promo_scorecard)},
    {"metric": "unique_promo_games", "value": promo_scorecard["game_id"].nunique()},
    {"metric": "return_recommendation_count", "value": recommendation_counts.get("return", 0)},
    {"metric": "rework_recommendation_count", "value": recommendation_counts.get("rework", 0)},
    {"metric": "retire_recommendation_count", "value": recommendation_counts.get("retire", 0)},
    {"metric": "review_recommendation_count", "value": recommendation_counts.get("review", 0)},
    {"metric": "average_total_value_index", "value": round(float(to_number(promo_scorecard["total_value_index"]).mean()), 2)}
])

generation_summary.to_csv(summary_path, index=False)

print(f"Wrote {scorecard_path} with {len(promo_scorecard)} promotion rows")
print(f"Wrote {summary_path}")
print(
    promo_scorecard[
        [
            "season",
            "game_date",
            "promo_name",
            "promo_category",
            "tickets_sold",
            "scanned_attendance",
            "total_revenue_indicator",
            "total_value_index",
            "recommendation"
        ]
    ].head(10).to_string(index=False)
)