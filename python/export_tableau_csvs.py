import csv
import getpass
import subprocess
from pathlib import Path

MYSQL_BIN = "/usr/local/mysql/bin/mysql"
DATABASE = "trash_pandas_crm"
OUTPUT_DIR = Path("outputs/tableau")

EXPORTS = {
    "tableau_fan_scoring_export": "fan_scoring_export.csv",
    "tableau_game_performance_export": "game_performance_export.csv",
    "tableau_group_sales_opportunities_export": "group_sales_opportunities_export.csv",
    "tableau_promo_performance_export": "promo_performance_export.csv",
    "tableau_season_summary_export": "season_summary_export.csv",
    "tableau_crm_action_summary_export": "crm_action_summary_export.csv",
}

def run_mysql_query(view_name, password):
    query = f"USE {DATABASE}; SELECT * FROM {view_name};"

    result = subprocess.run(
        [
            MYSQL_BIN,
            "-u",
            "root",
            f"--password={password}",
            "--batch",
            "--raw",
            "--execute",
            query,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout

def write_csv_from_mysql_output(mysql_output, output_path):
    lines = mysql_output.splitlines()

    if not lines:
        raise ValueError(f"No output returned for {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for line in lines:
            values = [
                "" if value == "NULL" else value
                for value in line.split("\t")
            ]
            writer.writerow(values)

def main():
    password = getpass.getpass("MySQL root password: ")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for view_name, file_name in EXPORTS.items():
        output_path = OUTPUT_DIR / file_name
        print(f"Exporting {view_name} -> {output_path}")
        mysql_output = run_mysql_query(view_name, password)
        write_csv_from_mysql_output(mysql_output, output_path)

    print("\nDONE")
    print("=" * 60)

    for _, file_name in EXPORTS.items():
        path = OUTPUT_DIR / file_name
        print(f"{path}: {path.stat().st_size:,} bytes")

if __name__ == "__main__":
    main()
