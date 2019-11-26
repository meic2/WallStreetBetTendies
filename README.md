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
```tick_data/AAPL/2017-01-01/2017-01-30``` <br>
