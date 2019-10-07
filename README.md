# WallStreetBetTendies
Uses Reddit posts and comments from different subreddits to determine relationships between stock sentiment and stock price movement

Architecture:
Scheduled job that runs every day at 12:00 AM that retrieves daily posts and comments from stock and investing-based subreddits, performs various NLP analysis tasks on it (e.g. cleaning and preprocessing, named entity recognition, feature and keyword extraction, sentiment computation, etc.), and uploads it to the database in the background

Dashboard that performs SQL queries in order to display insights:
Parameters that user can specify: stock symbol, time range, subreddit
1. Num of positive sentiment posts/comments vs. num of negative sentiment posts/comments vs. stock price movement (how does stock perform in following days/months after positive or negative comments, does prior drastic stock price chance affect subreddit's sentiment of stock)
2. Most common keywords associated with stock during different volatility periods (most common keyword when stock was dropping rapidly)
