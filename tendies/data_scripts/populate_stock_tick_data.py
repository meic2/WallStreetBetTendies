import collections
import datetime
import json
import psycopg2
import requests
import time
import urllib


def load_av_credentials():
    with open('data_scripts/av_credentials.json') as f:
        av_credentials = json.load(f)
        av_api_key = av_credentials['api_key']
    return av_api_key


# TODO: Add error handling here in case of incorrect or missing stock symbol
def load_tick_data(stock_symbols):
    av_api_key = load_av_credentials()
    symbols_tick_data = {}

    for symbol in stock_symbols:
        print('Symbol: ', symbol)
        symbol_params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'full',
            'apikey': av_api_key
        }
        stock_data = requests.get('https://www.alphavantage.co/query?{}'.format(urllib.parse.urlencode(symbol_params))).json()
        keys = stock_data.keys()
        if 'Time Series (Daily)' not in keys:
            print(stock_data)
        else:
            print(keys)
        symbol_tick_data = stock_data['Time Series (Daily)']
        symbols_tick_data[symbol] = symbol_tick_data

    return symbols_tick_data


def upload_to_db(stock_tick_data):
    conn = psycopg2.connect(
        host="fa19-cs411-048.cs.illinois.edu",
        database="wsb_tendies",
        user="wsb_django_user",
        password="411_wsb_tendies"
    )
    cur = conn.cursor()

    for stock in stock_tick_data:
        tick_data = stock_tick_data[stock]

        for timestamp in tick_data:
            date = datetime.datetime.strptime(timestamp, '%Y-%m-%d')
            prices = tick_data[timestamp]
            open_price = float(prices['1. open'])
            high_price = float(prices['2. high'])
            low_price = float(prices['3. low'])
            close_price = float(prices['4. close'])
            volume = int(prices['5. volume'])

            update_stock_tick_data_query = (
                'UPDATE StockTickData SET low_price={}, high_price={}, open_price={}, close_price={}, volume={} WHERE ts=\'{}\' AND stock_symbol=\'{}\''.format(
                    low_price, high_price, open_price, close_price, volume, date, stock
                )
            )
            insert_stock_tick_data_query = (
                'INSERT INTO StockTickData '
                '(ts, stock_symbol, low_price, high_price, open_price, close_price, volume) '
                'SELECT \'{}\', \'{}\', {}, {}, {}, {}, {} WHERE NOT EXISTS (SELECT 1 FROM StockTickData WHERE ts = \'{}\' AND stock_symbol = \'{}\')'.format(
                    date, stock, low_price, high_price, open_price, close_price, volume, date, stock
                )
            )

            cur.execute(update_stock_tick_data_query)
            cur.execute(insert_stock_tick_data_query)
            conn.commit()

    cur.close()

tech_stocks = [
    'AAPL', 'GOOG', 'FB', 'MSFT', 'AMZN', 'TSLA', 'NFLX', 'AMD', 
    'CSCO', 'TWTR', 'SNAP', 'CRM', 'NVDA'
]
media_stocks = ['DIS', 'ROKU', 'CMCSA', 'T']
retail_stocks = ['TGT', 'COST', 'WMT']
industrial_stocks = ['BA', 'SPCE', 'EADSY', 'CAT']
oil_stocks = ['CHK', 'WPX', 'XOM', 'CVX', 'WTI']
other_stocks = ['SPY', 'SPX']
all_stocks = tech_stocks + media_stocks + retail_stocks + industrial_stocks + oil_stocks + other_stocks

all_tick_data_uploaded = False
start_idx = 0
while not all_tick_data_uploaded:
    if start_idx + 5 < len(all_stocks):
        end_idx = start_idx + 5
    else:
        end_idx = len(all_stocks)
        all_tick_data_uploaded = True
    end_idx = start_idx + 5 if start_idx + 5 <= len(all_stocks) else len(all_stocks)
    stocks = all_stocks[start_idx:end_idx]
    tick_data = load_tick_data(stocks)
    stock_idx += 5
    time.sleep(60)  # Done because AlphaVantage API only allows 5 requests per minute

try:
    upload_to_db(tech_stock_tick_data)
except (Exception, psycopg2.DatabaseError) as error:
    print('ERROR with uploading tick data: ', error)
