# Data Sources

| source_name     | what_signal_it_gives                                    | how_we_access_it                         | pull_frequency |
|----------------|----------------------------------------------------------|------------------------------------------|----------------|
| Google Trends  | Search interest and search growth over time              | Python via pytrends                      | Weekly         |
| Reddit         | Startup mentions, discussion volume, engagement quality  | Reddit API via PRAW or search endpoints  | Weekly         |
| News / GDELT   | Media coverage and article growth                        | News API or GDELT API                    | Weekly         |

## Notes

### Google Trends
Used to measure how much search demand for a startup is increasing over time.

### Reddit
Used to measure how often a startup is being discussed and how much engagement those discussions receive.

### News / GDELT
Used to measure whether a startup is receiving growing press coverage and media attention.