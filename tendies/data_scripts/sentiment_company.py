import collections
import datetime
import json
import pymongo
import psycopg2
import requests


def get_sentiment_count_res(company_name, subreddit):
    conn = psycopg2.connect(
        host="fa19-cs411-048.cs.illinois.edu",
        database="wsb_tendies",
        user="wsb_django_user",
        password="411_wsb_tendies"
    )
    cur = conn.cursor()

    client = pymongo.MongoClient("mongodb://localhost:27017")
    wsb_mongo_db = client['wsb_tendies']
    post_keywords_collection = wsb_mongo_db['post_keywords']
    # comment_keywords_collection = wsb_mongo_db['comment_keywords']

    try:
        company_ticker = requests.get('https://s.yimg.com/aq/autoc?query={}&region=US&lang=en-US'.format(company_name)).json()['ResultSet']['Result'][0]['symbol'].lower()
        print('company ticker: ', company_ticker)
    except:
        print('Company ticker not found')
        company_ticker = ''
    query = [
        {"$project": {"data": {"$objectToArray":"$keywords"}, "post_id": 1}},
        {"$unwind": "$data"},
        {"$match": {"$or": [{"data.k": '{}'.format(company_name)}, {"data.k": '{}'.format(company_ticker)}]}},
        {"$project": {"post_id": 1, "_id":0}}
    ]

    document = post_keywords_collection.aggregate(query)
    positive_post = 0
    negative_post = 0
    upvote = 0
    number_post = 0
    dict_vote = {'positive_post': 0, 'negative_post': 0, 'average_upvote_wsb': 0,}

    for post in document: 
        number_post+=1
        post_id = post['post_id'] 
        try:
            cur.execute(
                'SELECT sentiment_score, num_upvotes, subreddit_name FROM post WHERE post_id = \'{}\''.format(post_id)
            )
            rows = cur.fetchall()
            for row in rows:
                if row[2] != subreddit:
                    break
                sentiment_score = float(row[0])
                upvote += int(row[1])
                if sentiment_score > 0 : positive_post += 1
                elif sentiment_score < 0: negative_post += 1

        except (Exception, psycopg2.DatabaseError) as error:
                print('ERROR with finding the postid: {}'.format(str(error)))
                raise Exception(error)

    if number_post > 0:
        average_upvote = upvote / number_post
    else:
        average_upvote = 0
    dict_vote = {'positive_post': positive_post, 'negative_post': negative_post, 'average_upvote': average_upvote}
    return dict_vote