import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import psycopg2

# from ..data_scripts.populate_stock_tick_data import load_tick_data, upload_to_db

from data_scripts.populate_stock_tick_data import load_tick_data, upload_to_db
from data_scripts.delete_tick_data import delete_stock_tick_from_db

def get_stock_tick_data(request, stock_symbol, start_date, end_date):
    print('Stock symbol: ', stock_symbol)
    print('Start date: ', start_date)
    print('End date: ', end_date)

    # start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    # end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    conn = psycopg2.connect(
        host="fa19-cs411-048.cs.illinois.edu",
        database="wsb_tendies",
        user="wsb_django_user",
        password="411_wsb_tendies")
    cur = conn.cursor()

    get_stock_tick_data_query = (
        'SELECT ts, close_price FROM StockTickData WHERE stock_symbol = \'{}\''
        'AND ts::DATE >= DATE \'{}\' AND ts <= DATE \'{}\''
        'ORDER BY ts ASC'.format(stock_symbol, start_date, end_date)
    )

    print(get_stock_tick_data_query)

    closing_prices = {stock_symbol: []}

    cur.execute(get_stock_tick_data_query)
    conn.commit()

    for ts, close_price in cur:
        price_at_time = {'date': ts, 'close_price': close_price}
        closing_prices[stock_symbol].append(price_at_time)
        # print(close_price)

    cur.close()

    print(closing_prices)

    return JsonResponse(closing_prices)


def delete_stock_tick_data(request, stock_symbol, start_date, end_date):
    try:
        delete_stock_tick_from_db(stock_symbol, start_date, end_date)
        return JsonResponse({'status': 200})
    except (Exception, psycopg2.DatabaseError) as error:
        print('ERROR with deleting tick data: {}'.format(error))
        return JsonResponse({'status': 404, 'error': str(error)})


def insert_stock_tick_data(request, stock_symbol):
    try:
        tick_data = load_tick_data([stock_symbol])
        upload_to_db(tick_data)
        return JsonResponse({'status': 200})
    except (Exception, psycopg2.DatabaseError) as error:
        print('ERROR with uploading tick data: ', error)
        return JsonResponse({'status': 404, 'error': str(error)})