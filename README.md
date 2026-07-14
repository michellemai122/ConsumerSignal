# ConsumerSignal

**Which consumer startups are gaining momentum right now?**

ConsumerSignal tracks 25 early-stage consumer/AI startups and ranks them by a
**Momentum Score (0–100)** computed from live search and news signals. It's a
small end-to-end data product: a Python pipeline pulls external signals into
SQLite, a scoring layer normalizes them into comparable scores, and a Flask API
serves a single-page dashboard.

> 📄 **Read the case study:** [`CASE_STUDY.md`](CASE_STUDY.md)

---

## Live demo

`<add your deployed URL here after following "Deploy" below>`

## Run locally

```bash
pip install -r requirements.txt
python3 run.py           # picks a free port and opens the dashboard
```

`run.py` exists because macOS grabs port 5000 for AirPlay and because opening
`index.html` directly (`file://`) has no server to talk to — it avoids both traps.

## Deploy (free, ~5 min on Render)

1. Push this folder to a new GitHub repo.
2. On [render.com](https://render.com) → **New → Web Service** → connect the repo.
   Render reads `render.yaml` and deploys automatically. (Or set the start
   command manually: `gunicorn app.api:app`.)
3. Paste the resulting URL into the "Live demo" line above.

The demo dataset (`startup_intelligence.db`) is committed and served read-only,
so no external database is required.

## Architecture

```
data/startups.csv
   → scripts/*.py        (fetch search + news signals)
   → SQLite              (startup_intelligence.db)
   → app/scoring.py      (normalize → Momentum Score)
   → app/api.py (Flask)  (/api/startups, /api/startup/<name>, /api/category/<cat>)
   → index.html          (dashboard UI)
```

## Refresh the data

```bash
python3 scripts/fetch_news.py      # live Google News signals
python3 scripts/fetch_trends.py    # Google Trends (falls back to News RSS on rate limit)
python3 scripts/compute_scores.py  # recompute normalized scores
```

Requires `pandas`, `requests`, `pytrends` (data pipeline only — not needed to run the site).

## Scoring

Momentum is a weighted blend of four normalized (0–100) components:

| Component  | Weight | Signal |
|------------|:------:|--------|
| Growth     | 30%    | 30-day search/news velocity |
| Awareness  | 25%    | Search interest volume |
| Engagement | 25%    | Social engagement *(placeholder — see case study)* |
| Media      | 20%    | Recent news article volume |

See [`CASE_STUDY.md`](CASE_STUDY.md) for methodology, limitations, and roadmap.
