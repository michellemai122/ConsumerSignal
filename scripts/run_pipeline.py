"""
Refresh every signal source, then recompute momentum scores.

Each source runs on its own. If one source fails (for example Google Trends
returns 429 from a cloud IP), the other sources still run and the failed
source keeps its previous rows. Scores are recomputed when at least one
source returned fresh data.

Each run writes one row to `pipeline_runs`. The dashboard reads the latest
successful row to show "Last updated".

Exit code: 0 when scores were refreshed, 1 when no source returned data.

Usage:
    python scripts/run_pipeline.py
"""
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "scripts"))

from app.db import run_query  # noqa: E402

import compute_scores  # noqa: E402
import fetch_news  # noqa: E402
import fetch_trends  # noqa: E402

# Reddit is not wired up yet (scripts/fetch_reddit.py is empty), so it is not
# listed here. compute_scores treats missing Reddit data as zero.
SOURCES = {
    "google_trends": fetch_trends.main,
    "google_news": fetch_news.main,
}


def ensure_runs_table():
    run_query(
        """
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at TEXT NOT NULL,
            status TEXT NOT NULL,
            sources TEXT NOT NULL
        )
        """,
        fetch=False,
    )


def run_source(name, fn):
    print(f"\n=== {name} ===")
    try:
        fetched, total = fn()
        return {"status": "ok" if fetched else "failed", "rows": fetched, "of": total}
    except Exception as e:
        traceback.print_exc()
        return {"status": "failed", "rows": 0, "error": str(e)[:200]}


def main():
    ensure_runs_table()

    results = {name: run_source(name, fn) for name, fn in SOURCES.items()}
    any_fresh = any(r["rows"] > 0 for r in results.values())

    if any_fresh:
        print("\n=== scores ===")
        compute_scores.main()
        status = "ok" if all(r["status"] == "ok" for r in results.values()) else "partial"
    else:
        status = "failed"

    run_query(
        "INSERT INTO pipeline_runs (run_at, status, sources) VALUES (?, ?, ?)",
        (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            status,
            json.dumps(results),
        ),
        fetch=False,
    )

    print(f"\nPipeline finished: {status}")
    for name, r in results.items():
        print(f"  {name}: {r}")

    return 0 if any_fresh else 1


if __name__ == "__main__":
    sys.exit(main())
