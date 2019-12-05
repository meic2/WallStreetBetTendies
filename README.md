# WallStreetBetTendies
Uses Reddit posts and comments from different subreddits to determine relationships between stock sentiment and stock price movement

Architecture:
Scheduled job that runs every day at 12:00 AM that retrieves daily posts and comments from stock and investing-based subreddits, performs various NLP analysis tasks on it (e.g. cleaning and preprocessing, named entity recognition, feature and keyword extraction, sentiment computation, etc.), and uploads it to the database in the background

Dashboard that performs SQL queries in order to display insights:
Parameters that user can specify: stock symbol, time range, subreddit
1. Num of positive sentiment posts/comments vs. num of negative sentiment posts/comments vs. stock price movement (how does stock perform in following days/months after positive or negative comments, does prior drastic stock price chance affect subreddit's sentiment of stock)
2. Most common keywords associated with stock during different volatility periods (most common keyword when stock was dropping rapidly)

## Setup:
1. Sign in to VM (upload SSH public key to VM of local device if necessary).
2. Install Postgres SQL on VM, start service, and add user with password.\
https://docs.microsoft.com/en-us/azure/virtual-machines/linux/postgresql-install\
https://www.a2hosting.com/kb/developer-corner/testing-and-development/creating-a-postgresql-installation-for-local-testing
3. Run below command to view Postgres data and config directory:\
```sudo -u postgres psql -c "SHOW data_directory";```
4. Uncomment listen_address and port line in postgresql.conf. Update localhost to '*' and add 'host 0.0.0.0/0' to accept non-local connections.
5. Restart Postgres service and add database settings in Django project under settings.py. 

## Start Project on Server:
```python3 manage.py runserver <server_ip_addr>:8000```

## Open Jupyter notebook on remote server via local browser:
1. Run ```ssh -L 8000:localhost:8888 user@ip_addr``` to connect to remote server.
2. Then start jupyter notebook and navigate to locahost:8000. 

## Endpoints:
1. Stock Tick Data endpoint: <br>
```http://172.22.158.49:8000/tick_data?stock_symbol=AAPL&start_date=2018-12-01&end_date=2019-12-01``` <br>
Example Output: <br>
{
    "MSFT": [
        {
            "date": "2018-12-03T00:00:00",
            "close_price": 112.09
        },
        {
            "date": "2018-12-04T00:00:00",
            "close_price": 108.52
        }
    ]
}

2. Moving Volatility endpoint: <br>
```http://172.22.158.49:8000/moving_volatility?stock_symbol=AAPL&start_date=2018-10-01&end_date=2019-01-01``` <br>
Example Output: <br>
{
    "status": 200,
    "res": [
        {
            "stock_symbol": "AAPL",
            "ts": "2018-05-25 00:00:00",
            "moving_10_volatility": 0.00269582245382441,
            "moving_30_volatility": 0.00704960800986764
        },
        {
            "stock_symbol": "AAPL",
            "ts": "2018-05-29 00:00:00",
            "moving_10_volatility": 0.00254678002178621,
            "moving_30_volatility": 0.00706563446594377
        },
        {
            "stock_symbol": "AAPL",
            "ts": "2018-05-30 00:00:00",
            "moving_10_volatility": 0.00254388242147337,
            "moving_30_volatility": 0.00706686429586809
        },
        {
            "stock_symbol": "AAPL",
            "ts": "2018-05-31 00:00:00",
            "moving_10_volatility": 0.0022636742034069,
            "moving_30_volatility": 0.00701587375850883
        }
    ]
}

3. Subreddit Sentiment Disagreement endpoint: <br>
```http://172.22.158.49:8000/subreddit_sentiment_disagreement?&subreddit_name=stocks&subreddit_name_2=investing&start_date=2018-12-01&end_date=2019-12-01``` <br>
Example Output: <br>
{
    "status": 200,
    "res": [
        {
            "p_month": "Dec",
            "p_sentiment": 0.0305337420910414,
            "c_sentiment": 0.0467179359582487,
            "other_p_sentiment": -0.00413696654991213,
            "other_c_sentiment": 0.0682914612315927
        },
        {
            "p_month": "Aug",
            "p_sentiment": 0.128351886190842,
            "c_sentiment": 0.0964967767254736,
            "other_p_sentiment": -0.0301804664066544,
            "other_c_sentiment": 0.0778370680971779
        }
    ]
}

4. Sentiment Popularity Correlation endpoint: <br>
```http://172.22.158.49:8000/sentiment_popularity_correlation?&subreddit_name=investing``` <br>
Example Output: <br>


5. Company Sentiment Count endpoint: <br>
```http://172.22.158.49:8000/sentiment_count?&company=tesla&subreddit_name=stocks``` <br>
Example Output: <br>
{
    "status": 200,
    "res": {
        "positive_post": 45,
        "negative_post": 17,
        "average_upvote": 149.94155844155844
    }
}

6. Most Common Keywords Associated with Company: <br>
```http://172.22.158.49:8000/company_keywords?&company=wework&subreddit_name=stocks```
Example Output: <br>
{
    "status": 200,
    "res": [
        {
            "stock": 192
        },
        {
            "tesla": 147
        },
        {
            "global": 78
        },
        {
            "price": 76
        },
        {
            "ideas": 73
        },
        {
            "share": 64
        }
    ]
}
