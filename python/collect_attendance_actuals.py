import re
import csv
import html
import urllib.request
from pathlib import Path

BASE_URL = "https://www.thebaseballcube.com/content/minor_game_log/{season}~14089/"

OUTPUT_FULL = Path("data/raw/attendance_game_logs_2023_2025.csv")
OUTPUT_TOYOTA = Path("data/raw/attendance_2023_2025.csv")

SEASONS = [2023, 2024, 2025]

MONTHS = {
    "April", "May", "June", "July", "August", "September"
}

SOURCE_NAME = "the_baseball_cube_minor_game_log"

def fetch_page(season: int) -> str:
    url = BASE_URL.format(season=season)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_rows(season: int, page_html: str):
    """
    Parses visible game-log rows from The Baseball Cube page.

    Expected visible row shape after tag cleanup:
    2025-04-04 April Chattanooga Lookouts Home L 1-9 boxscore 6,597 2:51 0-1 Toyota Field Madison,Alabama
    """

    clean = strip_tags(page_html)

    # Split before each game date.
    chunks = re.split(r"(?=\b20\d{2}-\d{2}-\d{2}\b)", clean)

    rows = []

    for chunk in chunks:
        date_match = re.match(r"(20\d{2}-\d{2}-\d{2})\s+", chunk)
        if not date_match:
            continue

        game_date = date_match.group(1)

        # Keep each chunk short enough to avoid bleeding into the next row.
        next_date = re.search(r"\s20\d{2}-\d{2}-\d{2}\s", chunk[10:])
        if next_date:
            chunk = chunk[:10 + next_date.start()]

        pattern = re.compile(
            r"^(?P<game_date>20\d{2}-\d{2}-\d{2})\s+"
            r"(?P<month>April|May|June|July|August|September)\s+"
            r"(?P<opponent>.+?)\s+"
            r"(?P<v_h>Home|Vis)\s+"
            r"(?P<result>W|L)\s+"
            r"(?P<score>\d+-\d+)\s+"
            r"boxscore\s+"
            r"(?P<attendance>[0-9,]+)\s+"
            r"(?P<time_of_game>\d+:\d+)\s+"
            r"(?P<record>\d+-\d+)\s+"
            r"(?P<ballpark>.+?)\s+"
            r"(?P<location>[A-Za-z .'-]+,[A-Za-z .'-]+)"
        )

        match = pattern.search(chunk)

        if not match:
            continue

        row = match.groupdict()

        attendance = int(row["attendance"].replace(",", ""))

        rows.append({
            "game_date": row["game_date"],
            "season": season,
            "month_name": row["month"],
            "opponent": row["opponent"].strip(),
            "tbc_home_away": "Home" if row["v_h"] == "Home" else "Away",
            "result": row["result"],
            "score": row["score"],
            "attendance": attendance,
            "time_of_game": row["time_of_game"],
            "team_record_after_game": row["record"],
            "ballpark": row["ballpark"].strip(),
            "location": row["location"].strip(),
            "is_toyota_field_game": 1 if row["ballpark"].strip() == "Toyota Field" and row["location"].strip() == "Madison,Alabama" else 0,
            "source_name": SOURCE_NAME
        })

    return rows


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "game_date",
        "season",
        "month_name",
        "opponent",
        "tbc_home_away",
        "result",
        "score",
        "attendance",
        "time_of_game",
        "team_record_after_game",
        "ballpark",
        "location",
        "is_toyota_field_game",
        "source_name"
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    all_rows = []

    for season in SEASONS:
        print(f"Fetching {season} attendance game log...")
        page = fetch_page(season)
        rows = parse_rows(season, page)

        print(f"{season}: parsed {len(rows)} game-log rows")
        all_rows.extend(rows)

toyota_rows = [
    row for row in all_rows
    if row["tbc_home_away"] == "Home"
]

for row in toyota_rows:
    row["is_toyota_field_game"] = 1

    write_csv(OUTPUT_FULL, all_rows)
    write_csv(OUTPUT_TOYOTA, toyota_rows)

    print("\nWROTE FILES")
    print("=" * 60)
    print(f"{OUTPUT_FULL}: {len(all_rows)} rows")
    print(f"{OUTPUT_TOYOTA}: {len(toyota_rows)} Toyota Field rows")

    print("\nTOYOTA FIELD ATTENDANCE BY SEASON")
    print("=" * 60)

    for season in SEASONS:
        season_rows = [row for row in toyota_rows if row["season"] == season]
        total_attendance = sum(row["attendance"] for row in season_rows)
        paid_dates = len({row["game_date"] for row in season_rows})
        print(f"{season}: rows={len(season_rows)}, dates={paid_dates}, attendance={total_attendance:,}")


if __name__ == "__main__":
    main()
