import collections
import datetime
import json
import psycopg2
import requests
import urllib


def get_tick_data_from_db(stock_symbol, start_date, end_date):
    conn = psycopg2.connect(
        host="fa19-cs411-048.cs.illinois.edu",
        database="wsb_tendies",
        user="wsb_django_user",
        password="411_wsb_tendies")
    cur = conn.cursor()

    get_stock_tick_data_query = (
        'SELECT ts, close_price FROM StockTickData WHERE stock_symbol = \'{}\''
        ' AND ts::DATE >= DATE \'{}\' AND ts <= DATE \'{}\''
        ' ORDER BY ts ASC'.format(stock_symbol, start_date, end_date)
    )

    print('Query to retrieve tick data: ', get_stock_tick_data_query)

    closing_prices = {stock_symbol: []}

    cur.execute(get_stock_tick_data_query)
    conn.commit()

    for ts, close_price in cur:
        price_at_time = {'date': ts, 'close_price': close_price}
        closing_prices[stock_symbol].append(price_at_time)

    cur.close()

    return closing_prices
