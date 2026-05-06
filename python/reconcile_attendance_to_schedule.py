import csv
from collections import Counter, defaultdict
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/processed/game_attendance_reconciled_2023_2025.csv")
YEARS = [2023, 2024, 2025]

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def clean_text(value):
    return " ".join((value or "").strip().lower().split())

schedule_rows = []
for year in YEARS:
    schedule_rows.extend(read_csv(RAW_DIR / f"schedule_{year}.csv"))

attendance_rows = read_csv(RAW_DIR / "attendance_2023_2025.csv")

home_schedule = [r for r in schedule_rows if r["home_away"] == "Home"]

for i, row in enumerate(attendance_rows, start=1):
    row["attendance_log_sequence"] = i

schedule_groups = defaultdict(list)
attendance_groups = defaultdict(list)

for row in home_schedule:
    key = (row["season"], clean_text(row["opponent"]))
    schedule_groups[key].append(row)

for row in attendance_rows:
    key = (row["season"], clean_text(row["opponent"]))
    attendance_groups[key].append(row)

print("\nCOUNT CHECK BY SEASON + OPPONENT")
print("=" * 60)

all_keys = sorted(set(schedule_groups.keys()) | set(attendance_groups.keys()))
count_issue = False

for key in all_keys:
    schedule_count = len(schedule_groups.get(key, []))
    attendance_count = len(attendance_groups.get(key, []))

    if schedule_count != attendance_count:
        count_issue = True
        print(f"Mismatch {key}: schedule={schedule_count}, attendance={attendance_count}")

if not count_issue:
    print("No count mismatches found.")

for key in schedule_groups:
    schedule_groups[key].sort(key=lambda r: (r["game_date"], r["game_id"]))

for key in attendance_groups:
    attendance_groups[key].sort(
        key=lambda r: (r["game_date"], int(r["attendance_log_sequence"]))
    )

attendance_date_counts = Counter(
    (r["season"], r["game_date"]) for r in attendance_rows
)

reconciled = []

for key in sorted(schedule_groups.keys()):
    schedule_list = schedule_groups[key]
    attendance_list = attendance_groups.get(key, [])

    if len(schedule_list) != len(attendance_list):
        raise ValueError(
            f"Cannot reconcile {key}: schedule={len(schedule_list)}, attendance={len(attendance_list)}"
        )

    for sched, att in zip(schedule_list, attendance_list):
        actual_date_key = (att["season"], att["game_date"])
        rows_on_actual_date = attendance_date_counts[actual_date_key]

        reconciled.append({
            "game_id": sched["game_id"],
            "season": sched["season"],
            "planned_game_date": sched["game_date"],
            "actual_game_date": att["game_date"],
            "opponent_code": sched["opponent_code"],
            "opponent": sched["opponent"],
            "planned_game_time": sched["game_time"],
            "planned_day_of_week": sched["day_of_week"],
            "planned_month_name": sched["month_name"],
            "result": att["result"],
            "score": att["score"],
            "attendance": att["attendance"],
            "time_of_game": att["time_of_game"],
            "team_record_after_game": att["team_record_after_game"],
            "ballpark": att["ballpark"],
            "location": att["location"],
            "is_doubleheader_date": 1 if rows_on_actual_date > 1 else 0,
            "attendance_rows_on_actual_date": rows_on_actual_date,
            "zero_attendance_flag": 1 if int(att["attendance"]) == 0 else 0,
            "date_match_flag": 1 if sched["game_date"] == att["game_date"] else 0,
            "match_method": "season_opponent_sequence",
            "attendance_source_name": att["source_name"]
        })

reconciled.sort(key=lambda r: (int(r["season"]), r["planned_game_date"], r["game_id"]))

fieldnames = [
    "game_id",
    "season",
    "planned_game_date",
    "actual_game_date",
    "opponent_code",
    "opponent",
    "planned_game_time",
    "planned_day_of_week",
    "planned_month_name",
    "result",
    "score",
    "attendance",
    "time_of_game",
    "team_record_after_game",
    "ballpark",
    "location",
    "is_doubleheader_date",
    "attendance_rows_on_actual_date",
    "zero_attendance_flag",
    "date_match_flag",
    "match_method",
    "attendance_source_name"
]

write_csv(OUT_PATH, reconciled, fieldnames)

print("\nRECONCILIATION OUTPUT")
print("=" * 60)
print(f"Wrote: {OUT_PATH}")
print(f"Rows: {len(reconciled)}")

print("\nCOUNTS BY SEASON")
print("=" * 60)

for season in ["2023", "2024", "2025"]:
    rows = [r for r in reconciled if r["season"] == season]
    total_attendance = sum(int(r["attendance"]) for r in rows)
    zero_games = sum(int(r["zero_attendance_flag"]) for r in rows)
    doubleheader_rows = sum(int(r["is_doubleheader_date"]) for r in rows)
    date_mismatches = sum(1 for r in rows if r["planned_game_date"] != r["actual_game_date"])

    print(
        f"{season}: rows={len(rows)}, "
        f"attendance={total_attendance:,}, "
        f"zero_attendance_games={zero_games}, "
        f"doubleheader_rows={doubleheader_rows}, "
        f"planned_vs_actual_date_mismatches={date_mismatches}"
    )

print("\nHIGH-LEVEL CHECKS")
print("=" * 60)
print("Expected rows: 207")
print("Expected 2023 attendance: 314,306")
print("Expected 2024 attendance: 308,267")
print("Expected 2025 attendance: 275,423")
