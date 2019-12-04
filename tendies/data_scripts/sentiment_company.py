import collections
import datetime
import json
import pymongo
import psycopg2
import requests
from string import printable
import urllib


def get_sentiment_count(company_name):
    conn = psycopg2.connect(
    host="fa19-cs411-048.cs.illinois.edu",
    database="wsb_tendies",
    user="wsb_django_user",
    password="411_wsb_tendies")
    cur = conn.cursor()

    client = pymongo.MongoClient("mongodb://localhost:27018")
    wsb_mongo_db = client['wsb_tendies']
    post_keywords_collection = wsb_mongo_db['post_keywords']
    # comment_keywords_collection = wsb_mongo_db['comment_keywords']

    query = [
        {"$project": {"data": {"$objectToArray":"$keywords"}, "post_id": 1}},
        {"$unwind": "$data"},
        {"$match": {"data.k": '{}'.format(company_name)}},
        {"$project": {"post_id": 1, "_id":0}}
        ]

    document = post_keywords_collection.aggregate(query)
    print("connect to db")
    positive_post = 0
    negative_post = 0
    upvote = 0
    number_post = 0
    for post in document: 
        number_post+=1
        post_id = post['post_id']   
        try:
            cur.execute(
                'SELECT sentiment_score, num_upvotes FROM post WHERE post_id = \'{}\''.format(post_id)
            )
            rows = cur.fetchall()
            for row in rows:
                print (row)
                sentiment_score = float(row[0])
                upvote += int(row[1])
                if sentiment_score > 0 : positive_post += 1
                elif sentiment_score < 0: negative_post += 1

        except (Exception, psycopg2.DatabaseError) as error:
                print('ERROR with finding the postid: {}'.format(str(error)))
                raise Exception(error)
    average_upvote = upvote/number_post
    dict_vote = {'positive_post': positive_post, 'negative_post': negative_post, 'average_upvote': average_upvote}
    print(dict_vote)
    return dict_vote


get_sentiment_count('tesla')
