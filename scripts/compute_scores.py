import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.db import get_connection, run_query
from app.scoring import compute_scores


def load_table(query):
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def main():
    startups_df = load_table("""
        SELECT startup_id, startup_name, category, description
        FROM startups
    """)

    trends_df = load_table("""
        SELECT startup_id, signal_date, search_interest, search_growth_30d
        FROM trend_signals
    """)

    news_df = load_table("""
        SELECT startup_id, signal_date, article_count
        FROM news_signals
    """)

    # Reddit may still be empty for now, so create a safe default if no rows
    reddit_df = load_table("""
        SELECT startup_id, signal_date, mentions, avg_upvotes, avg_comments
        FROM reddit_signals
    """)

    if reddit_df.empty:
        reddit_df = pd.DataFrame({
            "startup_id": startups_df["startup_id"],
            "mentions": 0,
            "avg_upvotes": 0,
            "avg_comments": 0
        })

    # Keep latest row per startup
    if not trends_df.empty:
        trends_df = (
            trends_df.sort_values("signal_date")
            .drop_duplicates(subset=["startup_id"], keep="last")
            [["startup_id", "search_interest", "search_growth_30d"]]
        )
    else:
        trends_df = pd.DataFrame({
            "startup_id": startups_df["startup_id"],
            "search_interest": 0,
            "search_growth_30d": 0
        })

    if not news_df.empty:
        news_df = (
            news_df.sort_values("signal_date")
            .drop_duplicates(subset=["startup_id"], keep="last")
            [["startup_id", "article_count"]]
        )
    else:
        news_df = pd.DataFrame({
            "startup_id": startups_df["startup_id"],
            "article_count": 0
        })

    if "signal_date" in reddit_df.columns:
        reddit_df = (
            reddit_df.sort_values("signal_date")
            .drop_duplicates(subset=["startup_id"], keep="last")
            [["startup_id", "mentions", "avg_upvotes", "avg_comments"]]
        )
    else:
        reddit_df = reddit_df[["startup_id", "mentions", "avg_upvotes", "avg_comments"]]

    # Merge all signals
    merged_df = startups_df.merge(trends_df, on="startup_id", how="left")
    merged_df = merged_df.merge(news_df, on="startup_id", how="left")
    merged_df = merged_df.merge(reddit_df, on="startup_id", how="left")

    scored_df = compute_scores(merged_df)
    scored_df["score_date"] = datetime.today().strftime("%Y-%m-%d")

    output_df = scored_df[[
        "startup_id",
        "score_date",
        "awareness_score",
        "growth_score",
        "engagement_score",
        "media_score",
        "momentum_score",
        "confidence_flag"
    ]]

    run_query("DELETE FROM startup_scores", fetch=False)

    conn = get_connection()
    output_df.to_sql("startup_scores", conn, if_exists="append", index=False)
    conn.close()

    print("Computed startup scores successfully.")
    print(output_df.sort_values("momentum_score", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()