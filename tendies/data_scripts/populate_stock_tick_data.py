import collections
import datetime
import json
import psycopg2
import requests
import urllib


def load_av_credentials():
    with open('data_scripts/av_credentials.json') as f:
        av_credentials = json.load(f)
        av_api_key = av_credentials['api_key']
    return av_api_key


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

            insert_stock_tick_data_query = (
                'INSERT INTO StockTickData '
                '(ts, stock_symbol, low_price, high_price, open_price, close_price, volume) '
                'VALUES (\'{}\',\'{}\',{},{},{},{},{})'.format(
                    date, stock, open_price, high_price, low_price, close_price, volume
                )
            )  # TODO: Add fucntionality to ignore duplicates (UPSERT)!

            cur.execute(insert_stock_tick_data_query)
            conn.commit()

    cur.close()

'''
# NOTE: Can only make 5 requests for stock tick data per minute
tech_stock_tick_data = load_tick_data(['AAPL', 'GOOG', 'FB', 'MSFT', 'AMZN'])
# tech_stock_tick_data = load_tick_data(['FB', 'AMZN'])
try:
    upload_to_db(tech_stock_tick_data)
except (Exception, psycopg2.DatabaseError) as error:
    print('ERROR with uploading tick data: ', error)
'''
