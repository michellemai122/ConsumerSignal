# Metric Dictionary

## Google Trends Metrics

| field_name         | definition                                              | example |
|-------------------|----------------------------------------------------------|---------|
| startup_name      | Name of startup being tracked                            | Phia    |
| date              | Date of observation                                      | 2026-03-01 |
| search_interest   | Google Trends interest score on a 0-100 scale            | 72      |
| search_growth_30d | Percent change in search interest over 30 days           | 80.0    |

## Reddit Metrics

| field_name          | definition                                              | example |
|--------------------|----------------------------------------------------------|---------|
| startup_name       | Name of startup being tracked                            | Phia    |
| date               | Date of observation                                      | 2026-03-01 |
| number_of_mentions | Number of Reddit posts/comments mentioning startup       | 48      |
| avg_upvotes        | Average upvotes across matched posts                     | 125.4   |
| avg_comments       | Average comments across matched posts                    | 19.7    |
| mention_growth     | Percent change in mention count over prior period        | 55.0    |

## News Metrics

| field_name      | definition                                               | example |
|----------------|-----------------------------------------------------------|---------|
| startup_name   | Name of startup being tracked                             | Phia    |
| date           | Date of observation                                       | 2026-03-01 |
| article_count  | Number of news articles matching startup in period        | 12      |
| article_growth | Percent change in article count over prior period         | 33.3    |

## Derived Metrics

| field_name       | definition                                                     | example |
|-----------------|-----------------------------------------------------------------|---------|
| momentum_score  | Weighted score combining search, Reddit, and news growth        | 81.2    |
| category        | Startup category                                                | AI Productivity |
| confidence_flag | Data quality flag based on source coverage                      | High    |