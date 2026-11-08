import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db import run_query


def get_startups():
    return run_query("""
        SELECT startup_id, startup_name
        FROM startups
        ORDER BY startup_id
    """)


def fetch_recent_news_count(startup_name, days_back=7):
    query = f'"{startup_name}"'
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"

    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = root.findall(".//item")

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    recent_count = 0

    for item in items:
        pub_date_el = item.find("pubDate")

        if pub_date_el is None:
            continue

        try:
            pub_date = parsedate_to_datetime(pub_date_el.text)

            if pub_date >= cutoff:
                recent_count += 1

        except Exception:
            continue

    return recent_count


def save_news_rows(rows):
    # Replace only the startups we fetched this run. A startup whose fetch
    # failed keeps its previous row instead of dropping out of the scores.
    for row in rows:
        run_query(
            "DELETE FROM news_signals WHERE startup_id = ?",
            (row["startup_id"],),
            fetch=False
        )
        run_query(
            """
            INSERT INTO news_signals (startup_id, signal_date, article_count)
            VALUES (?, ?, ?)
            """,
            (
                row["startup_id"],
                row["signal_date"],
                row["article_count"]
            ),
            fetch=False
        )


def main():
    startups = get_startups()
    news_rows = []

    for startup in startups:

        startup_id = startup["startup_id"]
        startup_name = startup["startup_name"]

        try:

            print(f"Fetching 7-day news count for {startup_name}...")

            article_count = fetch_recent_news_count(startup_name)

            news_rows.append({
                "startup_id": startup_id,
                "signal_date": datetime.today().strftime("%Y-%m-%d"),
                "article_count": article_count
            })

        except Exception as e:

            print(f"News fetch error for {startup_name}: {e}")

    if news_rows:

        save_news_rows(news_rows)

        print(f"Inserted {len(news_rows)} rows into news_signals.")

    else:

        print("No news rows were inserted.")

    return len(news_rows), len(startups)


if __name__ == "__main__":
    main()