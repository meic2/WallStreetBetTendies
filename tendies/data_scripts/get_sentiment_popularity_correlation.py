import collections
import datetime
import json
import psycopg2
import requests
from string import printable
import urllib


def get_sentiment_popularity_correlation_res(query_filename, subreddit_name):
    conn = psycopg2.connect(
        host="fa19-cs411-048.cs.illinois.edu",
        database="wsb_tendies",
        user="wsb_django_user",
        password="411_wsb_tendies"
    )
    cur = conn.cursor()

    with open(query_filename, 'r') as q:
        sentiment_popularity_query = q.read().format(subreddit_name).strip()
        print('Query to retrieve sentiment popularity correlation: ', sentiment_popularity_query)

        cur.execute(sentiment_popularity_query)
        conn.commit()

        final_res = []
        res = cur.fetchall()
        print('Results: ', res)
        for row in res:
            row_dict = {}
            row_dict['p_month'] = row[0]
            row_dict['p_upvotes'] = row[1]
            row_dict['p_sent'] = row[2]
            row_dict['t_comments'] = int(row[3])
            final_res.append(row_dict)

        cur.close()

    return final_res
