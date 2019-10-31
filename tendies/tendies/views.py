import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import psycopg2

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
        'AND ts::DATE >= DATE \'{}\' AND ts <= DATE \'{}\''.format(
            stock_symbol, start_date, end_date
        )
    )

    print(get_stock_tick_data_query)

    cur.execute(get_stock_tick_data_query)
    conn.commit()

    for close_price in cur:
        print(close_price)

    cur.close()

    return JsonResponse({})