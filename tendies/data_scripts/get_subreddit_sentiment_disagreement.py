import collections
import datetime
import json
import psycopg2
import requests
from string import printable
import urllib


def get_subreddit_sentiment_disagreement_res(query_filename, subreddit_name, subreddit_name_2, start_date, end_date):
    conn = psycopg2.connect(
        host="fa19-cs411-048.cs.illinois.edu",
        database="wsb_tendies",
        user="wsb_django_user",
        password="411_wsb_tendies")
    cur = conn.cursor()

    with open(query_filename, 'r') as q:
        subreddit_sentiment_disagreement_query = q.read().format(
            subreddit_name_2, start_date, end_date, subreddit_name, start_date, end_date
        ).strip()
        # subreddit_sentiment_disagreement_query = """select wsb.p_month, wsb.p_sentiment, wsb.c_sentiment, allOther.p_sentiment, allOther.c_sentiment from (select TO_CHAR(p.post_date,'Mon') as p_month, avg(p.sentiment_score) as p_sentiment, avg(c.sentiment_score) as c_sentiment from Post p join Comment c on p.post_id = c.post_id where p.subreddit_name in ('investing','stocks','StockMarket','economy') and p.post_date::DATE >= DATE '2018-12-01' and p.post_date::DATE < DATE '2019-12-01' group by p_month) as allOther, (select TO_CHAR(p.post_date,'Mon') as p_month, avg(p.sentiment_score) as p_sentiment, avg(c.sentiment_score) as c_sentiment from Post p join Comment c on p.post_id = c.post_id where p.subreddit_name='wallstreetbets' and p.post_date::DATE >= DATE '2018-12-01' and p.post_date::DATE < DATE '2019-12-01' group by p_month) as wsb where allOther.p_month = wsb.p_month and (wsb.p_sentiment > 0.0 and allOther.p_sentiment < 0.0) or (wsb.c_sentiment > 0.0 and allOther.p_sentiment < 0.0);"""
        print('Query to retrieve subreddit sentiment disagreement: ', subreddit_sentiment_disagreement_query)

        cur.execute(subreddit_sentiment_disagreement_query)
        conn.commit()

        final_res = []
        res = cur.fetchall()
        print('Results: ', res)
        for row in res:
            row_dict = {}
            row_dict['p_month'] = row[0]
            row_dict['p_sentiment'] = row[1]
            row_dict['c_sentiment'] = row[2]
            row_dict['other_p_sentiment'] = row[3]
            row_dict['other_c_sentiment'] = row[4]
            final_res.append(row_dict)

        cur.close()

    return final_res
