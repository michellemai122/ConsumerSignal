DATA_SOURCES = {
    "google_trends": {
        "signal": "search interest and 30-day search growth",
        "access_method": "pytrends",
        "pull_frequency": "weekly"
    },
    "reddit": {
        "signal": "mentions, upvotes, comments, discussion growth",
        "access_method": "praw",
        "pull_frequency": "weekly"
    },
    "news": {
        "signal": "article count and article growth",
        "access_method": "news api or gdelt",
        "pull_frequency": "weekly"
    }
}