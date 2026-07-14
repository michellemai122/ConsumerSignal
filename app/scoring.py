import pandas as pd


def minmax_scale(series):
    """
    Scale a numeric pandas Series to 0-100.
    If all values are the same, return 50 for everything.
    """
    series = series.fillna(0)

    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return pd.Series([50.0] * len(series), index=series.index)

    return ((series - min_val) / (max_val - min_val) * 100).round(2)


def compute_confidence_flag(row):
    """
    Confidence is based on how many source tables have usable signal values.
    """
    sources_present = 0

    if row.get("search_interest", 0) > 0 or row.get("search_growth_30d", 0) != 0:
        sources_present += 1

    if row.get("article_count", 0) > 0:
        sources_present += 1

    if row.get("mentions", 0) > 0 or row.get("avg_upvotes", 0) > 0 or row.get("avg_comments", 0) > 0:
        sources_present += 1

    if sources_present == 3:
        return "High"
    elif sources_present == 2:
        return "Medium"
    else:
        return "Low"


def compute_scores(df):
    """
    Takes merged startup-level signal data and returns a scored dataframe.
    Expected columns:
    - startup_id
    - startup_name
    - category
    - search_interest
    - search_growth_30d
    - article_count
    - mentions
    - avg_upvotes
    - avg_comments
    """
    df = df.copy()

    # Fill missing values so scoring doesn't break
    for col in [
        "search_interest",
        "search_growth_30d",
        "article_count",
        "mentions",
        "avg_upvotes",
        "avg_comments"
    ]:
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)

    # Derived raw engagement value
    df["raw_engagement"] = (
        df["mentions"] +
        df["avg_upvotes"] +
        df["avg_comments"]
    )

    # Score components
    df["awareness_score"] = minmax_scale(df["search_interest"])
    df["growth_score"] = minmax_scale(df["search_growth_30d"])
    df["engagement_score"] = minmax_scale(df["raw_engagement"])
    df["media_score"] = minmax_scale(df["article_count"])

    # Final weighted score
    df["momentum_score"] = (
        0.30 * df["growth_score"] +
        0.25 * df["awareness_score"] +
        0.25 * df["engagement_score"] +
        0.20 * df["media_score"]
    ).round(2)

    # Confidence
    df["confidence_flag"] = df.apply(compute_confidence_flag, axis=1)

    return df