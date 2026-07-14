DROP TABLE IF EXISTS startup_scores;
DROP TABLE IF EXISTS reddit_signals;
DROP TABLE IF EXISTS news_signals;
DROP TABLE IF EXISTS trend_signals;
DROP TABLE IF EXISTS startups;

CREATE TABLE startups (
    startup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    startup_name TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    description TEXT
);

CREATE TABLE trend_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    startup_id INTEGER NOT NULL,
    signal_date TEXT NOT NULL,
    search_interest REAL,
    search_growth_30d REAL,
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id)
);

CREATE TABLE reddit_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    startup_id INTEGER NOT NULL,
    signal_date TEXT NOT NULL,
    mentions INTEGER,
    avg_upvotes REAL,
    avg_comments REAL,
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id)
);

CREATE TABLE news_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    startup_id INTEGER NOT NULL,
    signal_date TEXT NOT NULL,
    article_count INTEGER,
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id)
);

CREATE TABLE startup_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    startup_id INTEGER NOT NULL,
    score_date TEXT NOT NULL,
    awareness_score REAL,
    growth_score REAL,
    engagement_score REAL,
    media_score REAL,
    momentum_score REAL,
    confidence_flag TEXT,
    FOREIGN KEY (startup_id) REFERENCES startups(startup_id)
);