import csv
import sys
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db import run_query

CSV_PATH = BASE_DIR / "data" / "startups.csv"


def load_startups():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Could not find startups file: {CSV_PATH}")

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            startup_name = row["startup_name"].strip()
            category = row["category"].strip()
            description = row["description"].strip()

            run_query(
                """
                INSERT OR IGNORE INTO startups (startup_name, category, description)
                VALUES (?, ?, ?)
                """,
                (startup_name, category, description),
                fetch=False
            )

    print("Startups loaded successfully.")


if __name__ == "__main__":
    load_startups()