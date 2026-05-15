import csv
from pathlib import Path

raw_games_path = Path("data/public/games.csv")
raw_promotions_path = Path("data/public/promotions.csv")
raw_attendance_path = Path("data/public/attendance.csv")

processed_dir = Path("data/processed")
processed_dir.mkdir(parents=True, exist_ok=True)

games_output_path = processed_dir / "games_clean.csv"
promotions_output_path = processed_dir / "promotions_clean.csv"
attendance_output_path = processed_dir / "attendance_clean.csv"
summary_output_path = processed_dir / "public_cleaning_summary.csv"

def read_csv(path):
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def clean_bool(value):
    return str(value).strip().lower() == "true"

def clean_int(value):
    if value is None or str(value).strip() == "":
        return ""
    return int(float(str(value).strip()))

def clean_money_or_number(value):
    if value is None or str(value).strip() == "":
        return ""
    return float(str(value).strip())

games = read_csv(raw_games_path)
promotions = read_csv(raw_promotions_path)
attendance = read_csv(raw_attendance_path)

clean_games = []

for row in games:
    clean_games.append({
        "game_id": row["game_id"].strip(),
        "season": clean_int(row["season"]),
        "game_date": row["game_date"].strip(),
        "home_away": row["home_away"].strip(),
        "opponent": row["opponent"].strip(),
        "day_of_week": row["day_of_week"].strip(),
        "start_time": row["start_time"].strip(),
        "homestand_id": row["homestand_id"].strip(),
        "series_id": row["series_id"].strip(),
        "game_number_in_homestand": clean_int(row["game_number_in_homestand"]),
        "month": clean_int(row["month"]),
        "weekend_flag": clean_bool(row["weekend_flag"]),
        "holiday_flag": clean_bool(row["holiday_flag"]),
        "source_id": row["source_id"].strip(),
        "public_data_flag": clean_bool(row["public_data_flag"]),
        "notes": row["notes"].strip()
    })

clean_promotions = []

for row in promotions:
    clean_promotions.append({
        "promo_id": row["promo_id"].strip(),
        "game_id": row["game_id"].strip(),
        "season": clean_int(row["season"]),
        "game_date": row["game_date"].strip(),
        "promo_name": row["promo_name"].strip(),
        "promo_category": row["promo_category"].strip(),
        "promo_type": row["promo_type"].strip(),
        "primary_promo_flag": clean_bool(row["primary_promo_flag"]),
        "sponsor_attached_flag": clean_bool(row["sponsor_attached_flag"]),
        "giveaway_flag": clean_bool(row["giveaway_flag"]),
        "fireworks_flag": clean_bool(row["fireworks_flag"]),
        "theme_night_flag": clean_bool(row["theme_night_flag"]),
        "family_flag": clean_bool(row["family_flag"]),
        "dog_day_flag": clean_bool(row["dog_day_flag"]),
        "jersey_auction_flag": clean_bool(row["jersey_auction_flag"]),
        "expected_fan_segment": row["expected_fan_segment"].strip(),
        "source_id": row["source_id"].strip(),
        "public_data_flag": clean_bool(row["public_data_flag"]),
        "notes": row["notes"].strip()
    })

clean_attendance = []

for row in attendance:
    announced_attendance = row["announced_attendance"].strip()
    actual_home_game_records = row["actual_home_game_records"].strip()

    clean_attendance.append({
        "attendance_id": row["attendance_id"].strip(),
        "game_id": row["game_id"].strip(),
        "season": clean_int(row["season"]),
        "game_date": row["game_date"].strip(),
        "opponent": row["opponent"].strip(),
        "announced_attendance": "" if announced_attendance == "" else clean_int(announced_attendance),
        "attendance_source": row["attendance_source"].strip(),
        "attendance_match_status": row["attendance_match_status"].strip(),
        "actual_home_game_records": "" if actual_home_game_records == "" else clean_int(actual_home_game_records),
        "attendance_note": row["attendance_note"].strip(),
        "public_data_flag": clean_bool(row["public_data_flag"])
    })

game_fields = [
    "game_id",
    "season",
    "game_date",
    "home_away",
    "opponent",
    "day_of_week",
    "start_time",
    "homestand_id",
    "series_id",
    "game_number_in_homestand",
    "month",
    "weekend_flag",
    "holiday_flag",
    "source_id",
    "public_data_flag",
    "notes"
]

promotion_fields = [
    "promo_id",
    "game_id",
    "season",
    "game_date",
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
    "source_id",
    "public_data_flag",
    "notes"
]

attendance_fields = [
    "attendance_id",
    "game_id",
    "season",
    "game_date",
    "opponent",
    "announced_attendance",
    "attendance_source",
    "attendance_match_status",
    "actual_home_game_records",
    "attendance_note",
    "public_data_flag"
]

write_csv(games_output_path, clean_games, game_fields)
write_csv(promotions_output_path, clean_promotions, promotion_fields)
write_csv(attendance_output_path, clean_attendance, attendance_fields)

matched_attendance_rows = [
    row for row in clean_attendance
    if row["attendance_match_status"] == "matched"
]

unmatched_attendance_rows = [
    row for row in clean_attendance
    if row["attendance_match_status"] == "unmatched"
]

summary_rows = [
    {
        "file_name": "games_clean.csv",
        "row_count": len(clean_games),
        "notes": "Cleaned public game schedule foundation"
    },
    {
        "file_name": "promotions_clean.csv",
        "row_count": len(clean_promotions),
        "notes": "Cleaned public promotion foundation"
    },
    {
        "file_name": "attendance_clean.csv",
        "row_count": len(clean_attendance),
        "notes": f"Cleaned public announced attendance foundation; matched={len(matched_attendance_rows)} unmatched={len(unmatched_attendance_rows)}"
    }
]

write_csv(summary_output_path, summary_rows, ["file_name", "row_count", "notes"])

print(f"Wrote {games_output_path}")
print(f"Wrote {promotions_output_path}")
print(f"Wrote {attendance_output_path}")
print(f"Wrote {summary_output_path}")