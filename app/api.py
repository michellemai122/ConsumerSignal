import json
from pathlib import Path
import sqlite3

from flask import Flask, jsonify, send_from_directory

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "startup_intelligence.db"

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


@app.after_request
def add_cors_headers(response):
    # Allow the dashboard to work even when index.html is opened directly
    # from disk (file://) rather than served through Flask.
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def serve_home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/startups")
def get_startups():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            s.startup_id,
            s.startup_name,
            s.category,
            s.description,
            ls.score_date,
            ls.awareness_score,
            ls.growth_score,
            ls.engagement_score,
            ls.media_score,
            ls.momentum_score,
            ls.confidence_flag
        FROM startups s
        LEFT JOIN (
            SELECT ss1.*
            FROM startup_scores ss1
            INNER JOIN (
                SELECT startup_id, MAX(score_date) AS max_score_date
                FROM startup_scores
                GROUP BY startup_id
            ) ss2
            ON ss1.startup_id = ss2.startup_id
            AND ss1.score_date = ss2.max_score_date
        ) ls
        ON s.startup_id = ls.startup_id
        ORDER BY
            CASE WHEN ls.momentum_score IS NULL THEN 1 ELSE 0 END,
            ls.momentum_score DESC,
            s.startup_name ASC
    """).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/startup/<startup_name>")
def get_startup_detail(startup_name):
    conn = get_connection()

    startup = conn.execute("""
        SELECT
            s.startup_id,
            s.startup_name,
            s.category,
            s.description
        FROM startups s
        WHERE lower(s.startup_name) = lower(?)
    """, (startup_name,)).fetchone()

    if not startup:
        conn.close()
        return jsonify({"error": "Startup not found"}), 404

    startup_id = startup["startup_id"]

    trend = conn.execute("""
        SELECT signal_date, search_interest, search_growth_30d
        FROM trend_signals
        WHERE startup_id = ?
        ORDER BY signal_date DESC
        LIMIT 1
    """, (startup_id,)).fetchone()

    news = conn.execute("""
        SELECT signal_date, article_count
        FROM news_signals
        WHERE startup_id = ?
        ORDER BY signal_date DESC
        LIMIT 1
    """, (startup_id,)).fetchone()

    reddit = conn.execute("""
        SELECT signal_date, mentions, avg_upvotes, avg_comments
        FROM reddit_signals
        WHERE startup_id = ?
        ORDER BY signal_date DESC
        LIMIT 1
    """, (startup_id,)).fetchone()

    score = conn.execute("""
        SELECT
            score_date,
            awareness_score,
            growth_score,
            engagement_score,
            media_score,
            momentum_score,
            confidence_flag
        FROM startup_scores
        WHERE startup_id = ?
        ORDER BY score_date DESC
        LIMIT 1
    """, (startup_id,)).fetchone()

    peers = conn.execute("""
        SELECT
            s.startup_name,
            s.category,
            sc.momentum_score
        FROM startups s
        LEFT JOIN (
            SELECT ss1.*
            FROM startup_scores ss1
            INNER JOIN (
                SELECT startup_id, MAX(score_date) AS max_score_date
                FROM startup_scores
                GROUP BY startup_id
            ) ss2
            ON ss1.startup_id = ss2.startup_id
            AND ss1.score_date = ss2.max_score_date
        ) sc
        ON s.startup_id = sc.startup_id
        WHERE lower(s.category) = lower(?)
        ORDER BY
            CASE WHEN sc.momentum_score IS NULL THEN 1 ELSE 0 END,
            sc.momentum_score DESC,
            s.startup_name ASC
    """, (startup["category"],)).fetchall()

    conn.close()

    return jsonify({
        "startup": dict(startup),
        "trend_signals": dict(trend) if trend else None,
        "news_signals": dict(news) if news else None,
        "reddit_signals": dict(reddit) if reddit else None,
        "scorecard": dict(score) if score else None,
        "peers": [dict(row) for row in peers]
    })


@app.route("/api/category/<category>")
def get_category_comparison(category):
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            s.startup_name,
            s.category,
            s.description,
            ls.score_date,
            ls.awareness_score,
            ls.growth_score,
            ls.engagement_score,
            ls.media_score,
            ls.momentum_score,
            ls.confidence_flag
        FROM startups s
        LEFT JOIN (
            SELECT ss1.*
            FROM startup_scores ss1
            INNER JOIN (
                SELECT startup_id, MAX(score_date) AS max_score_date
                FROM startup_scores
                GROUP BY startup_id
            ) ss2
            ON ss1.startup_id = ss2.startup_id
            AND ss1.score_date = ss2.max_score_date
        ) ls
        ON s.startup_id = ls.startup_id
        WHERE lower(s.category) = lower(?)
        ORDER BY
            CASE WHEN ls.momentum_score IS NULL THEN 1 ELSE 0 END,
            ls.momentum_score DESC,
            s.startup_name ASC
    """, (category,)).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/meta")
def get_meta():
    """When the data was last refreshed, for the dashboard header."""
    conn = get_connection()

    try:
        run = conn.execute("""
            SELECT run_at, status, sources
            FROM pipeline_runs
            WHERE status IN ('ok', 'partial')
            ORDER BY run_at DESC
            LIMIT 1
        """).fetchone()
    except sqlite3.OperationalError:
        # Older databases have no pipeline_runs table yet.
        run = None

    if run:
        result = {
            "last_updated": run["run_at"],
            "status": run["status"],
            "sources": json.loads(run["sources"]),
        }
    else:
        score_date = conn.execute(
            "SELECT MAX(score_date) AS d FROM startup_scores"
        ).fetchone()["d"]
        result = {"last_updated": score_date, "status": None, "sources": None}

    conn.close()
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)