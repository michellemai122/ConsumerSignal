import sys
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import time
import requests
import xml.etree.ElementTree as ET

from pytrends.request import TrendReq

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db import run_query


pytrends = TrendReq(hl="en-US", tz=360)


def get_startups():
    return run_query("""
        SELECT startup_id, startup_name
        FROM startups
        ORDER BY startup_id
    """)


def compute_growth_from_series(values):
    """
    Percent growth from first to last value.
    """
    if len(values) < 2:
        return 0.0

    first_value = values.iloc[0]
    last_value = values.iloc[-1]

    if first_value == 0:
        if last_value == 0:
            return 0.0
        return 100.0

    return round(((last_value - first_value) / first_value) * 100, 2)


def compute_growth(current_count, previous_count):
    """
    Percent growth between two counts.
    """
    if previous_count == 0:
        if current_count == 0:
            return 0.0
        return 100.0

    return round(((current_count - previous_count) / previous_count) * 100, 2)


def count_google_news_rss_items(query):
    """
    Fallback awareness proxy using Google News RSS.
    """
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = root.findall(".//item")
    return len(items)


def fetch_pytrends_data(startup_name):
    """
    Primary method: try Google Trends via pytrends.
    """
    pytrends.build_payload([startup_name], timeframe="today 3-m")
    df = pytrends.interest_over_time()

    if df.empty or startup_name not in df.columns:
        return None

    values = df[startup_name]
    search_interest = round(float(values.mean()), 2)
    search_growth_30d = compute_growth_from_series(values)

    return search_interest, search_growth_30d


def fetch_fallback_proxy(startup_name):
    """
    Fallback method if Google Trends rate-limits:
    use Google News RSS volume as awareness proxy.
    """
    today = datetime.today().date()
    seven_days_ago = today - timedelta(days=7)
    fourteen_days_ago = today - timedelta(days=14)

    current_query = f'"{startup_name}" after:{seven_days_ago}'
    previous_query = f'"{startup_name}" after:{fourteen_days_ago} before:{seven_days_ago}'

    current_count = count_google_news_rss_items(current_query)
    previous_count = count_google_news_rss_items(previous_query)

    search_interest = float(current_count)
    search_growth_30d = compute_growth(current_count, previous_count)

    return search_interest, search_growth_30d


def fetch_trend_data_for_startup(startup_id, startup_name):
    try:
        print(f"Trying pytrends for {startup_name}...")
        search_interest, search_growth_30d = fetch_pytrends_data(startup_name)

        return {
            "startup_id": startup_id,
            "signal_date": datetime.today().strftime("%Y-%m-%d"),
            "search_interest": search_interest,
            "search_growth_30d": search_growth_30d
        }

    except Exception as e:
        print(f"Pytrends failed for {startup_name}: {e}")
        print(f"Falling back to Google News RSS proxy for {startup_name}...")

        try:
            search_interest, search_growth_30d = fetch_fallback_proxy(startup_name)

            return {
                "startup_id": startup_id,
                "signal_date": datetime.today().strftime("%Y-%m-%d"),
                "search_interest": search_interest,
                "search_growth_30d": search_growth_30d
            }

        except Exception as fallback_error:
            print(f"Fallback also failed for {startup_name}: {fallback_error}")
            return None


def save_trend_rows(rows):
    run_query("DELETE FROM trend_signals", fetch=False)

    for row in rows:
        run_query(
            """
            INSERT INTO trend_signals (
                startup_id,
                signal_date,
                search_interest,
                search_growth_30d
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                row["startup_id"],
                row["signal_date"],
                row["search_interest"],
                row["search_growth_30d"]
            ),
            fetch=False
        )


def main():
    startups = get_startups()
    trend_rows = []

    for startup in startups:
        startup_id = startup["startup_id"]
        startup_name = startup["startup_name"]

        result = fetch_trend_data_for_startup(startup_id, startup_name)

        if result:
            trend_rows.append(result)

        time.sleep(2)

    if trend_rows:
        save_trend_rows(trend_rows)
        print(f"Inserted {len(trend_rows)} rows into trend_signals.")
    else:
        print("No trend rows were inserted.")


if __name__ == "__main__":
    main()